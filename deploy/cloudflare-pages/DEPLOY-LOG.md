# 部署日志（Cloudflare Pages · ai-h5）

## 2026-09-11 网页端全量重做上线

| 项 | 值 |
| --- | --- |
| 正式地址 | <https://ai-h5.pages.dev> |
| 本次生产部署 ID | 最新 `05b9f06a`（含桌面隐藏 tab 栏修复）；首版 `498f281b` |
| 部署方式 | `npx wrangler pages deploy dist-h5 --project-name ai-h5 --branch main`（Direct Upload，非 Git 集成） |
| 构建 | `npm run build:vercel`（= `taro build --type h5` + 拷 `backend/static` → `dist-h5/static`，40 个文件） |
| 线上验收 | `powershell -File tools/check-live-curl.ps1 -Base https://ai-h5.pages.dev` → **24/24 通过** |
| ⏪ 回滚锚点 | 上一个生产部署 **`6a13764d`**（17 小时前，commit `bfc4f32`，即重做前的旧界面） |

### 回滚步骤（1 分钟）

1. 打开 Cloudflare 控制台 → **Workers & Pages** → 项目 **ai-h5** → **Deployments**
2. 在列表里找到 `6a13764d`（Production / main）
3. 右侧 **⋯ → Rollback to this deployment**（或页面上的 Rollback 按钮）
4. 回滚后重跑验收：`powershell -File tools/check-live-curl.ps1 -Base https://ai-h5.pages.dev`

> 注意：回滚只影响**前端静态产物 + Pages Function**；后端在 Vercel，由 Git 自动部署，需单独回滚（Vercel 控制台 → Deployments → 目标版本 → Promote to Production）。

### 本次改动摘要

- **设计系统**：`src/styles/theme.scss` 全量替换为 Linear 式暗色 token（画布 `#08090a` / 三级表面 / hairline / 唯一强调色 `#5e6ad2`）+ 面板·玻璃·聚光描边·骨架屏·焦点环·进场动画等 mixin
- **响应式外壳**：`src/index.html` viewport 改 `device-width`；新增 `src/components/AppShell`（H5 用 `index.h5.tsx`：桌面侧边栏 + 顶栏 + 1180PX 内容列；小程序用 `index.tsx` 透明包裹），桌面隐藏 Taro 原生 tab 栏
- **通用组件**：`src/components/ui`（Button / Panel / Tag / SectionHeader / Stat / Skeleton / EmptyState / Reveal）
- **22 个页面**：11 页完整重做（首页、学习、我的、课程详情、视频、AI 导师、项目、项目详情、学习路径、章节、测评）+ 10 页桌面补丁 + 雷达图 canvas/svg 双路径换色
- **动效**：纯 CSS keyframes + IntersectionObserver（不进小程序包），全部尊重 `prefers-reduced-motion`
- **性能**：Pages Function 对匿名只读接口做**显式 Cache API 边缘缓存**（60s，带 token 不缓存）
- **安全修复**：线上禁止「任意 code 换 token」（未配微信凭据时返回 503）；管理员默认口令 `admin/admin123` 已改为强口令；新增 `POST /api/admin/change-password`

### 已知事项

- 生产口令/后台凭据见 `docs/private/admin-credentials.txt`（不进公开仓库）
- 国内访问仍受「Cloudflare 境外 PoP」限制（首字节 1–3s）；想更快需把后端迁到阿里云 FC（`deploy/aliyun-fc/` 已备好，反代改 `API_ORIGIN` 即可切换）
- `tools/check_live.py`（urllib 版）会被 Cloudflare Bot Fight 拦成 403，线上验收请用 `tools/check-live-curl.ps1`
