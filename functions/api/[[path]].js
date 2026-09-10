/**
 * Cloudflare Pages Function：把 H5 页面发出的 /api/** 请求反向代理到真正的后端。
 *
 * 为什么需要它：
 *   - Cloudflare Pages 只能托管静态站点，跑不了我们的 Python/FastAPI 后端
 *     （Workers/Pages Functions 只支持 JS/WASM）。
 *   - H5 前端默认使用**同源相对路径** `/api/**`（见 src/config/env.ts 的 API_BASE = ''），
 *     所以只要在 pages.dev 这个域名下把 /api/** 转发到后端，浏览器全程同源，
 *     不需要 CORS，也不需要改前端代码。
 *
 * 目标后端通过环境变量 API_ORIGIN 配置（Pages 项目 → Settings → Environment variables）：
 *   API_ORIGIN = https://你的后端域名        # 默认值为下面这个 Vercel 生产地址
 *
 * 部署位置（仓库根目录，Pages 会自动识别）：
 *   functions/api/[[path]].js
 */

const DEFAULT_API_ORIGIN = 'https://ai-nine-inky.vercel.app';

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  const origin = String(env.API_ORIGIN || DEFAULT_API_ORIGIN).replace(/\/+$/, '');
  const target = origin + url.pathname + url.search;

  const headers = new Headers(request.headers);
  // Host 必须交给 fetch 按目标地址生成，否则后端会按 pages.dev 处理
  headers.delete('host');
  // 同源代理：去掉 Origin，后端不必为 pages.dev 配置 CORS 白名单
  headers.delete('origin');
  // 剔除 Cloudflare 自己加的头，避免后端把它当成客户端信息
  for (const h of ['cf-connecting-ip', 'cf-ipcountry', 'cf-ray', 'cf-worker', 'cf-visitor']) {
    headers.delete(h);
  }
  headers.set('x-forwarded-proto', 'https');

  const init = {
    method: request.method,
    headers,
    redirect: 'manual',
  };
  // 只有带 body 的方法才透传 body（GET/HEAD 不能带）
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = request.body;
  }

  let res;
  try {
    res = await fetch(target, init);
  } catch (err) {
    return new Response(
      JSON.stringify({ detail: `反代后端失败：${origin}（${err && err.message}）` }),
      { status: 502, headers: { 'content-type': 'application/json; charset=utf-8' } }
    );
  }

  const outHeaders = new Headers(res.headers);
  // fetch 已经自动解压，保留这些头会让浏览器再次解码导致乱码
  for (const h of ['content-encoding', 'content-length', 'transfer-encoding', 'connection']) {
    outHeaders.delete(h);
  }
  outHeaders.set('x-proxied-to', origin);

  return new Response(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers: outHeaders,
  });
}
