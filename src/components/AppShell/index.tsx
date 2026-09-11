/**
 * AppShell（小程序端 / 默认实现）
 *
 * 多端隔离方式：H5 使用同目录的 index.h5.tsx（桌面侧边栏 + 顶栏外壳），
 * 本文件是其余端（微信小程序等）的实现——只做一层透明包裹，保持 App 组件“单根节点”，
 * 不引入任何浏览器 API、svg 图标或 hash 监听。
 *
 * 为什么不用条件编译注释：实测在 .tsx 中不会被剥离，H5-only 代码会进入小程序包
 * （运行时碰到 window 直接报错），故改用文件级多端后缀 .h5.tsx。
 */
import { View } from '@tarojs/components';

export default function AppShell({ children }: { children?: React.ReactNode }) {
  return <View className="app-shell-plain">{children}</View>;
}