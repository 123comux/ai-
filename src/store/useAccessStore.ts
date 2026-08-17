/**
 * 功能使用权限状态（5 天免费试用 → 缴纳押金解锁）。
 *
 * 作用：
 * - 冷启动拉取导语配置 + 试用状态，弹「功能使用说明」弹窗（仅冷启动一次）。
 * - 运行中收到任意接口 403 access_denied → 置 locked，全屏锁定遮罩接管。
 * - 缴纳押金/退费状态变化后 refresh() 静默刷新，解锁遮罩即时消失。
 *
 * 安全边界：锁只是前端 UX，真正拦截在服务端中间件。这里所有网络失败一律 fail-open
 * （保持现状、不误锁），避免网络异常把用户锁在家里；服务端始终强校验。
 */
import { create } from 'zustand';
import Taro from '@tarojs/taro';
import { fetchAccessIntro, fetchAccessStatus } from '@/services/api';
import type { AccessConfig, AccessStatus } from '@/types/index';

/** 把剩余秒数格式化为友好文案：≥1 天显示"X 天"，否则"约 X 小时"。 */
export function formatTrialRemaining(seconds: number): string {
  if (seconds >= 86400) return `${Math.ceil(seconds / 86400)} 天`;
  const hours = Math.max(1, Math.ceil(seconds / 3600));
  return `约 ${hours} 小时`;
}

interface AccessState {
  status: AccessStatus | null;
  config: AccessConfig | null;
  /** 冷启动「功能使用说明」弹窗是否可见（仅冷启动一次，确认后关闭） */
  introVisible: boolean;
  /** 是否锁定（试用到期且未缴押金）；服务端 403 或拉取到的 status 裁决 */
  locked: boolean;
  /** 是否处于「解锁通道页」（押金页）：该页允许正常操作，锁定遮罩自动隐藏 */
  onUnlockPage: boolean;
  checking: boolean;
  /** 冷启动：并行拉取导语配置 + 状态 → 总是弹弹窗（配置/状态失败有兜底文案） */
  init: () => Promise<void>;
  /** 点「我已了解」：关弹窗；若即将到期发一次友好提醒；锁定则遮罩接管 */
  confirmIntro: () => void;
  /** 静默刷新解锁状态（前台切换/缴押金后调），不弹弹窗、不误锁 */
  refresh: () => Promise<void>;
  /** 运行期任意接口 403 access_denied → 立即锁定，遮罩接管 */
  handleAccessDenied: (state: AccessStatus) => void;
  /** 标记是否处于押金缴纳页（由 deposit 页生命周期维护，用于隐藏锁定遮罩） */
  setOnUnlockPage: (v: boolean) => void;
}

export const useAccessStore = create<AccessState>((set, get) => ({
  status: null,
  config: null,
  introVisible: false,
  locked: false,
  onUnlockPage: false,
  checking: false,

  init: async () => {
    set({ checking: true });
    let config: AccessConfig | null = null;
    let status: AccessStatus | null = null;
    try {
      config = await fetchAccessIntro();
    } catch {
      /* 导语配置失败：组件用兜底文案（5 天 / ¥199），不影响弹窗 */
    }
    try {
      status = await fetchAccessStatus();
    } catch {
      /* 状态失败（未登录/网络）：fail-open，不误锁 */
    }
    set({
      config,
      status,
      locked: status ? !status.access_granted : false,
      checking: false,
      introVisible: true,
    });
  },

  confirmIntro: () => {
    set({ introVisible: false });
    const s = get().status;
    if (s?.warn_expiring) {
      Taro.showToast({
        title: `试用期还剩 ${formatTrialRemaining(s.trial_remaining_seconds)}，请及时缴纳押金，到期未缴将暂停使用`,
        icon: 'none',
        duration: 3000,
      });
    }
    // locked 时 introVisible=false 由 <AccessGate> 的锁定遮罩接管
  },

  refresh: async () => {
    if (get().introVisible) return; // 弹窗展示中不打扰
    try {
      const status = await fetchAccessStatus();
      set({ status, locked: !status.access_granted });
    } catch {
      /* 网络失败：保持现状，绝不误锁 */
    }
  },

  handleAccessDenied: (state) => {
    set((s) => ({
      status: state ? { ...s.status, ...state } : s.status,
      locked: true,
    }));
  },

  setOnUnlockPage: (v) => set({ onUnlockPage: v }),
}));