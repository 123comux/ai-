"""Backend configuration."""

import os
from pathlib import Path

# Load backend/.env (gitignored) — holds secrets like ZHIPU_API_KEY.
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Project root
BASE_DIR = Path(__file__).parent

# Data directories
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"

# Ensure directories exist
for d in [RAW_DIR, PROCESSED_DIR, KNOWLEDGE_BASE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============ 数据库（SQLite 默认 / MySQL 生产） ============
# DB_ENGINE=mysql 时使用 MySQL（业务 SQL 运行时做方言翻译），否则 SQLite。
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "data" / "cms.db"))
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ai_teach")

# Server config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Zhipu AI (GLM) API key — loaded from backend/.env (gitignored). Never hardcode.
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
ZHIPU_API_URL = os.getenv("ZHIPU_API_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions")

# DeepSeek AI（OpenAI 兼容）——与智谱并存，提供 standard / pro 档位。
# 无 key 时 model_router 自动回退到智谱，不影响功能。
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")

# ============ 微信订阅消息（模板消息） ============
# 模板 ID 需在小程序后台「订阅消息」申请后填入 backend/.env，未配置则静默跳过发送。
WX_SUB_TEMPLATE_CHECKIN = os.getenv("WX_SUB_TEMPLATE_CHECKIN", "")    # 打卡成功提醒
WX_SUB_TEMPLATE_HOMEWORK = os.getenv("WX_SUB_TEMPLATE_HOMEWORK", "")  # 作业评审结果通知
WX_SUB_TEMPLATE_LEARNING = os.getenv("WX_SUB_TEMPLATE_LEARNING", "")  # 学习提醒/里程碑
WX_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
WX_SUBSCRIBE_SEND_URL = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send"

# ============ 微信支付（商户号 V3，押金收付） ============
# 商户号未配置时，押金报名/退费走「占位路径」（仅记状态，不真正收钱），便于开发演示。
WXPAY_MCHID = os.getenv("WXPAY_MCHID", "")                       # 微信支付商户号
WXPAY_SERIAL_NO = os.getenv("WXPAY_SERIAL_NO", "")               # 商户 API 证书序列号
WXPAY_PRIVATE_KEY = os.getenv("WXPAY_PRIVATE_KEY", "")           # 商户 API 私钥 apiclient_key.pem 路径
WXPAY_APIV3_KEY = os.getenv("WXPAY_APIV3_KEY", "")               # APIv3 密钥（32 字节）
WXPAY_NOTIFY_URL = os.getenv("WXPAY_NOTIFY_URL", "")             # 支付回调公网 HTTPS 地址
WXPAY_REFUND_NOTIFY_URL = os.getenv("WXPAY_REFUND_NOTIFY_URL", "")  # 退款回调地址
WXPAY_API_BASE = os.getenv("WXPAY_API_BASE", "https://api.mch.weixin.qq.com")


def wxpay_configured() -> bool:
    """是否已配置微信支付商户号（未配置则押金走占位路径）。"""
    return all([WXPAY_MCHID, WXPAY_SERIAL_NO, WXPAY_PRIVATE_KEY, WXPAY_APIV3_KEY, WXPAY_NOTIFY_URL])

# Dataset config
FIREWEB_EDU_SAMPLE = "sample-10BT"  # Can also use "sample-100BT", "sample-350BT"
FIREWEB_EDU_MAX_ROWS = 1000  # Limit for local processing

QVAC_GENESIS_MAX_ROWS = 5000

STUDYCHAT_MAX_ROWS = 16851  # Full dataset

# CORS (allow Taro dev server + Web Preview + Cloud IDE + any port)
CORS_ORIGINS = [
    "null",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:57434",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:57434",
    "http://127.0.0.1:8000",
    "http://localhost:10087",
    "http://127.0.0.1:10087",
    "https://trae.mobile.volcapp.com",
]
# 生产域名（H5 端）通过环境变量追加：ALLOWED_CORS_ORIGINS="https://你的域名,https://www.你的域名"
CORS_ORIGINS += [o.strip() for o in os.getenv("ALLOWED_CORS_ORIGINS", "").split(",") if o.strip()]
CORS_ORIGIN_REGEX = r"https://.*\.(mobile\.volcapp\.com|volceapi\.com|apigateway.*\.volceapi\.com)"

# ============ WeChat Mini-Program Auth ============
# 微信小程序登录：code2session 换取 openid/session_key。
# 真实上线需在小程序后台填写 AppID / AppSecret（写入 backend/.env，勿提交）。
WECHAT_APPID = os.getenv("WECHAT_APPID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")
WECHAT_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"

# 开发模式：未配置 AppID/Secret 或显式 DEV_MODE=true 时，
# /api/auth/wechat-login 接受任意 code 并生成开发用户（openid=dev_<code>），
# 便于本地联调，无需真实微信环境。生产环境务必设为 false 并配置 AppID/Secret。
DEV_MODE = os.getenv("DEV_MODE", "true").lower() in ("1", "true", "yes", "on")

# 开发期"模拟切换用户"开关：为 true 时开放 /api/auth/dev/* 接口，
# 允许在设置页列出后台用户并以任意用户身份进入（便于验证多用户数据隔离）。
# 生产环境（DEV_MODE=false）强制关闭，避免开放任意用户切换接口。
_impersonate_env = os.getenv("DEV_IMPERSONATE", "false").lower() in ("1", "true", "yes", "on")
DEV_IMPERSONATE = _impersonate_env and DEV_MODE

# ============ Auth Token (HMAC-signed, dependency-free) ============
# 用于签发登录态 token 的密钥。生产环境必须配置强随机值，否则启动失败（fail-fast）。
JWT_SECRET = os.getenv("JWT_SECRET", "")
if not JWT_SECRET:
    if DEV_MODE:
        JWT_SECRET = "dev-insecure-secret-change-me"
    else:
        raise RuntimeError(
            "生产环境必须配置 JWT_SECRET（强随机值，例如 `py -c \"import secrets;print(secrets.token_hex(32))\"`），"
            "写入 backend/.env 后重启。"
        )
TOKEN_EXPIRE_DAYS = int(os.getenv("TOKEN_EXPIRE_DAYS", "30"))

# ============ 功能使用权限（5 天免费试用 + 缴纳押金解锁） ============
# 全部功能模块统一 5 天免费试用期：自用户首次打开小程序/首次使用功能（服务端首次确认）起算。
# 试用期结束后限制使用，直至缴纳押金（复用押金式培训的收押金通道，缴纳后实时解锁）。
ACCESS_TRIAL_DAYS = int(os.getenv("ACCESS_TRIAL_DAYS", "5"))                        # 免费试用期时长（天）
ACCESS_TRIAL_WARN_SECONDS = int(os.getenv("ACCESS_TRIAL_WARN_SECONDS", "86400"))    # 试用即将结束提醒窗口（秒），默认提前 24 小时
# 全部免费开关：置 true 时关闭「试用期结束 → 缴押金解锁」的收费墙，所有用户一律放行。
# 用于演示/公测阶段，无需缴纳押金即可使用全部功能。
ACCESS_ALL_FREE = os.getenv("ACCESS_ALL_FREE", "false").lower() in ("1", "true", "yes", "on")

# ============ AI 每日额度（试用/未缴押金用户限流） ============
# 未解锁（未缴押金）的已登录用户，AI 功能每日调用上限。已缴押金/解锁用户不限。
# 该上限按「天 × 用户」累计全部 AI 功能（导师/测评分析/课程推荐/实操分析）的总次数。
# 匿名（未登录）用户无身份可追踪，不计数也不限流，保持原有公开行为。
AI_DAILY_LIMIT_DEFAULT = int(os.getenv("AI_DAILY_LIMIT_DEFAULT", "20"))

# AI 功能标识（用于 ai_usage_daily.feature 区分统计口径，可分别查询/调上限）
AI_FEATURES = ("tutor", "assessment", "recommend", "practice")

# 服务端授权校验的豁免前缀（路径以该段开头即放行，不参与试用期拦截）：
# /api/auth 登录 | /api/access 权限状态/导语本身 | /api/deposit 押金收付（解锁通道）| /api/pay 支付回调
# /api/admin + /admin 后台 | /static 静态资源 | /health 探活
ACCESS_EXEMPT_PREFIXES = (
    "/api/auth", "/api/access", "/api/deposit", "/api/pay",
    "/api/admin", "/admin", "/static", "/health",
)

# 押金式培训：已缴纳押金（active）、或退费流程中（refund_pending/refunded）视为已付费解锁；
# 押金转为培训费可续学（converted）同样解锁。pending_payment（未完成支付）与 forfeited 不予解锁。
DEPOSIT_UNLOCKED_STATUSES = ("active", "refund_pending", "refunded", "converted")

# ============ 押金式培训（Deposit-style training）参数 ============
# 与商业评审报告《押金式培训版》对齐：
# 三锁门槛：时间锁 90 天 / 过程锁 完课率 100% + 作业 / 考核锁 均分 ≥85 + 实战项目
DEPOSIT_DEFAULT_AMOUNT = float(os.getenv("DEPOSIT_AMOUNT", "199.00"))  # 默认培训押金（元）
DEPOSIT_CURRENCY = "CNY"
DEPOSIT_TIME_LOCK_DAYS = 90          # 时间锁：报名后 90 天内须完成全部课程与考核
DEPOSIT_STAGES = 7                   # 七阶段课程 / 七阶段考核
DEPOSIT_PASS_SCORE = 85              # 考核锁：七阶段考核均分达标线
DEPOSIT_REFUND_WORKING_DAYS = 15     # 退费时效：最终考核通过后 15 个工作日内到账
DEPOSIT_REFUND_RATE_LOW = 0.15       # 预估真实退费率区间（收入测算用）
DEPOSIT_REFUND_RATE_HIGH = 0.25