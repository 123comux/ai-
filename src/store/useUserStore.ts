import { create } from 'zustand';

interface UserState {
  isLoggedIn: boolean;
  nickname: string;
  avatar: string;
  grade: string;
  major: string;
  targetDirection: string;
  setUser: (info: Partial<UserState>) => void;
  login: () => void;
  logout: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  isLoggedIn: true,
  nickname: 'AI 学习者',
  avatar: 'https://picsum.photos/id/64/200/200',
  grade: '大三',
  major: '计算机科学与技术',
  targetDirection: '大模型应用开发',
  setUser: (info) => set((state) => ({ ...state, ...info })),
  login: () => set({ isLoggedIn: true }),
  logout: () => set({ isLoggedIn: false }),
}));