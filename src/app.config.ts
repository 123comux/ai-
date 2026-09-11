export default defineAppConfig({
  pages: [
    'pages/home/index',
    'pages/learn/index',
    'pages/project/index',
    'pages/mine/index',
    'pages/assessment/index',
    'pages/courseDetail/index',
    'pages/chapterDetail/index',
    'pages/learningPath/index',
    'pages/projectDetail/index',
    'pages/jobMatching/index',
    'pages/tutor/index',
    'pages/video/index',
    'pages/webview/index',
    'pages/portfolio/index',
    'pages/goals/index',
    'pages/favorites/index',
    'pages/settings/index',
    'pages/deposit/index',
    'pages/community/index',
    'pages/communityPost/index',
    'pages/learningTool/index'
  ],
  window: {
    backgroundTextStyle: 'dark',
    navigationBarBackgroundColor: '#08090a',
    navigationBarTitleText: '智学 AI',
    navigationBarTextStyle: 'white'
  },
  // 暗色 tab 栏：颜色与 src/styles/theme.scss 的 $surface-1 / $ink-subtle / $color-primary-light 对齐。
  // 图标仍是 assets/tabbar/*.png（H5 侧用 CSS 滤镜提亮，见 src/app.scss）。
  tabBar: {
    color: '#62666d',
    selectedColor: '#7c88e8',
    backgroundColor: '#0f1011',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/home/index',
        text: '首页',
        iconPath: 'assets/tabbar/home.png',
        selectedIconPath: 'assets/tabbar/home-selected.png'
      },
      {
        pagePath: 'pages/learn/index',
        text: '学习',
        iconPath: 'assets/tabbar/learn.png',
        selectedIconPath: 'assets/tabbar/learn-selected.png'
      },
      {
        pagePath: 'pages/project/index',
        text: '项目',
        iconPath: 'assets/tabbar/project.png',
        selectedIconPath: 'assets/tabbar/project-selected.png'
      },
      {
        pagePath: 'pages/mine/index',
        text: '我的',
        iconPath: 'assets/tabbar/mine.png',
        selectedIconPath: 'assets/tabbar/mine-selected.png'
      }
    ]
  }
})
