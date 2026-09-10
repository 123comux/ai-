# 阿里云函数计算 FC 部署指南

**目标**：让手机在**国内网络下直接打开**这个站点（不需要梯子），同时满足三个前提：
**不买服务器、本机不装 Docker、不做域名备案**。

| 项目 | 说明 |
| --- | --- |
| 前端 + 后端 | 同一个容器（FastAPI 同时提供 H5 页面和 `/api` 接口，同源，无跨域） |
| 镜像构建 | GitHub Actions 云端构建（你的仓库是 public，Actions 分钟数免费不限量） |
| 镜像仓库 | 阿里云容器镜像服务 ACR **个人版**（免费） |
| 运行 | 阿里云函数计算 FC（自定义镜像 / Web 函数），弹性实例按量计费 |
| 数据库 | TiDB Cloud Serverless（沿用现在这套，不用改） |
| 访问地址 | FC 自动分配 `https://xxx.cn-hangzhou.fcapp.run`，**国内直连、不需要备案** |
| 费用 | 新用户前 3 个月有 15 万 CU/月 试用额度；之后这种低流量站点大约**每月几毛到几元** |

> 为什么不直接在本机 build：本机没有 Docker。FC 的自定义镜像函数**只能使用同一账号、同一地域的 ACR 镜像**，
> 所以链路固定为：`GitHub Actions 构建 → 推 ACR → FC 拉取`。仓库里已经准备好
> [Dockerfile](../../Dockerfile) 和 [构建工作流](../../.github/workflows/aliyun-fc-image.yml)。

---

## 一、先领免费额度（顺序很重要）

1. **确认实名认证**（你截图里「上云引导」的第 1 项，1/4 那个进度条）。
   FC、ACR 都要求实名，个人身份证认证几分钟就好。
2. 打开 **函数计算控制台** <https://fc.console.aliyun.com>（首次登录即获得试用资格）。
3. 去 **免费试用中心** <https://free.aliyun.com/> 搜「函数计算」→ 领取试用套餐。
   官方口径：*「函数计算为首次登录函数计算控制台的用户提供一定额度的免费试用包，以月为周期连续提供 3 个周期，
   每个周期超出 15 万 CU 使用量的部分自动转入按量付费」*
   （[官方文档](https://www.alibabacloud.com/help/zh/functioncompute/trial-quota-1)）。
   **先领，再创建函数**，避免被算成按量。
4. ACR 个人版免费，不需要领，直接下一步。

---

## 二、创建 ACR 镜像仓库（约 3 分钟）

1. 打开 <https://cr.console.aliyun.com>，左侧选 **个人版实例**，地域选 **华东1（杭州）**。
2. 首次使用先在 **访问凭证** 里 **设置固定密码**（这个密码就是后面 GitHub Secret 里的 `ACR_PASSWORD`）。
   用户名就是你阿里云账号的登录名（`ACR_USERNAME`）。
3. **命名空间** → 创建，例如 `work16c4`。
4. **镜像仓库** → 创建镜像仓库：
   - 仓库名称：`aishixi`
   - 仓库类型：**私有**（FC 同账号可以拉取，私有更安全）
   - 代码源：**本地仓库**（我们不用它的自动构建）
5. 记下完整镜像地址，形如：
   ```
   registry.cn-hangzhou.aliyuncs.com/work16c4/aishixi
   ```

---

## 三、在 GitHub 配 5 个 Secret

仓库 → **Settings → Secrets and variables → Actions → New repository secret**：

| Secret 名 | 值 | 从哪来 |
| --- | --- | --- |
| `ACR_REGISTRY` | `registry.cn-hangzhou.aliyuncs.com` | 固定值（地域要和 FC 函数一致） |
| `ACR_NAMESPACE` | `work16c4` | 第二步建的命名空间 |
| `ACR_REPOSITORY` | `aishixi` | 第二步建的仓库名 |
| `ACR_USERNAME` | 你的阿里云账号登录名 | ACR 访问凭证页 |
| `ACR_PASSWORD` | 你在 ACR 设的固定密码 | ACR 访问凭证页 |

---

## 四、跑一次构建（不需要 Docker）

仓库 → **Actions** → 左侧 **Build & Push Image (Aliyun FC)** → **Run workflow**（分支 `main`）。

- 大约 5–10 分钟（要装 Node 依赖编译 H5，再打 Python 镜像）。
- 成功后日志最后的 Summary 会打印镜像地址；ACR 控制台 → 镜像仓库 → `aishixi` → **镜像版本** 里能看到 `latest`。
- 之后**每次 push 到 main，只要碰到前端/后端代码就会自动出新镜像**。

---

## 五、创建 FC 函数（控制台点选，逐项对照）

控制台 <https://fc.console.aliyun.com> → 顶部地域选 **华东1（杭州）** → **函数 → 创建函数**：

| 配置项 | 填什么 | 说明 |
| --- | --- | --- |
| 函数类型 | **Web 函数** | 直接对外提供 HTTP |
| 函数名称 | `aishixi-h5` | 唯一即可 |
| 运行环境 | **自定义镜像 → 使用 ACR 中的镜像** | 选 `work16c4/aishixi`，版本 `latest` |
| 启动命令 / 监听端口 | 启动命令**留空**，监听端口填 **8010** | ★ 必须和镜像里的 `PORT=8010` 一致，否则报 `PortNotListening` |
| 规格 | vCPU **0.5**、内存 **1024 MB** | 低流量足够；想更省可 512 MB |
| 执行超时时间 | **120 秒** | AI 接口内部最长 60 秒，要留余量 |
| 单实例并发度 | **10** | 一个实例并发处理多个请求，省额度 |
| 最小实例数 | **0** | 不用不收费；设 1 会常驻计费（但没冷启动） |
| 磁盘 | 默认 512 MB | 写日志/缓存够用 |
| 环境变量 | 抄 [`fc-env.template`](./fc-env.template) | DB / JWT_SECRET / 智谱 Key，和 Vercel 那套一样 |
| HTTP 触发器 | 触发器类型 **HTTP**，认证方式 **anonymous**，公网访问 URL **开启** | 选 `function` 的话链接需要签名，浏览器打不开 |
| 日志 | **自动配置**（会建一个 `serverless-<地域>` 的 SLS 项目） | 出问题只能看这里 |
| 时区 | `Asia/Shanghai`（可选） | 日志时间对得上 |

创建完成后，函数详情页会给出**公网访问地址**：

```
https://aishixi-h5-xxxxxxxx.cn-hangzhou.fcapp.run
```

> 注意：**不要**去改镜像里的 `PORT`，也不要在环境变量里再加 `PORT`。
> 容器入口脚本（[`backend/docker-entrypoint.sh`](../../backend/docker-entrypoint.sh)）会优先采用 FC 注入的
> `FC_SERVER_PORT`，其次才是镜像里的 `PORT=8010`，两边保持一致就不会出现端口不匹配。

---

## 六、验收

本机（Windows，仓库根目录）：

```powershell
py tools\check_live.py https://aishixi-h5-xxxxxxxx.cn-hangzhou.fcapp.run
# 可选：顺带真实登录一次
py tools\check_live.py https://aishixi-h5-xxxxxxxx.cn-hangzhou.fcapp.run --login 138xxxxxxxx
```

这个脚本会跑 20 项检查（H5 首页、静态资源、`/api` 探活、课程/视频/项目列表、登录、AI 接口等），
全部通过才算上线成功。然后**用手机流量直接打开**（不挂梯子）复测一遍。

---

## 七、以后再更新怎么办

```powershell
git add -A
git commit -m "feat: xxx"
git push            # → Actions 自动构建并推送新镜像
```

然后必须去 **FC 控制台 → 函数 → 配置 → 镜像 → 重新选择 `:latest` → 点击「部署」**。
FC 记录的是创建/更新时的镜像 Digest，只推镜像不改函数，函数**仍然跑旧版本**
（官方文档明确要求镜像变化后要及时更新函数）。

---

## 八、常见报错对照表

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `PortNotListening: port 9000 is not listening on 0.0.0.0` | 函数「监听端口」和镜像里的 `PORT` 不一致 | 控制台把监听端口改成 `8010`；入口脚本已优先读 `FC_SERVER_PORT` |
| 函数 `Failed` / 拉取镜像失败 | 镜像地域与函数地域不同、或不在同一账号下 | 两者都用**华东1（杭州）**、同一账号 |
| 浏览器打开 502 / 服务不可用 | 容器启动超时（启动脚本卡住） | 看函数日志；确认没设 `SEED_ON_BOOT=true`（会对云库灌种子，很慢） |
| 页面能开、接口 500 | 环境变量缺项（DB 或 `JWT_SECRET`） | 对照 `fc-env.template` 补齐；`/api` 返回里带运行环境信息 |
| 想确认没开后门 | `DEV_MODE` 代码默认是 `true` | 环境变量里必须显式 `DEV_MODE=false` |
| 首次请求慢 2–3 秒 | 弹性实例被回收后的冷启动 | 能接受就不管；介意就把「最小实例数」设 1（会一直计费） |
| 容器日志提示写文件失败 | 平台文件系统只读 | 环境变量加 `FS_READONLY=1`（代码会改成不落盘） |
| 收到 SLS 计费/额度提醒 | 日志服务超出免费额度 | 关闭日志功能，或降低日志量 |

---

## 九、费用与方案对比

| 项 | 试用期内（前 3 个月） | 之后（按量，低流量估算） |
| --- | --- | --- |
| FC 计算 | 15 万 CU/月，基本用不完 | 假设 1000 请求/天 × 100ms × 512MB ≈ 每月 1500 GB·s，**几毛~几元** |
| ACR 个人版 | 免费 | 免费 |
| SLS 日志 | 有免费额度 | 流量小基本在额度内 |
| TiDB Cloud | 免费额度内（现在就在用） | 同理 |
| 服务器 / 域名 / 备案 | 都不需要 | 都不需要 |

对比你现在的 Vercel：`*.vercel.app` 在国内被墙（你实测电脑挂梯子能开、手机三种网络都打不开），
FC 给的是阿里云自己的域名，国内直连。两套可以**并存**：Vercel 留给海外/挂梯子的场景，FC 给国内手机。

> ⚠️ 微信小程序注意：小程序后台配置 request 合法域名时，要求域名**已 ICP 备案**，
> `*.fcapp.run` 不能直接用于小程序。H5 网页不受这条限制——如果以后要正式发小程序，
> 再单独买一个域名并备案（那时 FC 支持自定义域名）。

---

## 十、可选：用 Serverless Devs 一条命令部署

不想点控制台的话，仓库里给了 [`s.yaml`](./s.yaml)（镜像已经在 ACR 里，所以**不需要 Docker**）：

```bash
npm i -g @serverless-devs/s     # 阿里云 Cloud Shell 里已预装 npm，且无需 sudo
s config add                    # 按提示配一对阿里云 AccessKey（注意最小权限）
# 把 s.yaml 里的 <占位符> 和 region 改成你的真实值
s deploy
```

> 特别提醒：**阿里云 Cloud Shell 里没有 docker**（官方预装清单只有 kubectl / helm3 / docker-machine，
> 且不给 sudo），所以 Cloud Shell 只能用来 `s deploy` 部署已构建好的镜像，不能用来 build 镜像——
> 构建这件事交给 GitHub Actions。

---

## 你现在要做的 5 件事

1. 确认**实名认证**已完成（截图里上云引导的第 1 项）。
2. 领 FC 试用额度：<https://free.aliyun.com/> 搜「函数计算」。
3. 建 ACR 个人版命名空间 + 镜像仓库 `aishixi`，设固定密码（第二节）。
4. 在 GitHub 配 5 个 Secret（第三节）。
5. 跑 Actions 构建，然后按第五节的表格创建 FC 函数。

每一步做完把截图发我，或者直接把 FC 给的 `*.fcapp.run` 域名发我，我来跑验收。
