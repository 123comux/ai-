/**
 * 环境配置：API 服务地址等。
 *
 * 通过构建时注入 TARO_APP_API_BASE 覆盖（生产为已备案的 HTTPS 域名）：
 *   TARO_APP_API_BASE=https://api.your-domain.com npm run build:weapp
 * 未配置时回退本地开发地址（小程序开发者工具勾选「不校验合法域名」可访问）。
 */
export const API_BASE: string = process.env.TARO_APP_API_BASE || 'http://localhost:8000';
