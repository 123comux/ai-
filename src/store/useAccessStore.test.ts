import { describe, it, expect, vi } from 'vitest';

// mock Taro 与 api，避免拉起真实的小程序运行时 / 网络
vi.mock('@tarojs/taro', () => ({
  default: {
    getStorageSync: vi.fn(() => ''),
    request: vi.fn(),
    navigateTo: vi.fn(),
    showToast: vi.fn(),
    redirectTo: vi.fn(),
  },
}));

// 倒计时文案纯函数（不依赖 Taro）
import { formatTrialRemaining } from './useAccessStore';

describe('formatTrialRemaining', () => {
  it('≥1 天显示整天天数（向上取整）', () => {
    expect(formatTrialRemaining(86400)).toBe('1 天');
    expect(formatTrialRemaining(5 * 86400)).toBe('5 天');
  });

  it('不足 1 天显示小时（向上取整，至少 1 小时）', () => {
    expect(formatTrialRemaining(3600)).toBe('约 1 小时');
    expect(formatTrialRemaining(86399)).toBe('约 24 小时');
  });

  it('少于 1 小时时最少显示 约 1 小时，不出现 0/负数', () => {
    expect(formatTrialRemaining(1)).toBe('约 1 小时');
    expect(formatTrialRemaining(0)).toBe('约 1 小时');
    expect(formatTrialRemaining(-5)).toBe('约 1 小时');
  });
});
