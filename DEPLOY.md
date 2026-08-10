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

**前端连接后端地址**：`src/services/api.ts` 中 `API_BASE` 默认 `http://localhost:8000`。
- 本地开发：保持 localhost 即可。
- 线上：改成 `https://your-domain.com`（小程序要求 HTTPS + 已备案域名；H5 同域由 Nginx 托管可保持同源）。

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
- [ ] 服务器域名已在小程序后台配置。
- [ ] `DEV_MODE=false`，且 `WECHAT_APPID/WECHAT_SECRET` 已填真实值。
- [ ] `JWT_SECRET` 已更换为强随机串。
- [ ] 押金/退费流程自测通过（报名 → 三锁进度 → 达标退费；未达标/超时/重复退均被拒）。
- [ ] 隐私协议：押金收取、退费规则、数据使用需在《隐私保护指引》与《押金服务协议》中明确说明（审核重点）。
- [ ] 类目选择正确（教育/在线培训），如涉及收费需对应资质。
- [ ] 真机预览：首页不白屏、登录态持久、视频/项目/测评/岗位对标/我的页核心流程可用。
- [ ] 提交审核时附「测试账号」与「功能说明」，加速过审。

---

## 4. 环境变量速查（backend/.env）

| 变量 | 说明 | 生产建议 |
|------|------|----------|
| `HOST` / `PORT` | 监听地址/端口 | `0.0.0.0` / `8000` |
| `JWT_SECRET` | Token 签名密钥 | **必换强随机串** |
| `TOKEN_EXPIRE_DAYS` | Token 有效期 | 30 |
| `ZHIPU_API_KEY` | 智谱 GLM Key | 必填（AI 主路径） |
| `WECHAT_APPID` / `WECHAT_SECRET` | 微信登录 | 必填（生产） |
| `DEV_MODE` | 开发模式 | **生产设为 false** |
| `DEPOSIT_AMOUNT` 等 | 押金三锁参数 | 对照商业评审报告 |

完整示例见 `backend/.env.example`。

---

## 5. 运维

- **日志**：Docker `docker logs ai-teach-backend`；裸机看 uvicorn 输出（已配置 `logging.INFO`）。
- **数据库备份**：定期备份挂载卷中的 `data/cms.db`（如 `cp cms.db cms.db.bak`）。
- **重新初始化**：删 `cms.db` 重启容器/进程，会自动重建并灌种子（注意：会清空用户数据）。
- **扩缩容**：SQLite 适合单机轻量场景；如需更高并发，可迁移到 PostgreSQL（改 `database.py` 连接层）并前置 Redis。

---

## 6. 快速核对命令

```bash
# 后端单测（29 项，应全绿）
cd backend && python -m unittest tests.test_all

# 前端类型检查（应 0 错误）
npx tsc --noEmit -p tsconfig.json

# 构建双端
npm run build:weapp && npm run build:h5
```
