import { create } from 'zustand';
import Taro from '@tarojs/taro';
import { wechatLogin, h5PhoneLogin, fetchMe, updateProfile as updateProfileApi, devImpersonate } from '@/services/api';
import type { LoginResult } from '@/types/index';

const TOKEN_KEY = 'aishi_token';
// 旧版本地资料缓存 key（资料现以后端 users 表为准，此处仅退出时兜底清理历史数据）
const USER_INFO_KEY = 'user_info';
// 网页端登录过的手机号：用于冷启动静默恢复登录态（后端不校验验证码，可直接换 token）
const H5_PHONE_KEY = 'aishi_h5_phone';

const IS_WEAPP = process.env.TARO_ENV === 'weapp';

/** 登录成功后统一写入本地 token 并返回要合并进 store 的用户态（微信登录 / 网页端手机号登录共用） */
function persistLogin(data: LoginResult): Partial<UserState> {
  Taro.setStorageSync(TOKEN_KEY, data.token);
  return {
    isLoggedIn: true,
    token: data.token,
    userId: data.user.id,
    nickname: data.user.nickname,
    avatar: data.user.avatar,
    grade: data.user.grade ?? '',
    major: data.user.major ?? '',
    targetDirection: data.user.targetDirection ?? '',
  };
}

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
  /** 保证登录态：微信端走 wx.login；网页端用上次登录的手机号静默续登，未登录过则抛错引导去手动登录 */
  login: () => Promise<void>;
  /** 网页端手机号登录（H5 专用；成功后记住手机号，后续冷启动自动续登） */
  phoneLogin: (phone: string) => Promise<void>;
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
    // 网页端（H5）没有 wx.login：
    // - 之前登录过 → 用记住的手机号静默续登（token 过期后也能自动恢复）
    // - 从未登录过 → 抛错，由页面引导用户到「我的」页面用手机号登录
    if (!IS_WEAPP) {
      const savedPhone = Taro.getStorageSync(H5_PHONE_KEY);
      if (!savedPhone) {
        throw new Error('网页端请先在「我的」页面用手机号登录');
      }
      await get().phoneLogin(savedPhone);
      return;
    }

    // 小程序端：wx.login 拿真实 code（H5 无此能力）
    // code 一次性使用（可能被前一次登录消费掉），失败时重取一次重试
    let lastErr: any;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        const res = await Taro.login();
        const code = (res as any)?.code || '';
        if (!code) throw new Error('wx.login 未返回 code');
        // 2) 用 code 换 token + 用户（后端真实 code2session → openid）
        const data = await wechatLogin(code);
        set(persistLogin(data));
        // 3) 登录后请求订阅消息授权（模板未配置则静默跳过）
        try {
          const { requestSubscriptions } = await import('@/utils/subscribe');
          requestSubscriptions();
        } catch { /* 忽略订阅失败 */ }
        return;
      } catch (err) {
        lastErr = err;
      }
    }
    throw lastErr;
  },

  phoneLogin: async (phone: string) => {
    const trimmed = (phone || '').trim();
    if (!/^1[3-9]\d{9}$/.test(trimmed)) {
      throw new Error('请输入正确的 11 位手机号');
    }
    const data = await h5PhoneLogin(trimmed);
    Taro.setStorageSync(H5_PHONE_KEY, trimmed);
    set(persistLogin(data));
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
    set(persistLogin(data));
  },

  logout: () => {
    // 清空本地存储的用户信息（token + 本地资料缓存），恢复未登录初始态
    Taro.removeStorageSync(TOKEN_KEY);
    Taro.removeStorageSync(USER_INFO_KEY);
    // 网页端还要清掉记住的手机号：否则下次冷启动 login() 会用它静默自动登录，退出形同虚设
    Taro.removeStorageSync(H5_PHONE_KEY);
    set({
      isLoggedIn: false, token: '', userId: 0, nickname: '', avatar: '',
      grade: '', major: '', targetDirection: '',
    });
  },

  setUser: (info) => set((state) => ({ ...state, ...info })),
}));
