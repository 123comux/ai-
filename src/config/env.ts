/**
 * 环境配置：API 服务地址等。
 *
 * 通过构建时注入 TARO_APP_API_BASE 覆盖（生产为已备案的 HTTPS 域名）：
 *   TARO_APP_API_BASE=https://api.your-domain.com npm run build:weapp
 *   TARO_APP_API_BASE=https://your-domain.com npm run build:h5
 *
 * H5 端未配置时的兜底策略：使用同源相对路径（API_BASE = ''），把请求交给 `/api` 反向代理——
 *   - 本地开发：config/dev.ts 已配置 devServer.proxy['/api'] → http://localhost:8010
 *   - 线上部署：deploy/nginx.conf 已配置 /api → backend:8010（同源）
 * 这样手机连同一 Wi-Fi、用局域网 IP 打开网页端（如 http://192.168.1.5:10087）也能正常请求后端。
 * 若写成 http://localhost:xxxx，手机上的 localhost 指向手机自身，接口必然全部失败，同时还会引入跨域。
 *
 * 小程序端没有同源概念，必须使用绝对地址，未配置时回退本机地址
 * （微信开发者工具勾选「不校验合法域名」即可联调）。
 *
 * 注意：H5 端 webpack5 默认不注入 Node 的 `process` 全局，直接引用
 * `process.env.TARO_APP_API_BASE` 会在浏览器运行时抛 `process is not defined`，
 * 因此这里做一次安全取值：process 缺失时回退。
 */
const __env: { env?: Record<string, string | undefined> } =
  typeof process !== 'undefined' ? process : {};

// process.env.TARO_ENV 由 Taro 在构建时静态替换为 'h5' / 'weapp'
const IS_H5 = process.env.TARO_ENV === 'h5';

/** 未显式配置 TARO_APP_API_BASE 时的兜底地址（端口与 backend/config.py 的默认 PORT 保持一致） */
const FALLBACK_API_BASE = IS_H5 ? '' : 'http://localhost:8010';

export const API_BASE: string = __env.env?.TARO_APP_API_BASE || FALLBACK_API_BASE;
