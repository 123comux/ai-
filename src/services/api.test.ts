import { describe, it, expect, vi } from 'vitest';

vi.mock('@tarojs/taro', () => ({
  default: {
    getStorageSync: vi.fn(() => ''),
    request: vi.fn(),
  },
}));

// 纯工具函数（不发起网络，仅 URL 归一化/头像上传判定）
import { resolveAssetUrl, needsAvatarUpload } from './api';

describe('resolveAssetUrl', () => {
  it('绝对 http/https/data 原样返回', () => {
    expect(resolveAssetUrl('https://a.com/x.png')).toBe('https://a.com/x.png');
    expect(resolveAssetUrl('http://a.com/x.png')).toBe('http://a.com/x.png');
    expect(resolveAssetUrl('data:image/png;base64,abc')).toBe('data:image/png;base64,abc');
  });

  it('相对 /static 路径拼接为完整后端地址', () => {
    const url = resolveAssetUrl('/static/covers/1.png');
    expect(url.startsWith('http')).toBe(true);
    expect(url).toContain('/static/covers/1.png');
  });

  it('空值返回空串', () => {
    expect(resolveAssetUrl('')).toBe('');
    expect(resolveAssetUrl(null)).toBe('');
    expect(resolveAssetUrl(undefined)).toBe('');
  });
});

describe('needsAvatarUpload', () => {
  it('后端自有 avatar 地址视为已持久化，无需上传', () => {
    expect(needsAvatarUpload('/static/avatars/x.png')).toBe(false);
    expect(needsAvatarUpload('https://api.example.com/static/avatars/x.png')).toBe(false);
  });

  it('微信临时头像（wxfile/http tmp）需要上传', () => {
    expect(needsAvatarUpload('wxfile://tmp/x')).toBe(true);
    expect(needsAvatarUpload('http://tmp/xxxx.jpeg')).toBe(true);
    expect(needsAvatarUpload('http://tmp/abc')).toBe(true);
  });

  it('空白/空值无需上传', () => {
    expect(needsAvatarUpload('')).toBe(false);
    expect(needsAvatarUpload(null)).toBe(false);
    expect(needsAvatarUpload(undefined)).toBe(false);
  });
});
