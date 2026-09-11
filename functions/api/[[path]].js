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
 * 边缘缓存（2026-09 新增）：
 *   回源实测 4.8–14.3 秒（Vercel hkg1 冷启动 + 新加坡 TiDB），因此对**匿名只读接口**做边缘缓存。
 *   实现要点（踩过的坑）：
 *     1) 本代理把所有请求收敛到出站 URL `/api/index`，真实路径放在请求头里 →
 *        依赖默认缓存键（出站 URL）会把所有接口撞成同一条缓存，
 *        `/api/videos` 会拿到 `/api/content/banners` 的数据。
 *     2) `init.cf.cacheKey` 在 Pages Functions 上不可靠，因此改为**显式 Cache API**
 *        （caches.default + 以"客户端请求 URL"为键），行为确定、可验证。
 *     3) 带 Authorization 的请求一律不缓存（可能含个人进度数据，避免串号）。
 *
 * 部署位置（仓库根目录，Pages 会自动识别）：
 *   functions/api/[[path]].js
 */

const DEFAULT_API_ORIGIN = 'https://ai-nine-inky.vercel.app';

/** 匿名只读接口白名单：命中才进边缘缓存 */
const CACHEABLE = [
  /^\/api$/,
  /^\/api\/courses(\/|$)/,
  /^\/api\/videos(\/|$)/,
  /^\/api\/projects(\/|$)/,
  /^\/api\/learning-paths(\/|$)/,
  /^\/api\/content\//,
  /^\/api\/ai\/models$/,
  /^\/api\/assessment\/questions$/
];

const CACHE_SECONDS = 60;

export async function onRequest(context) {
  const { request, env, waitUntil } = context;
  const url = new URL(request.url);

  const origin = String(env.API_ORIGIN || DEFAULT_API_ORIGIN).replace(/\/+$/, '');

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

  // ---- 边缘缓存：只缓存匿名 GET 白名单 ----
  const anonymous = !headers.get('authorization');
  const cacheable = request.method === 'GET' && anonymous && CACHEABLE.some((re) => re.test(url.pathname));
  // 缓存键 = 客户端看到的完整 URL（含 query），因此每个接口、每种查询各自一条缓存
  const cacheKey = cacheable ? new Request(url.toString(), { method: 'GET' }) : null;
  const cache = typeof caches !== 'undefined' ? caches.default : null;

  if (cacheKey && cache) {
    const hit = await cache.match(cacheKey);
    if (hit) {
      const hitHeaders = new Headers(hit.headers);
      hitHeaders.set('x-edge-cache', 'HIT');
      return new Response(hit.body, { status: hit.status, statusText: hit.statusText, headers: hitHeaders });
    }
  }

  // Vercel 的 Serverless 路由只认精确的 /api/index（实测：/api/courses 这类子路径
  // 会被边缘节点直接 404，函数根本没执行）。所以对 Vercel 目标，我们固定打到
  // 函数入口，再用请求头把真实路径交给 api/index.py 还原。
  // 目标不是 Vercel（例如以后换成阿里云函数计算/自建后端）时，按原样透传路径即可。
  const isVercel = /\.vercel\.app$/i.test(new URL(origin).hostname);
  let target;
  if (isVercel) {
    target = origin + '/api/index';
    headers.set('x-original-path', url.pathname);
    headers.set('x-original-query', url.search.startsWith('?') ? url.search.slice(1) : '');
  } else {
    target = origin + url.pathname + url.search;
  }

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

  if (cacheKey && cache && res.ok) {
    outHeaders.set('cache-control', `public, max-age=30, s-maxage=${CACHE_SECONDS}, stale-while-revalidate=300`);
    outHeaders.set('x-edge-cache', 'MISS');
    const payload = new Response(res.body, {
      status: res.status,
      statusText: res.statusText,
      headers: outHeaders,
    });
    // 写缓存不阻塞响应（Pages Functions 提供 waitUntil）
    const put = cache.put(cacheKey, payload.clone());
    if (typeof waitUntil === 'function') waitUntil(put);
    else await put;
    return payload;
  }

  return new Response(res.body, {
    status: res.status,
    statusText: res.statusText,
    headers: outHeaders,
  });
}
