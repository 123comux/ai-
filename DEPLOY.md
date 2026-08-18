# AI 教学服务平台 · 部署与上线指南

> 适用：押金式培训版（零基础 AI 教学小程序：Taro 4 前端 + FastAPI 后端 + SQLite）
> 目标：把本地可运行的项目，发布为「微信小程序 + H5 双端」可用的线上服务。

---

## 0. 架构总览

```
                         ┌─────────────────────────────┐
   微信小程序(dist/)  ──▶ │        Nginx (443 HTTPS)     │
   浏览器(H5 dist-h5) ──▶ │  - /api  → backend:8000      │
                         │  - /     → H5 静态产物        │
                         └───────────────┬─────────────┘
                                         │
                                  ┌──────▼──────┐
                                  │ FastAPI:8000 │
                                  │  SQLite cms.db│
                                  └──────────────┘
```

- **前端**：`src/`（Taro 4 + React + TS），`npm run build:weapp` → `dist/`，`npm run build:h5` → `dist-h5/`。
- **后端**：`backend/`（FastAPI + SQLite），`uvicorn main:app`。
- **AI**：线上主路径走智谱 GLM API（`ZHIPU_API_KEY`）；本地 `torch/transformers` 模型仅作兜底，**部署镜像不含这些重依赖**。

---

## 1. 后端部署

### 方式 A：Docker（推荐）

```bash
# 1) 准备环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，至少填：ZHIPU_API_KEY、WECHAT_APPID、WECHAT_SECRET、JWT_SECRET、DEV_MODE=false

# 2) 构建镜像
docker build -f backend/Dockerfile -t ai-teach-backend .

# 3) 运行（首次会自动建库+灌种子数据）
docker run -d -p 8000:8000 \
  --name ai-teach-backend \
  --env-file backend/.env \
  -v ai-teach-data:/app/data \
  ai-teach-backend
```

> 数据持久化：务必挂载 `/app/data` 卷，否则容器重建会丢失用户/押金数据。
> 重新灌数据：删除 `cms.db` 后重启容器，入口脚本会自动重新初始化。

### 方式 B：裸机 / 云服务器直接运行

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-runtime.txt
cp .env.example .env   # 填好真实值
python -m database     # 建库 + 灌种子数据（仅首次）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

### 健康检查

```bash
curl https://your-domain.com/api/health   # 期望 {"status":"ok"}
curl https://your-domain.com/             # 返回 API 元信息
```

---

## 2. 前端构建

```bash
# 安装依赖（仓库已含 node_modules，换机需重装）
npm install

# 微信小程序产物 -> dist/（用微信开发者工具导入 dist/ 预览/上传）
npm run build:weapp

# H5 产物 -> dist-h5/（部署到 Nginx 或任意静态托管）
npm run build:h5
```

> 构建报错 `Conflicting order ... mini-css-extract-plugin` 已在 `config/index.ts` 的
> `mini.miniCssExtractPluginOption.ignoreOrder=true` 处理，正常情况下不会再出现。

**前端连接后端地址**：`src/config/env.ts` 中 `API_BASE` 默认 `http://localhost:8000`，用构建时注入覆盖：
```bash
# 生产构建（微信小程序与 H5 均用已备案 HTTPS 域名）
TARO_APP_API_BASE=https://your-domain.com npm run build:weapp
TARO_APP_API_BASE=https://your-domain.com npm run build:h5
```
- 本地开发：不注入即用 localhost。
- 线上：小程序要求 HTTPS + 已备案域名；H5 同域由 Nginx 托管可保持同源。

---

## 3. 上线前置条件（微信小程序）

> 文档「上线前提（11.9）」：微信企业认证、域名备案、HTTPS、小程序提审。

### 3.1 微信企业认证
- 登录 [微信公众平台](https://mp.weixin.qq.com) → 小程序。
- 个人主体**无法**使用部分能力（如微信支付、部分接口），押金式培训涉及收退款，**强烈建议用企业/个体工商户主体**。
- 「设置 → 微信认证」提交营业执照等资料，付费认证（约 300 元/年）。

### 3.2 域名备案（ICP 接入备案）
- 服务器在国内（阿里云/腾讯云等）必须做 **ICP 备案**，否则域名无法解析到国内服务器，小程序也无法配置合法域名。
- 在云厂商备案系统提交：主体信息、网站信息、域名证书。
- 备案通过后，把域名解析（A 记录）指向服务器公网 IP。

### 3.3 HTTPS（必须）
- 小程序 `request` 合法域名**只接受 HTTPS（TLS 1.2+）**，且必须是**已备案的一级/子域名**。
- 用 Let's Encrypt 免费证书（certbot）或云厂商 SSL 证书。
- 证书文件放到 `deploy/certs/fullchain.pem`、`privkey.pem`，Nginx 配置见 `deploy/nginx.conf`。
- 证书续期：`certbot renew`（建议加入 crontab）。

### 3.4 配置小程序合法域名
- 公众平台 →「开发管理 → 开发设置 → 服务器域名」。
- 在 **request 合法域名** 增加：`https://your-domain.com`。
- 在 **uploadFile / downloadFile 合法域名**（如用到）按需增加。
- 本地开发可临时开启「不校验合法域名」（仅开发版生效，不能用线上）。

### 3.5 小程序提审清单（发版前自检）
- [ ] 已企业认证、域名已 ICP 备案、后端已 HTTPS。
- [ ] 服务器域名已在小程序后台配置（request / uploadFile / downloadFile 合法域名）。
- [ ] `DEV_MODE=false`，且 `WECHAT_APPID/WECHAT_SECRET` 已填真实值。
- [ ] `JWT_SECRET` 已更换为强随机串（未配置时生产启动会 fail-fast）。
- [ ] 押金/退费流程自测通过（报名 → 真实支付 → 三锁进度 → 作业提交 → 达标退费 → 后台人工复核 → 真实退款；未达标/超时/重复退均被拒）。
- [ ] 微信支付商户号已配置（`WXPAY_MCHID` 等），小额真实支付/退款各走一笔。
- [ ] 隐私协议：押金收取、退费规则、数据使用需在《隐私保护指引》与《押金服务协议》中明确说明（审核重点）。
- [ ] 类目选择正确（教育/在线培训），如涉及收费需对应资质。
- [ ] 真机预览：首页不白屏、登录态持久、课程/作业/测评/岗位对标/我的页核心流程可用。
- [ ] 提交审核时附「测试账号」与「功能说明」，加速过审。

---

## 4. 环境变量速查（backend/.env）

| 变量 | 说明 | 生产建议 |
|------|------|----------|
| `HOST` / `PORT` | 监听地址/端口 | `0.0.0.0` / `8000` |
| `JWT_SECRET` | Token 签名密钥 | **必换强随机串**（未配置生产启动即报错） |
| `TOKEN_EXPIRE_DAYS` | Token 有效期 | 30 |
| `ZHIPU_API_KEY` | 智谱 GLM Key（flash 档主路径） | 必填（AI 主路径） |
| `DEEPSEEK_API_KEY` | DeepSeek Key（standard/pro 档） | 建议填，提升 pro 档推理 |
| `WECHAT_APPID` / `WECHAT_SECRET` | 微信登录 | 必填（生产） |
| `DEV_MODE` | 开发模式 | **生产设为 false**（同时强制关闭 DEV_IMPERSONATE） |
| `ALLOWED_CORS_ORIGINS` | 额外 CORS 域名（逗号分隔） | `https://your-domain.com` |
| `WXPAY_MCHID` 等 6 项 | 微信支付商户号 | 涉及真实收退款时必填 |
| `WX_SUB_TEMPLATE_*` | 订阅消息模板 ID | 申请后填入（未填则静默不推送） |
| `DEPOSIT_AMOUNT` 等 | 押金三锁参数 | 对照商业评审报告 |
| `DB_ENGINE` | 数据库引擎 | `sqlite`（默认，本地/测试）或 `mysql`（生产） |
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME` | MySQL 连接参数 | `DB_ENGINE=mysql` 时必填 |

完整示例见 `backend/.env.example`。

---

## 5. 数据库（SQLite 默认 / MySQL 生产）

- **方言层** `backend/db.py`：业务代码零改动，`get_connection()` 按 `DB_ENGINE` 返回连接；
  MySQL 模式下 SQL 运行时做方言翻译（`?`→`%s`、`datetime('now')`→`NOW()`、upsert、DDL 时间戳列）。
- **本地/测试**：`DB_ENGINE` 缺省即 SQLite（`data/cms.db`），无需数据库服务。
- **生产**：`DB_ENGINE=mysql` + 连接参数，首次 `python -m database` 建表并灌种子（幂等）。
- **建库**：先建空库再灌种子：
  ```sql
  CREATE DATABASE ai_teach CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

## 6. CI（GitHub Actions）

`.github/workflows/ci.yml` 三个 job，push/PR 到 main 自动跑：
- **backend-sqlite**：SQLite 全量测试（`DEV_MODE=true`）
- **backend-mysql**：`mysql:8.0` service 容器 + 方言层全量测试（验证生产引擎）
- **frontend**：`npm ci` + `build:weapp` + `build:h5`

本地手动跑测试：
```bash
cd backend && DEV_MODE=true python -m pytest tests/ -q          # SQLite
cd backend && DEV_MODE=true DB_ENGINE=mysql DB_HOST=... python -m pytest tests/ -q   # MySQL
```

---

## 7. 运维

- **日志**：Docker `docker logs ai-teach-backend`；裸机看 uvicorn 输出（已配置 `logging.INFO`）。
- **数据库备份**：定期备份挂载卷中的 `data/cms.db`（如 `cp cms.db cms.db.bak`）。
- **重新初始化**：删 `cms.db` 重启容器/进程，会自动重建并灌种子（注意：会清空用户数据）。
- **扩缩容**：SQLite 适合单机轻量场景；如需更高并发，可迁移到 PostgreSQL（改 `database.py` 连接层）并前置 Redis。

---

## 8. 快速核对命令

```bash
# 后端单测（SQLite + MySQL 双引擎应全绿；当前 78 项）
cd backend && DEV_MODE=true python -m pytest tests/ -q

# 前端质量门禁（CI 同款）：类型检查 + ESLint + 单测
npm run typecheck      # tsc --noEmit，应 0 错误
npm run lint           # ESLint，应 0 error 0 warning
npm run test           # Vitest 单测，应全绿

# 构建双端
npm run build:weapp && npm run build:h5
```

## 9. 上线安全要点（务必核对）

- **支付未配置时的行为**：`enroll` 在**生产（DEV_MODE=false）且未配商户号时直接拒绝报名（503）**，绝不免费解锁付费墙；仅 `DEV_MODE=true` 走占位报名（开发自测）。上线前务必在 `.env` 设 `DEV_MODE=false` 并配齐 `WXPAY_MCHID/SERIAL_NO/PRIVATE_KEY/APIV3_KEY/NOTIFY_URL`，否则缴不了押金。
- **能力报告数据隔离**：已登录用户只读/写自己的 `user_ability_reports`，不再 fallback 全局 demo 文件；未登录的匿名测评不会算到登录账号头上（需重新测评）。全局 `ability_report.json` 仅供未登录会话 / job-matching。
- **`JWT_SECRET`**：生产必须替换为足够长的随机串，否则登录 token 可被伪造。

