import type { UserConfigExport } from '@tarojs/cli';
export default {
  logger: {
    quiet: false,
    stats: true,
  },
  mini: {},
  h5: {
    devServer: {
      port: 10087,
      open: false,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  },
} satisfies UserConfigExport<'webpack5'>;
