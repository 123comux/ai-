# Cloudflare Pages 部署指南（H5 静态托管 + /api 反代）

**先说结论**：Cloudflare 免费版**不能**让站点走中国大陆节点（那是付费企业版 + 必须 ICP 备案，
见 [Cloudflare China Network 官方文档](https://developers.cloudflare.com/china-network/)），
但它有另一个用处 —— **你实测发现 `*.pages.dev` 在你的网络下能连通，而 `*.vercel.app` 打不开**，
所以这条路可行：

```
手机浏览器 → https://xxx.pages.dev        （Cloudflare Pages，托管 H5 静态页面）
                └── /api/**  → Pages Function 反代 → Vercel 后端（现有那套，已连 TiDB）
```

前端全程同源（H5 的 `API_BASE = ''`，见 `src/config/env.ts`），所以**不用改任何前端代码、不用配 CORS**。

| 项目 | 说明 |
| --- | --- |
| 费用 | Pages 免费版：无限带宽、每月 500 次构建 |
| 你要做的事 | 在 Cloudflare 建一个 Pages 项目，连上这个 GitHub 仓库（约 3 分钟） |
| 后端 | 继续用现有的 Vercel 部署（`https://ai-nine-inky.vercel.app`），不用动 |
| 备案 | 不需要（域名是 Cloudflare 的 `pages.dev`） |
| 风险 | ① 手机运营商是否放行 `pages.dev`（你电脑实测可达，手机需实测）② Cloudflare 对单次请求时长有限制，AI 长请求可能超时 |

---

## 一、Cloudflare 侧操作（3 分钟）

1. 登录 <https://dash.cloudflare.com>（没有账号就注册，免费）。
2. 左侧 **Workers & Pages** → **Create** → **Pages** → **Connect to Git**。
3. 授权 GitHub，选择仓库 **`123comux/ai-`**（分支 `main`）。
4. 构建设置（照抄，别用默认值）：

| 配置项 | 值 |
| --- | --- |
| Framework preset | `None` |
| Build command | `npm install --legacy-peer-deps && npm run build:vercel` |
| Build output directory | `dist-h5` |
| 环境变量（可选） | `NODE_VERSION = 20`（Taro 4 需要 Node ≥ 18） |
| 环境变量（可选） | `API_ORIGIN = https://ai-nine-inky.vercel.app`（默认值就是它，可留空） |

> `--legacy-peer-deps` 不能省：Taro 4 与 webpack 的 peer 依赖冲突会让 `npm ci` 直接 ERESOLVE 失败。
> `npm run build:vercel` = `taro build --type h5` + 把 `backend/static` 的封面/banner 拷进 `dist-h5/static`。

5. **Save and Deploy** → 等 2–4 分钟 → 得到 `https://ai-xxxx.pages.dev`。

## 二、验收

```powershell
# 1) 后端本身（应该一直能通）
py tools\check_live.py https://ai-nine-inky.vercel.app

# 2) 通过 Pages 反代访问同一套接口
py tools\check_live.py https://ai-xxxx.pages.dev
```

然后**用手机流量打开 `https://ai-xxxx.pages.dev`**（不挂梯子）：
页面能出来 + 数据能加载 = 这条路成立；如果连页面都打不开，说明运营商对 `pages.dev` 也不通，
那就回到阿里云函数计算方案（`deploy/aliyun-fc/README.md`）。

## 三、以后更新

Pages 项目已连 GitHub：**push 到 main 会自动重新构建部署**（不用像阿里云 FC 那样手动点「部署」）。
也可以在 Pages → Deployments → Retry deployment 手动重跑。

> ⚠️ 本机 `git push` 会被网络重置（实测），需要开全局梯子，或者让 Agent 用 GitHub API 推送
> （`%TEMP%\push-via-api.mjs`）。

## 四、常见问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 构建失败 ERESOLVE | 没加 `--legacy-peer-deps` | 按上表改 Build command |
| 构建成功但页面 404 | Build output directory 不是 `dist-h5` | 改成 `dist-h5` 后重新部署 |
| 页面能开、接口全 404 | `functions/` 目录没进部署 | 确认仓库里有 `functions/api/[[path]].js`，看部署日志里的 Functions 数量 |
| 接口 502 / `反代后端失败` | `API_ORIGIN` 写错，或 Vercel 后端挂了 | 浏览器里直接打开 `API_ORIGIN/api` 验证 |
| AI 接口超时 | Cloudflare 单次请求时长限制 | 把 `src/services/api.ts` 里 AI 相关调用的 60000ms 超时改小（如 20000） |
| 微信内打开异常 | 微信对 `*.pages.dev` 有拦截记录 | 微信内分享用阿里云 FC 域名更稳 |
| 网站很慢（1–3 秒首字节） | Pages 走的是境外节点（HK/LA 等） | 静态资源有缓存；接口延迟取决于后端，追求国内速度请用阿里云 FC |

## 五、和阿里云 FC 方案的关系

| | Cloudflare Pages | 阿里云 FC |
| --- | --- | --- |
| 国内直连稳定性 | 取决于 `pages.dev` 是否被放行（境外节点） | 阿里云自有域名，国内直连，无需备案 |
| 你要做的事 | 连一次 GitHub（3 分钟） | ACR + Secret + 构建 + 建函数（约 20 分钟） |
| 后端 | 复用现有 Vercel | 自建镜像，后端也在国内 |
| 更新 | push 自动部署 | 构建后需在 FC 点一次「部署」 |
| 费用 | 免费 | 前 3 个月免费额度，之后约每月几元 |

两者可以先上 Cloudflare 快速验证「手机能不能打开」，不行再走 FC。
