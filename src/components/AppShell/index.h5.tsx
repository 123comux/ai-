/**
 * AppShell：网页端外壳（桌面侧边栏 + 顶栏 + 内容容器）
 *
 * 设计约束：
 * 1. 文件级多端隔离：本文件仅 H5 使用（Taro 多端文件后缀 .h5.tsx），小程序端用同目录 index.tsx。
 *    避免 svg/hash 监听等 H5-only 能力进入小程序包。
 * 2. 移动端（< 1024PX）外壳 `display: contents` 不参与布局，保留 Taro 原生底部 tab；
 *    桌面端切换为 grid（侧边栏 + 内容），并隐藏 .weui-tabbar。
 * 3. 当前路由靠 hashchange 监听（H5 是 hash 路由）；App 组件不会随页面切换重渲染，
 *    因此不能用 useRouter。
 */
import { useEffect, useState } from 'react';
import { View, Text, Image } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useUserStore } from '@/store/useUserStore';
import { Button } from '@/components/ui';
import styles from './index.module.scss';


type NavItem = { path: string; label: string; icon: string; tab?: boolean };

const PAGE_TITLE: Record<string, string> = {
  '/pages/home/index': '首页',
  '/pages/learn/index': '学习',
  '/pages/project/index': '实战项目',
  '/pages/mine/index': '我的',
  '/pages/assessment/index': '能力测评',
  '/pages/courseDetail/index': '课程详情',
  '/pages/chapterDetail/index': '章节内容',
  '/pages/learningPath/index': '学习路径',
  '/pages/projectDetail/index': '项目详情',
  '/pages/jobMatching/index': '岗位对标',
  '/pages/tutor/index': 'AI 导师',
  '/pages/video/index': '视频学习',
  '/pages/webview/index': '网页',
  '/pages/portfolio/index': '作品集',
  '/pages/goals/index': '学习目标',
  '/pages/favorites/index': '我的收藏',
  '/pages/settings/index': '设置',
  '/pages/deposit/index': '学习押金',
  '/pages/community/index': '学习社区',
  '/pages/communityPost/index': '帖子详情',
  '/pages/learningTool/index': '学习工具'
};

const PRIMARY: NavItem[] = [
  { path: '/pages/home/index', label: '首页', icon: 'home', tab: true },
  { path: '/pages/learn/index', label: '学习', icon: 'book', tab: true },
  { path: '/pages/project/index', label: '项目', icon: 'layers', tab: true },
  { path: '/pages/mine/index', label: '我的', icon: 'user', tab: true }
];

const SECONDARY: NavItem[] = [
  { path: '/pages/tutor/index', label: 'AI 导师', icon: 'spark' },
  { path: '/pages/assessment/index', label: '能力测评', icon: 'radar' },
  { path: '/pages/learningPath/index', label: '学习路径', icon: 'route' },
  { path: '/pages/community/index', label: '学习社区', icon: 'chat' },
  { path: '/pages/favorites/index', label: '我的收藏', icon: 'bookmark' },
  { path: '/pages/goals/index', label: '学习目标', icon: 'target' },
  { path: '/pages/portfolio/index', label: '作品集', icon: 'grid' },
  { path: '/pages/jobMatching/index', label: '岗位对标', icon: 'briefcase' },
  { path: '/pages/deposit/index', label: '学习押金', icon: 'shield' },
  { path: '/pages/settings/index', label: '设置', icon: 'settings' }
];

/** 统一的线性图标（24×24 网格、stroke 1.5、圆头圆角），仅 H5 使用 */
function Icon({ name }: { name: string }) {
  const common = {
    width: '20',
    height: '20',
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: '1.5',
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const
  };
  const paths: Record<string, JSX.Element> = {
    home: (
      <>
        <path d="M4 10.6 12 4l8 6.6" />
        <path d="M6 10v9.4h12V10" />
        <path d="M10.4 19.4v-4.6h3.2v4.6" />
      </>
    ),
    book: (
      <>
        <path d="M5 5.2A1.2 1.2 0 0 1 6.2 4H18v15.4H6.2A1.2 1.2 0 0 1 5 18.2z" />
        <path d="M9 4v15.4" />
      </>
    ),
    layers: (
      <>
        <path d="M12 4.4 20 9l-8 4.6L4 9z" />
        <path d="M4 13.4 12 18l8-4.6" />
      </>
    ),
    user: (
      <>
        <circle cx="12" cy="9" r="3.4" />
        <path d="M5.4 19.6c.9-3.3 3.5-4.9 6.6-4.9s5.7 1.6 6.6 4.9" />
      </>
    ),
    spark: (
      <>
        <path d="M12 4.2l1.7 4.4 4.4 1.7-4.4 1.7L12 16.4l-1.7-4.4L5.9 10.3l4.4-1.7z" />
        <path d="M18.4 16.2l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z" />
      </>
    ),
    radar: (
      <>
        <path d="M12 12 18 6.6" />
        <path d="M12 4.6a7.4 7.4 0 1 1-7.2 9.2" />
        <path d="M12 8.4a3.6 3.6 0 1 1-3.4 4.6" />
      </>
    ),
    route: (
      <>
        <circle cx="6.4" cy="6.4" r="2.4" />
        <circle cx="17.6" cy="17.6" r="2.4" />
        <path d="M8.8 6.4h6.4a2.4 2.4 0 0 1 2.4 2.4v6.4" />
      </>
    ),
    chat: (
      <>
        <path d="M5 6.4A2.4 2.4 0 0 1 7.4 4h9.2A2.4 2.4 0 0 1 19 6.4v6.2a2.4 2.4 0 0 1-2.4 2.4H10l-5 4z" />
      </>
    ),
    bookmark: (
      <>
        <path d="M7 4.6h10v15l-5-3.4-5 3.4z" />
      </>
    ),
    target: (
      <>
        <circle cx="12" cy="12" r="7.4" />
        <circle cx="12" cy="12" r="3.4" />
        <path d="M12 4.6V2.6M12 21.4v-2M4.6 12h-2M21.4 12h-2" />
      </>
    ),
    grid: (
      <>
        <rect x="4.4" y="4.4" width="6.2" height="6.2" rx="1.6" />
        <rect x="13.4" y="4.4" width="6.2" height="6.2" rx="1.6" />
        <rect x="4.4" y="13.4" width="6.2" height="6.2" rx="1.6" />
        <rect x="13.4" y="13.4" width="6.2" height="6.2" rx="1.6" />
      </>
    ),
    briefcase: (
      <>
        <rect x="4" y="8" width="16" height="11" rx="2" />
        <path d="M9.4 8V6.4A1.4 1.4 0 0 1 10.8 5h2.4a1.4 1.4 0 0 1 1.4 1.4V8" />
      </>
    ),
    shield: (
      <>
        <path d="M12 4.4 19 7v5.4c0 3.9-2.9 6.4-7 7.2-4.1-.8-7-3.3-7-7.2V7z" />
        <path d="M9.4 12.2l1.9 1.9 3.4-3.6" />
      </>
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="2.8" />
        <path d="M12 3.6v2.2M12 18.2v2.2M4.8 7.8l1.9 1.1M17.3 15.1l1.9 1.1M4.8 16.2l1.9-1.1M17.3 8.9l1.9-1.1" />
      </>
    )
  };
  return <svg {...common}>{paths[name] ?? paths.grid}</svg>;
}

function currentPath(): string {
  if (typeof window === 'undefined') return '';
  const hash = window.location.hash.replace(/^#/, '');
  const [path] = hash.split('?');
  return path || '/pages/home/index';
}


export default function AppShell({ children }: { children?: React.ReactNode }) {
  
  const [path, setPath] = useState<string>(() => currentPath());
  const isLoggedIn = useUserStore((s) => s.isLoggedIn);
  const nickname = useUserStore((s) => s.nickname);
  const avatar = useUserStore((s) => s.avatar);

  useEffect(() => {
    const onChange = () => setPath(currentPath());
    window.addEventListener('hashchange', onChange);
    window.addEventListener('popstate', onChange);
    return () => {
      window.removeEventListener('hashchange', onChange);
      window.removeEventListener('popstate', onChange);
    };
  }, []);

  const go = (item: NavItem) => {
    if (currentPath() === item.path) return;
    if (item.tab) Taro.switchTab({ url: item.path });
    else Taro.navigateTo({ url: item.path });
  };

  const renderNav = (item: NavItem) => {
    const active = path === item.path;
    return (
      <View
        key={item.path}
        className={`${styles.navItem} ${active ? styles.navItemActive : ''}`}
        onClick={() => go(item)}
        role="link"
        aria-current={active ? 'page' : undefined}
        tabIndex={0}
      >
        <View className={styles.navIcon}>
          <Icon name={item.icon} />
        </View>
        <Text className={styles.navLabel}>{item.label}</Text>
      </View>
    );
  };

  const title = PAGE_TITLE[path] ?? 'AI 学习平台';
  

  return (
    <View className={styles.shell}>
      {}
      <View className={styles.aside}>
        <View className={styles.brand} onClick={() => go(PRIMARY[0])}>
          <View className={styles.brandMark} />
          <Text className={styles.brandText}>智学 AI</Text>
        </View>
        <View className={styles.navGroup}>{PRIMARY.map(renderNav)}</View>
        <View className={styles.navDivider} />
        <View className={styles.navGroup}>{SECONDARY.map(renderNav)}</View>
        <View className={styles.asideFoot}>
          <View className={styles.userChip} onClick={() => go(PRIMARY[3])}>
            {avatar ? (
              <Image className={styles.avatar} src={avatar} mode="aspectFill" />
            ) : (
              <View className={styles.avatarFallback}>
                <Text>{(nickname || '游').slice(0, 1)}</Text>
              </View>
            )}
            <View className={styles.userMeta}>
              <Text className={styles.userName}>{isLoggedIn ? nickname || '学员' : '未登录'}</Text>
              <Text className={styles.userHint}>{isLoggedIn ? '查看我的学习' : '点此用手机号登录'}</Text>
            </View>
          </View>
        </View>
      </View>

      <View className={styles.main}>
        <View className={styles.topbar}>
          <Text className={styles.topbarTitle}>{title}</Text>
          <View className={styles.topbarActions}>
            <Button tone="ghost" size="sm" onClick={() => go(SECONDARY[0])}>
              问 AI 导师
            </Button>
            <Button size="sm" onClick={() => go(SECONDARY[1])}>
              开始能力测评
            </Button>
          </View>
        </View>
        <View className={styles.content}>{children}</View>
      </View>
      {}

      {/* 非 H5（小程序）：外壳全部剔除，直接渲染页面，保持原有单根结构 */}
      
    </View>
  );
}
