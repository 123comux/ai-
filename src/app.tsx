import { useLaunch, useDidShow, useDidHide } from '@tarojs/taro';
import { View } from '@tarojs/components';
import { useUserStore } from '@/store/useUserStore';
import { useAccessStore } from '@/store/useAccessStore';
// 全局样式
import './app.scss';

function App(props) {
  const restore = useUserStore((s) => s.restore);
  const login = useUserStore((s) => s.login);

  // 启动即恢复登录态；未登录则自动登录（建立真实用户，支撑多用户数据隔离）。
  // 用 useLaunch（App.onLaunch）而非 useEffect：微信小程序端 App 组件的 useEffect 不被可靠触发，
  // 会导致 useAccessStore.init() 从不执行、弹窗永不出现（H5 正常、微信端不弹的根因）。
  useLaunch(() => {
    // 冷启动：先立即弹「功能使用说明」弹窗（内部先置 visible 再拉数据，用兜底图文即时渲染），
    // 不等登录完成——登录/网络较慢时弹窗也能第一时间出现。
    useAccessStore.getState().init();
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
      // 登录态就绪后静默刷新试用/解锁状态，更新弹窗状态章颜色（不重复弹窗）
      useAccessStore.getState().refresh();
    })();
  });

  // 对应 onShow：每次回到前台静默刷新解锁状态（缴押金返回后锁定遮罩即时消失；不重复弹窗）
  useDidShow(() => {
    useAccessStore.getState().refresh();
  });

  // 对应 onHide
  useDidHide(() => {});

  // 注意：微信小程序 App 组件必须返回**单根**节点（不能返回 Fragment 多根），
  // 否则渲染帧异常导致整页白屏 / getCurrentInstanceFrame 超时。
  // 注意：导语弹窗 / 锁定遮罩（<AccessGate>）不在此渲染——微信端 App 组件里的内容
  // 是所有页面之下的容器，position:fixed 元素被页面层盖住无法显示，故改由首页渲染。
  return (
    <View className="app-root">
      {props.children}
    </View>
  );
}

export default App;
