# 智学 AI · 押金式 AI 教学服务平台

一个「押金式培训」的 AI 学习平台：用户免费试用 5 天，缴纳 ¥199 押金解锁全部功能，学完课程、完成作业、通过考核（三锁）达标后**全额退还押金**。面向零基础学员的 AI Agent 开发学习路线。

## 技术栈

- **前端**：Taro 4 + React 18 + TypeScript + Zustand（一套代码编译微信小程序 + H5）
- **后端**：FastAPI + SQLite（默认）/ MySQL（生产，方言自动翻译）
- **AI**：智谱 GLM / DeepSeek（模型路由），AI 导师 RAG、能力测评、作业评审、课程推荐
- **数据**：FineWeb-Edu / QVAC Genesis / StudyChat（课程、项目、知识库）
- **CI**：GitHub Actions（后端 SQLite+MySQL、前端 typecheck/lint/单测/双端构建）

## 目录结构

```
├── src/                  前端（Taro + React）
│   ├── pages/            页面（home/learn/project/assessment/deposit/...）
│   ├── components/       组件（AccessGate 等）
│   ├── services/         API 封装
│   ├── store/            zustand 状态（用户/权限/学习）
│   └── types/            类型定义
├── backend/              后端（FastAPI）
│   ├── routers/          接口路由 + 运营后台（admin_panel.html）
│   ├── services/         业务逻辑（AI 配额、权限、支付、模型路由等）
│   ├── data_pipeline/    数据/课程生成
│   ├── database.py       数据库 CRUD
│   ├── db.py             SQLite/MySQL 方言层
│   └── tests/            测试套件（96 项）
├── deploy/               Docker / Nginx 部署配置
└── docs/                 技术文档（不足清单、待办）
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # 配置 ZHIPU_API_KEY / WECHAT_* / DEV_MODE
python -m database            # 首次建表 + 灌种子数据
uvicorn main:app --reload     # 启动，默认 http://localhost:8000
```

- 运营后台：`http://localhost:8000/admin`（账号见 admin_users 表）
- 健康检查：`GET /health`

### 前端（微信小程序）

```bash
npm install
npm run dev:weapp             # 编译到 dist/，用微信开发者工具导入 dist/
```

### 前端（H5）

```bash
npm run dev:h5                # 默认 http://localhost:10087
```

## 测试与质量门禁

```bash
# 后端（conftest 自动用临时库，不污染开发数据；96 项）
cd backend && python -m pytest tests/ -q

# 前端
npm run typecheck
npm run lint
npm run test
```

## 上线部署

详见 [DEPLOY.md](DEPLOY.md)：Docker 一键部署、HTTPS/域名、商户号、提审清单、上线安全要点。
