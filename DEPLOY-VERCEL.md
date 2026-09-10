# 部署到 Vercel（H5 网页端 + FastAPI 后端 + 云 MySQL）

> 目标：一个 `https://<项目名>.vercel.app` 域名，网页端可用、后端接口同源、数据落在云 MySQL。
> 小程序端不受影响（仍连自己的后端地址，见文末「小程序怎么办」）。

---

## 0. 为什么不是「直接把仓库丢给 Vercel」就完事

Vercel 是 **Serverless**，有两个硬限制，本项目为此做了适配（代码已改好，你不需要动）：

| 限制 | 影响 | 本项目的处理 |
| --- | --- | --- |
| 部署目录**只读**（只有 `/tmp` 可写） | 原来的「写 JSON 文件」会 PermissionError → 500 | 新增 `backend/fsx.py`：只读环境自动跳过写文件（**数据真身在数据库**，不影响功能），头像改走 Vercel Blob |
| **没有持久磁盘** | SQLite 写不进去、实例间不共享 | 改用 **云 MySQL**（项目自带 SQLite→MySQL 方言层，业务代码零改动） |

另外还顺手修了 3 个「只有真跑在 MySQL 上才会暴露」的 bug（已加测试）：

1. `admin_sessions.token TEXT PRIMARY KEY` → MySQL 报 1170（TEXT 不能做键）；
2. 多行 upsert 的 `ON CONFLICT ... DO UPDATE` 没被方言层翻译 → MySQL 语法错误 1064；
3. MySQL 驱动返回 `datetime` 对象、SQLite 返回字符串 → Pydantic 校验失败（已在校验层统一）。

---

## 1. 准备云 MySQL（TiDB Cloud Serverless，免费 5GB）

本机 `localhost` 的 MySQL **Vercel 连不上**（除非把端口暴露公网，很不安全），所以要用公网库。

1. 打开 <https://tidbcloud.com> → 注册（GitHub / Google / 邮箱均可）；
2. 创建 **Serverless** 集群：区域选 **AWS Tokyo (ap-northeast-1)** 或 **Singapore**（离国内近，延迟低）；
   集群名随意，例如 `aishixi`；
3. 等 1~2 分钟创建完成 → 点 **Connect**：
   - **Connection Type: Public**（不要选 Private）
   - **User**: 记下形如 `xxxxxxxx.root`（不是 `root`）
   - **Region / Host**: 形如 `gateway01.ap-northeast-1.prod.aws.tidbcloud.com`
   - **Port**: `4000`
   - **Password**: 点 **Generate Password** 生成并**立刻保存**（只显示一次）
4. **允许 Vercel 访问**：TiDB Cloud 的 IP 白名单默认是 `0.0.0.0/0`（允许所有 IP）——
   保持默认即可。**必须这样**，因为 Vercel 没有固定出口 IP。
5. 数据库：可以用默认的 `test` 库，也可以在控制台 SQL Editor 里 `CREATE DATABASE aishixi;`。

> 其它同样可用的 MySQL 协议云库：阿里云 RDS、腾讯云 CDB、Aiven for MySQL、Railway MySQL。
> **不要用 PostgreSQL**（Neon / Supabase / Vercel Postgres）：项目的方言层目前只覆盖 MySQL，
> 换 PG 需要另写一套方言（`REPLACE INTO`、`AUTO_INCREMENT` 在 PG 里都没有）。

---

## 2. 把本地数据导进云库

在 `backend/` 目录下执行（Windows PowerShell 写法）。**先用 `--dry-run` 体检**：

```powershell
cd D:\aishixi\backend
$env:DB_ENGINE='mysql'
$env:DB_HOST='gateway01.ap-northeast-1.prod.aws.tidbcloud.com'   # 换成你的
$env:DB_PORT='4000'
$env:DB_USER='xxxxxxxx.root'                                     # 换成你的
$env:DB_PASSWORD='你在控制台生成的密码'
$env:DB_NAME='test'                                              # 或 aishixi
$env:DB_SSL_REQUIRED='true'                                      # TiDB 强制 TLS

py migrate_sqlite_to_mysql.py --dry-run    # 只体检：表清单、列宽风险、行数预览
py migrate_sqlite_to_mysql.py              # 正式建表 + 导入（幂等，可重复执行）
```

期望输出结尾：`[OK] 全部表行数一致，数据迁移完成。`（34 张表、约 126 行）

> **如果上一次导入失败过**（例如报 `(1064) ... near ''\')'`），库里可能残留了用旧结构建的表，
> 而 `init_db()` 是 `CREATE TABLE IF NOT EXISTS`、**不会修正已存在的表**。这时先清空再导：
>
> ```powershell
> py migrate_sqlite_to_mysql.py --dry-run --reset   # 先看会删掉哪些表
> py migrate_sqlite_to_mysql.py --reset             # 删表重建 + 导入
> ```

- 脚本会自动处理「SQLite 数据撑爆 MySQL TEXT(64KB)」的列（升级成 MEDIUMTEXT）；
- 脚本会做行数逐表核对，不一致就以非 0 退出，不会悄悄漏数据；
- 详细日志同时写到 `backend/data/migrate_to_mysql.log`。

> 密码里有特殊字符时用单引号包住：`$env:DB_PASSWORD='a&b#c'`。
> 你的 `JWT_SECRET` 也可以顺便生成一个：`py -c "import secrets;print(secrets.token_hex(32))"`

---

## 3. 配置 Vercel 环境变量

Vercel 项目 → **Settings → Environment Variables**（Production / Preview 都勾上）：

| 变量 | 值 | 必填 | 说明 |
| --- | --- | --- | --- |
| `DB_ENGINE` | `mysql` | ✅ | 切到 MySQL 引擎 |
| `DB_HOST` | `gateway01.xxx.tidbcloud.com` | ✅ | TiDB 的 Host |
| `DB_PORT` | `4000` | ✅ | TiDB 端口（注意不是 3306） |
| `DB_USER` | `xxxxxxxx.root` | ✅ | TiDB 用户名 |
| `DB_PASSWORD` | 生成的密码 | ✅ | |
| `DB_NAME` | `test` | ✅ | 库名 |
| `DB_SSL_REQUIRED` | `true` | ✅ | TiDB 强制 TLS（非本机地址时代码默认已开，显式写上更稳） |
| `JWT_SECRET` | 随机 64 位十六进制 | ✅ | **不配会启动失败**（`DEV_MODE=false` 时强制要求），用 `secrets.token_hex(32)` 生成 |
| `DEV_MODE` | `false` | ✅ | 生产必须关：开着会有「假 code 登录」后门 |
| `DEV_IMPERSONATE` | `false` | ✅ | 关掉「模拟切换用户」调试入口 |
| `ACCESS_ALL_FREE` | `true` / `false` | ⭕ | `true`＝全部免费；`false`＝启用「5 天试用 → 缴押金解锁」收费墙 |
| `ZHIPU_API_KEY` | 你的智谱 key | ⭕ | **不配也能跑**：AI 导师/测评会返回规则兜底回答（不会 500），但体验差 |
| `DEEPSEEK_API_KEY` | 你的 DeepSeek key | ⭕ | 同上，用于 pro 档位 |
| `ALLOWED_CORS_ORIGINS` | `https://你的域名.vercel.app` | ⭕ | H5 同源走 rewrite，**不需要**；只有小程序/其它域名直连时才需要 |
| `BLOB_READ_WRITE_TOKEN` | 建 Blob Store 后自动注入 | ⭕ | 配了才能上传头像（见第 6 节） |
| `AI_HTTP_TIMEOUT` | `15` | ⭕ | 已在 Vercel 环境自动取 15s，一般不用设 |

**⚠️ 上线前务必改管理员密码**：数据库里种了一个默认后台账号 `admin / admin123`
（`/admin` 页面）。改法：

```powershell
cd D:\aishixi\backend
py -c "import sqlite3,hashlib;c=sqlite3.connect('data/cms.db');c.execute('update admin_users set password_hash=? where username=?',(hashlib.sha256(b'你的新密码').hexdigest(),'admin'));c.commit();print('ok')"
# 然后重跑一次第 2 节的迁移脚本，把改动同步到云库
```

---

## 4. 部署

### 方式 A：Vercel CLI（**推荐**，一条命令，自动带上数据文件）

```powershell
cd D:\aishixi
npx vercel login          # 首次：选 GitHub / 邮箱登录
npx vercel --prod         # 首次会问项目名、目录等，直接回车即可
```

CLI 会把**当前工作目录**上传（遵守 `.vercelignore`），因此
`backend/data/processed/*.json` 这些**被 gitignore 但运行时要用的文件**会被正确打包。

### 方式 B：GitHub 自动部署（push 即部署）

在 Vercel 里 **Add New → Project → Import** 你的 GitHub 仓库（`123comux/ai-`）即可，
后续 `git push` 自动部署。但要注意：**Git 部署只拿仓库里有的文件**，而下面这些
运行时文件被 `.gitignore` 排除了，需要显式加入版本控制：

```powershell
cd D:\aishixi
git add -f backend/data/processed/assessment_questions.json `
           backend/data/processed/knowledge_base.json `
           backend/data/processed/projects.json `
           backend/data/processed/enriched_projects.json
git commit -m "chore: 纳入 Serverless 运行时需要的种子 JSON（测评题库/知识库）"
git push
```

（不加也能部署成功，但「AI 能力测评」会提示"暂无可用题目"、「知识库检索」为空。）

---

## 5. 部署后验收清单

按顺序点一遍，全绿即成功（我在本地用同样的配置实测过，见下面的期望结果）：

| # | 检查项 | 期望 |
| --- | --- | --- |
| 1 | 打开 `https://<项目>.vercel.app` | H5 首页正常，底部 Tab 可切换 |
| 2 | 首页课程 / 学习路径有内容 | 24 门课、11 条路径（数据来自云 MySQL） |
| 3 | 随便进一门课，点章节的 ▶ | 跳到视频页，B 站播放器正常（各章分P 不同） |
| 4 | 「我的」→ 手机号登录 | 能登录（**注意：当前没有短信验证，见第 7 节**） |
| 5 | 标记学完一章 / 收藏课程 / 打卡 | 刷新后仍在（说明写库成功；只读环境下不会 500） |
| 6 | AI 导师提问 | 配了 key → 正常回答；没配 → 返回兜底说明文字（都不是报错） |
| 7 | `/health` | `{"status":"ok"}` |
| 8 | `/admin` | 后台登录页（用你改过密码的 admin 账号） |
| 9 | 手机浏览器打开同一地址 | 布局自适应、底部不被 Tab 遮挡、可缩放 |

一键自检（把域名换成你的）：

```powershell
$base='https://你的项目.vercel.app'
(Invoke-WebRequest "$base/health" -UseBasicParsing).Content
(Invoke-WebRequest "$base/api/courses?limit=100" -UseBasicParsing).Content.Length   # 期望 > 100000
(Invoke-WebRequest "$base/api/learning-paths" -UseBasicParsing).Content.Length
```

---

## 6. 头像上传（可选，Vercel Blob）

只读文件系统写不了本地图片，所以头像走对象存储：

1. Vercel 项目 → **Storage → Create Database → Blob** → 免费额度 1GB；
2. 创建后 Vercel 会**自动注入** `BLOB_READ_WRITE_TOKEN` 到项目环境变量；
3. 重新部署一次（`npx vercel --prod`）让变量生效；
4. 之后上传头像会返回 `https://xxx.public.blob.vercel-storage.com/avatars/...`。

**没配 Blob 时**：上传接口返回 503 + 明确提示（不是 500），其它功能不受影响。

---

## 7. 安全清单（上线前请逐条确认）

- [ ] `DEV_MODE=false`（关掉假登录后门）、`DEV_IMPERSONATE=false`；
- [ ] `JWT_SECRET` 已设为随机值（不是 `dev-insecure-secret-change-me`）；
- [ ] 后台 `admin` 默认密码已改；
- [ ] **H5 手机号登录目前没有短信验证**（`/api/auth/h5-login` 接受任意合法手机号）——
      公开上线前建议：接入短信验证码，或改成微信 OAuth，或设 `H5_PHONE_LOGIN=false` 关闭该入口；
- [ ] 云库密码没有写进代码/仓库（只在 Vercel 环境变量里）；
- [ ] `.vercelignore` 已排除 `backend/.env`（本项目已配好，避免把本地密钥打进部署包）。

---

## 8. 常见问题

**Q：部署成功但接口 500 / 页面空白？**
先看 Vercel → Functions 日志。最常见是环境变量没配全（尤其 `DB_*` 和 `JWT_SECRET`）。

**Q：报 `(1045, "Access denied")` 或连不上数据库？**
- 确认 Host/Port/User 抄对（TiDB 端口是 **4000**，用户名带 `.root` 后缀）；
- 确认白名单允许所有 IP（`0.0.0.0/0`）——Vercel 没有固定出口 IP；
- 密码含特殊字符时在 Vercel 里原样粘贴，不要加引号。

**Q：第一次访问很慢（3~5 秒）？**
Serverless 冷启动正常现象。访问量上来后实例常驻会快很多。
如果 AI 接口偶发 504：说明供应商不可达（超时已限制在 15s，会走兜底回答）。

**Q：报 `(1064) ... near ''\')'` 或 `DEFAULT ('')` 语法错误？**
TiDB **不支持表达式默认值**，而 MySQL 8 要求 TEXT 列的默认值必须写成 `DEFAULT ('')` —— 两边冲突。
已修复（`db.py` 的方言层现在把「短标量默认值」的文本列翻成 `VARCHAR(1000)` 保留默认值，
把 `'[]'`/`'{}'` 这种 JSON 容器列的默认值去掉），**拉取最新代码后重跑即可**：

```powershell
py migrate_sqlite_to_mysql.py --dry-run --reset   # 旧表残留时先清空
py migrate_sqlite_to_mysql.py --reset
```

**Q：报 `(1364) Field 'xxx' doesn't have a default value`？**
同一类问题的另一种表现（app 插入时省略了该列）。当前代码里已确认 `users.grade`、`user_deposits.currency`
两处并修复；若再遇到，把列名告诉我，我把它加进「保留默认值」的判定里。

**Q：函数报 `Data too long for column`？**
重新跑一次第 2 节的迁移脚本，它会自动把该列升级为 MEDIUMTEXT。

**Q：想更新课程/视频数据？**
本地改完 → 重跑迁移脚本（幂等，只覆盖同主键的行）→ 或在 `/admin` 后台直接改。

**Q：免费额度够吗？**
- TiDB Cloud Serverless：5GB 存储 + 每月 5000 万 RU，本项目量级完全够；
- Vercel Hobby：100GB 带宽/月、函数 60s 上限（本项目已按 60s 配置）；
- 注意 Vercel Hobby **仅限非商业用途**，商用需升级 Pro。

---

## 9. 小程序怎么办

小程序**不能**像 H5 那样用同源 rewrite，必须用绝对地址。构建时注入：

```powershell
cd D:\aishixi
$env:TARO_APP_API_BASE='https://你的项目.vercel.app'
npm run build:weapp
```

然后在微信公众平台把该域名加入 **request 合法域名**（需 HTTPS）。
H5 端**不要**设这个变量（保持同源相对路径，交给 vercel.json 的 rewrite）。

---

## 10. 本次为部署新增/修改的文件

| 文件 | 作用 |
| --- | --- |
| `vercel.json` | 构建命令、函数配置（60s/1GB）、`/api`、`/static`、`/health`、`/admin` rewrite |
| `api/index.py` | Vercel Python 函数入口（复用 `backend/main.py` 的 app，兼容两种 rewrite 路径行为） |
| `requirements.txt`（根） | 函数运行时依赖（不含 torch，体积小） |
| `.vercelignore` | 排除 `node_modules`/`dist`/`backend/data/raw`(67MB)/`backend/.env` 等 |
| `tools/copy-vercel-static.mjs` + `package.json: build:vercel` | 把 `backend/static` 拷进 `dist-h5/static`，图片走 CDN |
| `backend/fsx.py`（新） | 只读 FS 兼容：`safe_write_json` / `save_avatar`(Vercel Blob) |
| `backend/migrate_sqlite_to_mysql.py`（新） | SQLite → MySQL 迁移 + 列宽自动升级 + 行数核对 |
| `backend/db.py` | 新增 MySQL TLS 支持、`datetime/Decimal` 类型归一化、TEXT 做键自动降级、多行 upsert 翻译 |
| `backend/config.py` | `DB_SSL_CA/DB_SSL_REQUIRED`、`AI_HTTP_TIMEOUT`；目录创建容错 |
| `backend/tests/test_all.py` | 新增 16 个测试：方言翻译、MySQL 类型一致性、只读 FS 降级 |
