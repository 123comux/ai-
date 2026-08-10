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
        await login();
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
