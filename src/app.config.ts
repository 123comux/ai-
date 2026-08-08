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
    'pages/learningRecord/index',
    'pages/goals/index',
    'pages/favorites/index',
    'pages/settings/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: '智学 AI',
    navigationBarTextStyle: 'black'
  },
  tabBar: {
    color: '#86909c',
    selectedColor: '#165dff',
    backgroundColor: '#ffffff',
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
