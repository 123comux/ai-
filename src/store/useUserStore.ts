import { create } from 'zustand';
import Taro from '@tarojs/taro';
import { wechatLogin, fetchMe, updateProfile as updateProfileApi, devImpersonate } from '@/services/api';

const TOKEN_KEY = 'aishi_token';
// 旧版本地资料缓存 key（资料现以后端 users 表为准，此处仅退出时兜底清理历史数据）
const USER_INFO_KEY = 'user_info';

interface UserState {
  isLoggedIn: boolean;
  token: string;
  userId: number;
  nickname: string;
  avatar: string;
  // 学员自填资料（初始为空，后端 users 表为唯一数据源，登录/恢复时同步）
  grade: string;
  major: string;
  targetDirection: string;
  login: () => Promise<void>;
  /** 启动时恢复登录态（读本地 token 并校验） */
  restore: () => Promise<void>;
  /** 更新用户资料（昵称/头像/年级/专业/目标方向），未传的字段保留当前值 */
  updateProfile: (profile: {
    nickname?: string;
    avatar?: string;
    grade?: string;
    major?: string;
    targetDirection?: string;
  }) => Promise<void>;
  /** 开发期模拟切换：以指定后台用户身份登录（后端 DEV_IMPERSONATE=true 才可用） */
  impersonate: (userId: number) => Promise<void>;
  logout: () => void;
  setUser: (info: Partial<UserState>) => void;
}

export const useUserStore = create<UserState>((set, get) => ({
  isLoggedIn: false,
  token: '',
  userId: 0,
  nickname: '',
  avatar: '',
  // 初始无默认资料，避免"大三/计算机科学与技术"这类占位干扰客户选择
  grade: '',
  major: '',
  targetDirection: '',

  login: async () => {
    // 1) 仅在微信小程序环境走 wx.login 拿真实 code（H5 无此能力，直接报错，不再造 dev_ 假码）
    const isWeapp = process.env.TARO_ENV === 'weapp';
    if (!isWeapp) {
      throw new Error('非小程序环境，微信登录不可用');
    }
    // code 一次性使用（可能被前一次登录消费掉），失败时重取一次重试
    let lastErr: any;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const res = await Taro.login();
        const code = (res as any)?.code || '';
        if (!code) throw new Error('wx.login 未返回 code');
        // 2) 用 code 换 token + 用户（后端真实 code2session → openid）
        const data = await wechatLogin(code);
        Taro.setStorageSync(TOKEN_KEY, data.token);
        set({
          isLoggedIn: true,
          token: data.token,
          userId: data.user.id,
          nickname: data.user.nickname,
          avatar: data.user.avatar,
          grade: data.user.grade ?? '',
          major: data.user.major ?? '',
          targetDirection: data.user.targetDirection ?? '',
        });
        return;
      } catch (err) {
        lastErr = err;
      }
    }
    throw lastErr;
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
        grade: user.grade ?? '',
        major: user.major ?? '',
        targetDirection: user.targetDirection ?? '',
      });
    } catch {
      // token 失效则清除本地登录态与资料缓存，下次进入重新登录
      Taro.removeStorageSync(TOKEN_KEY);
      Taro.removeStorageSync(USER_INFO_KEY);
      set({ isLoggedIn: false, token: '', userId: 0, nickname: '', avatar: '' });
    }
  },

  updateProfile: async (profile) => {
    // 未传的字段保留当前值（例如只改昵称时不清掉已有头像/资料）
    const current = get();
    const next = {
      nickname: (profile.nickname ?? current.nickname).trim(),
      avatar: profile.avatar ?? current.avatar,
      grade: profile.grade ?? current.grade,
      major: profile.major ?? current.major,
      targetDirection: profile.targetDirection ?? current.targetDirection,
    };
    // 以后端返回为准回写本地态
    const user = await updateProfileApi(next);
    set({
      nickname: user.nickname,
      avatar: user.avatar,
      grade: user.grade ?? '',
      major: user.major ?? '',
      targetDirection: user.targetDirection ?? '',
    });
  },

  impersonate: async (userId: number) => {
    // 开发期模拟切换：换取目标用户 token 后写入本地，等同切换登录身份
    const data = await devImpersonate(userId);
    Taro.setStorageSync(TOKEN_KEY, data.token);
    set({
      isLoggedIn: true,
      token: data.token,
      userId: data.user.id,
      nickname: data.user.nickname,
      avatar: data.user.avatar,
      grade: data.user.grade ?? '',
      major: data.user.major ?? '',
      targetDirection: data.user.targetDirection ?? '',
    });
  },

  logout: () => {
    // 清空本地存储的用户信息（token + 本地资料缓存），恢复未登录初始态
    Taro.removeStorageSync(TOKEN_KEY);
    Taro.removeStorageSync(USER_INFO_KEY);
    set({
      isLoggedIn: false, token: '', userId: 0, nickname: '', avatar: '',
      grade: '', major: '', targetDirection: '',
    });
  },

  setUser: (info) => set((state) => ({ ...state, ...info })),
}));
