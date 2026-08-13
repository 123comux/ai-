/**
 * 环境配置：API 服务地址等。
 *
 * 通过构建时注入 TARO_APP_API_BASE 覆盖（生产为已备案的 HTTPS 域名）：
 *   TARO_APP_API_BASE=https://api.your-domain.com npm run build:weapp
 * 未配置时回退本地开发地址（小程序开发者工具勾选「不校验合法域名」可访问）。
 *
 * 注意：H5 端 webpack5 默认不注入 Node 的 `process` 全局，直接引用
 * `process.env.TARO_APP_API_BASE` 会在浏览器运行时抛 `process is not defined`，
 * 因此这里做一次安全取值：process 缺失时回退本地地址。
 */
const __env: { env?: Record<string, string | undefined> } =
  typeof process !== 'undefined' ? process : {};

export const API_BASE: string = __env.env?.TARO_APP_API_BASE || 'http://localhost:8000';
