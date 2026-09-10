import type { UserConfigExport } from '@tarojs/cli';

// 本项目后端地址（H5 同源代理的转发目标），与 backend/config.py 的默认 PORT(8010) 保持一致。
// 换端口时只需改环境变量：
//   DEV_API_TARGET=http://localhost:8011 npm run dev:h5
const DEV_API_TARGET = process.env.DEV_API_TARGET || 'http://localhost:8010';

export default {
  logger: {
    quiet: false,
    stats: true,
  },
  mini: {},
  h5: {
    devServer: {
      // 绑定 0.0.0.0：手机连同一 Wi-Fi 用电脑局域网 IP 即可预览网页端
      // （http://<电脑IP>:10087），便于验证移动端自适应与功能。
      host: '0.0.0.0',
      port: 10087,
      open: false,
      // H5 端 API_BASE 未显式配置时为空串（同源相对路径），依赖此代理转发到后端，
      // 因此手机通过局域网 IP 访问也能正常打后端，且不产生跨域。
      proxy: {
        '/api': {
          target: DEV_API_TARGET,
          changeOrigin: true,
        },
        // 后端静态资源（头像/封面）同样走代理，保证手机端图片可加载
        '/static': {
          target: DEV_API_TARGET,
          changeOrigin: true,
        },
      },
    },
  },
} satisfies UserConfigExport<'webpack5'>;
