export default defineAppConfig({
  pages: [
    'pages/home/index',
    'pages/learn/index',
    'pages/project/index',
    'pages/mine/index',
    'pages/assessment/index',
    'pages/courseDetail/index',
    'pages/learningPath/index',
    'pages/projectDetail/index',
    'pages/jobMatching/index',
    'pages/tutor/index',
    'pages/video/index'
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
        iconPath: 'assets/tabbar/home.svg',
        selectedIconPath: 'assets/tabbar/home-selected.svg'
      },
      {
        pagePath: 'pages/learn/index',
        text: '学习',
        iconPath: 'assets/tabbar/learn.svg',
        selectedIconPath: 'assets/tabbar/learn-selected.svg'
      },
      {
        pagePath: 'pages/project/index',
        text: '项目',
        iconPath: 'assets/tabbar/project.svg',
        selectedIconPath: 'assets/tabbar/project-selected.svg'
      },
      {
        pagePath: 'pages/mine/index',
        text: '我的',
        iconPath: 'assets/tabbar/mine.svg',
        selectedIconPath: 'assets/tabbar/mine-selected.svg'
      }
    ]
  }
})
