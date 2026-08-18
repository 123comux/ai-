import { describe, it, expect, vi, beforeEach } from 'vitest';

// 直接以 vi.fn 作为模块 mock，测试内 import 到同一引用（vitest hoisted）
vi.mock('@tarojs/taro', () => ({
  default: { showToast: vi.fn(), navigateTo: vi.fn() },
}));
vi.mock('@/services/api', () => ({
  fetchAccessIntro: vi.fn(),
  fetchAccessStatus: vi.fn(),
}));

import { useAccessStore } from './useAccessStore';
import Taro from '@tarojs/taro';
import type { AccessConfig, AccessStatus } from '@/types/index';
import { fetchAccessIntro, fetchAccessStatus } from '@/services/api';

const intro = fetchAccessIntro as unknown as ReturnType<typeof vi.fn>;
const status = fetchAccessStatus as unknown as ReturnType<typeof vi.fn>;
const showToast = Taro.showToast as unknown as ReturnType<typeof vi.fn>;

describe('useAccessStore 状态机', () => {
  beforeEach(() => {
    useAccessStore.setState({
      status: null,
      config: null,
      introVisible: false,
      locked: false,
      onUnlockPage: false,
      checking: false,
    });
    vi.clearAllMocks();
    // 每个用例给默认 resolve，避免未 mock 时 reject 干扰
    intro.mockResolvedValue({ trial_days: 5, deposit_amount: 199 } as AccessConfig);
    status.mockResolvedValue({ access_granted: true, in_trial: true, trial_remaining_seconds: 86400 } as AccessStatus);
  });

  it('init 成功：弹窗出现，且只拉 intro（不拉 status，锁定交由 refresh 裁决）', async () => {
    await useAccessStore.getState().init();
    const s = useAccessStore.getState();
    expect(s.introVisible).toBe(true); // 冷启动即弹窗
    expect(intro).toHaveBeenCalledTimes(1);
    // init 不拉 status、不裁决锁定（避免冷启动误锁/401 噪音），保持除弹窗外 fail-open
    expect(status).not.toHaveBeenCalled();
    expect(s.locked).toBe(false);
    expect(s.checking).toBe(false);
  });

  it('init fail-open：intro/status 拉取失败时不误锁，且弹窗仍出现', async () => {
    intro.mockRejectedValue(new Error('network'));
    status.mockRejectedValue(new Error('network'));
    await useAccessStore.getState().init();
    const s = useAccessStore.getState();
    expect(s.introVisible).toBe(true); // 即使失败也弹窗（兜底文案）
    expect(s.locked).toBe(false);      // 绝不误锁
  });

  it('init 网络异常不会产生未捕获的 reject', async () => {
    intro.mockRejectedValue(new Error('boom'));
    status.mockRejectedValue(new Error('boom'));
    await expect(useAccessStore.getState().init()).resolves.toBeUndefined();
  });

  it('refresh：试用中(access_granted) → 不锁定', async () => {
    await useAccessStore.getState().refresh();
    expect(useAccessStore.getState().locked).toBe(false);
  });

  it('refresh：到期未缴 → 锁定', async () => {
    status.mockResolvedValue({ access_granted: false, in_trial: false, trial_remaining_seconds: 0 } as AccessStatus);
    await useAccessStore.getState().refresh();
    expect(useAccessStore.getState().locked).toBe(true);
  });

  it('refresh 网络失败保持现状（不误锁也不强行解锁）', async () => {
    useAccessStore.setState({ locked: true, status: { access_granted: false } as AccessStatus });
    status.mockRejectedValue(new Error('offline'));
    await useAccessStore.getState().refresh();
    expect(useAccessStore.getState().locked).toBe(true);
  });

  it('introVisible 展示中 refresh 不打扰（不发请求）', async () => {
    useAccessStore.setState({ introVisible: true });
    await useAccessStore.getState().refresh();
    expect(status).not.toHaveBeenCalled();
  });

  it('handleAccessDenied：运行期 403 → 立即锁定', () => {
    useAccessStore.getState().handleAccessDenied({ access_granted: false, in_trial: false, trial_remaining_seconds: 0 } as AccessStatus);
    expect(useAccessStore.getState().locked).toBe(true);
  });

  it('confirmIntro：关闭弹窗；即将到期时发友好 toast', () => {
    useAccessStore.setState({ introVisible: true, status: { warn_expiring: true, trial_remaining_seconds: 3600 } as AccessStatus });
    useAccessStore.getState().confirmIntro();
    expect(useAccessStore.getState().introVisible).toBe(false);
    expect(showToast).toHaveBeenCalled();
  });

  it('confirmIntro：非到期时不发 toast', () => {
    useAccessStore.setState({ introVisible: true, status: { warn_expiring: false } as AccessStatus });
    useAccessStore.getState().confirmIntro();
    expect(showToast).not.toHaveBeenCalled();
  });

  it('setOnUnlockPage：标记是否处于押金解锁通道页', () => {
    useAccessStore.getState().setOnUnlockPage(true);
    expect(useAccessStore.getState().onUnlockPage).toBe(true);
    useAccessStore.getState().setOnUnlockPage(false);
    expect(useAccessStore.getState().onUnlockPage).toBe(false);
  });
});
