import { create } from 'zustand';
import Taro from '@tarojs/taro';
import { wechatLogin, fetchMe } from '@/services/api';

const TOKEN_KEY = 'aishi_token';

interface UserState {
  isLoggedIn: boolean;
  token: string;
  userId: number;
  nickname: string;
  avatar: string;
  // 兼容原有"我的"资料字段（本地态，未接入后端）
  grade: string;
  major: string;
  targetDirection: string;
  login: () => Promise<void>;
  /** 启动时恢复登录态（读本地 token 并校验） */
  restore: () => Promise<void>;
  logout: () => void;
  setUser: (info: Partial<UserState>) => void;
}

export const useUserStore = create<UserState>((set) => ({
  isLoggedIn: false,
  token: '',
  userId: 0,
  nickname: '',
  avatar: '',
  grade: '大三',
  major: '计算机科学与技术',
  targetDirection: '入门实践',

  login: async () => {
    try {
      let code = '';
      try {
        const res = await Taro.login();
        code = (res as any)?.code || `dev_${Date.now()}`;
      } catch {
        // H5 / dev 环境下 Taro.login 可能不可用，用本地 dev code 兜底（后端 DEV_MODE 接受）
        code = `dev_${Date.now()}`;
      }
      const data = await wechatLogin(code);
      Taro.setStorageSync(TOKEN_KEY, data.token);
      set({
        isLoggedIn: true,
        token: data.token,
        userId: data.user.id,
        nickname: data.user.nickname,
        avatar: data.user.avatar,
      });
    } catch (err) {
      console.error('[login] failed:', err);
      Taro.showToast({ title: '登录失败，请重试', icon: 'none' });
    }
  },

  restore: async () => {
    const token = Taro.getStorageSync(TOKEN_KEY);
    if (!token) return;
    try {
      const user = await fetchMe();
      set({
        isLoggedIn: true,
        token,
        userId: user.id,
        nickname: user.nickname,
        avatar: user.avatar,
      });
    } catch {
      // token 失效则清除，下次进入重新登录
      Taro.removeStorageSync(TOKEN_KEY);
      set({ isLoggedIn: false, token: '', userId: 0, nickname: '', avatar: '' });
    }
  },

  logout: () => {
    Taro.removeStorageSync(TOKEN_KEY);
    set({
      isLoggedIn: false, token: '', userId: 0, nickname: '', avatar: '',
      grade: '大三', major: '计算机科学与技术', targetDirection: '入门实践',
    });
  },

  setUser: (info) => set((state) => ({ ...state, ...info })),
}));
