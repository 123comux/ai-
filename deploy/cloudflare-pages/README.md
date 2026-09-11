# Cloudflare Pages 部署指南（H5 静态托管 + /api 反代）

**当前状态：已上线** → <https://ai-h5.pages.dev>（手机在国内网络不挂梯子可直接打开）

```
手机浏览器 → https://ai-h5.pages.dev            ← Cloudflare Pages（H5 静态页面 + 静态图片）
                 └── /api/**  → Pages Function 反代 → Vercel 后端 → TiDB Cloud
```

前端用的是同源相对路径（`src/config/env.ts` 里 H5 的 `API_BASE = ''`），所以不用改前端、不用配 CORS。

## 一、为什么是 Pages 而不是 Workers（实测结论）

| 域名 | 国内连通性（实测） |
| --- | --- |
| `*.workers.dev` | ❌ DNS 被污染，解析到 69.162.134.178 这类黑洞 IP，全部超时 |
| `*.pages.dev` | ✅ 正常（`demo.pages.dev` 200 / 1.3s；我们的站点 200 / 0.9s） |
| `*.vercel.app` | ❌ 超时 |

所以：**Worker 建得再成功，`workers.dev` 域名在国内也打不开**；要用 Cloudflare 就必须落到 `pages.dev`。
（Cloudflare 自己的大陆节点 China Network 是 **企业版付费 + 每域名 ICP 备案**，免费版没有：
[官方文档](https://developers.cloudflare.com/china-network/)）

Pages Function 只能跑 JS/WASM，跑不了我们的 Python/FastAPI，所以后端仍留在 Vercel，由 Pages 反代。

## 二、本次踩到并修掉的两个坑

### 1. Vercel 只把「精确的 /api」路由到函数（子路径全 404）

症状：`/api` 返回 200，但 `/api/courses`、`/api/videos` 等返回 Vercel 的
`The page could not be found NOT_FOUND`，且响应头 `x-vercel-id` 里没有区域段（`hkg1`），
说明函数根本没被执行 —— `vercel.json` 里 `/api/:path*` → `/api/index/api/:path*` 这种
「目标路径带额外段」的 rewrite 并不能把请求送进函数。

修法（不依赖 Vercel rewrite 语义）：

- 反代固定请求函数入口 `/api/index`，把真实路径放进请求头
  `x-original-path: /api/courses`、`x-original-query: limit=10`；
- `api/index.py` 的 ASGI 中间件看到该头就还原 `scope["path"]` / `scope["query_string"]`。

相关文件：`functions/api/[[path]].js`、`api/index.py`。

### 2. Cloudflare Bot Fight 会拦非浏览器客户端

`requests` / `python-urllib` 直接打 `https://ai-h5.pages.dev` 会得到
`403 error code: 1010`（按 TLS 指纹识别为机器人）。浏览器和 `curl` 都正常，
所以**真实用户不受影响**；但自动化验收脚本要用 `curl`（或加浏览器 UA）来跑。

## 三、以后怎么更新

```powershell
# 前端改了（src/**）：重新构建 + 重新上传
npm run build:vercel
npx wrangler pages deploy dist-h5 --project-name ai-h5 --branch main

# 后端改了（backend/**）：push 即可，Vercel 会从 Git 自动部署
git push
```

Pages 项目类型是 **Direct Upload**（不是 Git 集成），所以前端每次都要手动跑上面两条命令。
`--commit-dirty=true` 可以消掉「working directory has uncommitted changes」的告警。

首次使用需要登录一次（OAuth，浏览器点 Allow）：

```powershell
npx wrangler login
```

## 四、验收结果（2026-09-11 实测，经 `https://ai-h5.pages.dev`）

| 检查 | 结果 |
| --- | --- |
| H5 首页 `/` | 200（1417B） |
| 静态图片 `/static/covers/project-0.png` | 200 PNG |
| `/api` 探活 | 200 |
| `/api/courses` | 200，20 条 |
| `/api/videos` | 200，24 条 |
| `/api/projects` | 200，5 条 |
| `/api/learning-paths` | 200，6 条 |
| `/api/content/banners` / `/directions` | 200，3 / 7 条 |
| `/api/assessment/questions?count=2` | 200，2 条 |
| `/api/ai/models` | 200 |
| `POST /api/auth/h5-login` | **200，签发 token（TiDB 写入正常）** |
| 带 token 访问 `/api/auth/me` | 200，用户 id=30002 |
| 无 token 访问 `/api/auth/me` | 401（正确） |

## 五、已知限制

| 限制 | 说明 | 对策 |
| --- | --- | --- |
| 请求时长 | Cloudflare 对单次请求有执行时长上限，AI 长回答可能被截断 | 把 `src/services/api.ts` 里 AI 调用的 60000ms 超时调小（如 20000） |
| 境外节点 | Pages 走香港/美国等节点，首字节 0.9–2.5 秒；接口要绕一圈到 Vercel（hkg1） | 追求国内速度就走阿里云 FC（`deploy/aliyun-fc/README.md`） |
| 微信内分享 | 微信对 `*.pages.dev` 有拦截记录 | 微信场景用阿里云 FC 域名 |
| Bot Fight | 非浏览器客户端 403 | 自动化用 curl |
| 小程序 | 小程序 request 合法域名要求 ICP 备案，`pages.dev` 不行 | H5 不受影响；要发小程序得走备案域名 |

## 六、和阿里云 FC 的关系

两条链路可以并存：

| | Cloudflare Pages（当前） | 阿里云 FC（备选，文件已就绪） |
| --- | --- | --- |
| 国内稳定性 | 取决于 `pages.dev` 是否被放行（境外节点） | 阿里云自有域名，国内直连，无需备案 |
| 部署成本 | 已上线，更新两条命令 | 需 ACR + 构建 + 建函数（约 20 分钟） |
| 后端 | 复用现有 Vercel | 后端也在国内 |
| 费用 | 免费 | 前 3 个月免费额度，之后约每月几元 |

如果哪天 `pages.dev` 也不通了，把 `functions/api/[[path]].js` 的 `API_ORIGIN`
改成 FC 的域名即可（目标不是 `*.vercel.app` 时，反代会按原样透传路径，不需要 `x-original-path`）。
