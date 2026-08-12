import { useEffect } from 'react';
import { useDidShow, useDidHide } from '@tarojs/taro';
// 全局样式
import './app.scss';
import { useUserStore } from '@/store/useUserStore';

function App(props) {
  const restore = useUserStore((s) => s.restore);
  const login = useUserStore((s) => s.login);

  // 启动即恢复登录态；未登录则自动登录（建立真实用户，支撑多用户数据隔离）
  useEffect(() => {
    (async () => {
      await restore();
      if (!useUserStore.getState().isLoggedIn) {
        try {
          await login();
        } catch (err) {
          // 非小程序环境或登录失败：保持未登录态，不打断启动（个人中心页可手动触发登录）
          console.warn('[App] auto login skipped:', err);
        }
      }
    })();
  }, []);

  // 对应 onShow
  useDidShow(() => {});

  // 对应 onHide
  useDidHide(() => {});

  return props.children;
}

export default App;
