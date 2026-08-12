"""微信支付 V3 服务：JSAPI 统一下单 / 回调验签解密 / 退款。

依赖 cryptography（RSA-SHA256 签名 + AES-256-GCM 解密），无其他重依赖。
商户号未配置时（wxpay_configured() 为 False）调用方走占位路径，见 deposit.py。
安全要点：
- 下单与退款用商户私钥签名（WECHATPAY2-SHA256-RSA2048）；
- 回调先验微信平台证书签名，再用 APIv3 密钥 AES-GCM 解密资源；
- 金额单位为「分」。
"""
import base64
import json
import logging
import time
import uuid

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import (
    WECHAT_APPID, WXPAY_MCHID, WXPAY_SERIAL_NO, WXPAY_PRIVATE_KEY,
    WXPAY_APIV3_KEY, WXPAY_NOTIFY_URL, WXPAY_REFUND_NOTIFY_URL, WXPAY_API_BASE,
)

logger = logging.getLogger(__name__)

_API = WXPAY_API_BASE

_private_key = None
# 微信平台证书缓存：{pem, expires_at}，回调验签用，定期刷新
_platform_cert = {"pem": "", "expires_at": 0}


# ---------- 基础工具 ----------

def _load_private_key():
    global _private_key
    if _private_key is None:
        with open(WXPAY_PRIVATE_KEY, "rb") as f:
            _private_key = serialization.load_pem_private_key(f.read(), password=None)
    return _private_key


def _nonce() -> str:
    return uuid.uuid4().hex


def _sign(message: str) -> str:
    key = _load_private_key()
    sig = key.sign(message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(sig).decode("utf-8")


def _auth_header(method: str, path: str, body: str) -> dict:
    timestamp = str(int(time.time()))
    nonce = _nonce()
    message = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body}\n"
    signature = _sign(message)
    return {
        "Authorization": (
            'WECHATPAY2-SHA256-RSA2048 mchid="%s",nonce_str="%s",signature="%s",'
            'timestamp="%s",serial_no="%s"'
        ) % (WXPAY_MCHID, nonce, signature, timestamp, WXPAY_SERIAL_NO),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "wechatpay-ai-teach/1.0",
    }


# ---------- 下单 ----------

def create_jsapi_order(out_trade_no: str, amount_fen: int, openid: str, description: str) -> str:
    """创建 JSAPI 支付单，返回 prepay_id。"""
    path = "/v3/pay/transactions/jsapi"
    body = {
        "appid": WECHAT_APPID,
        "mchid": WXPAY_MCHID,
        "description": (description or "智学AI·押金式培训")[:127],
        "out_trade_no": out_trade_no,
        "notify_url": WXPAY_NOTIFY_URL,
        "amount": {"total": int(amount_fen), "currency": "CNY"},
        "payer": {"openid": openid},
    }
    body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    resp = requests.post(_API + path, data=body_str.encode("utf-8"),
                         headers=_auth_header("POST", path, body_str), timeout=15)
    data = resp.json()
    if resp.status_code >= 300 or "prepay_id" not in data:
        raise RuntimeError(f"create_jsapi_order failed {resp.status_code}: {data}")
    return data["prepay_id"]


def build_pay_params(out_trade_no: str, amount_fen: int, openid: str, description: str) -> dict:
    """创建订单并生成 wx.requestPayment 需要的调起参数。"""
    prepay_id = create_jsapi_order(out_trade_no, amount_fen, openid, description)
    timestamp = str(int(time.time()))
    nonce = _nonce()
    package = f"prepay_id={prepay_id}"
    message = f"{WECHAT_APPID}\n{timestamp}\n{nonce}\n{package}\n"
    return {
        "appId": WECHAT_APPID,
        "timeStamp": timestamp,
        "nonceStr": nonce,
        "package": package,
        "signType": "RSA",
        "paySign": _sign(message),
    }


# ---------- 回调：验签 + 解密 ----------

def decrypt_resource(ciphertext_b64: str, nonce_b64: str, associated_data: str) -> dict:
    """用 APIv3 密钥 AES-256-GCM 解密回调资源。"""
    aesgcm = AESGCM(WXPAY_APIV3_KEY.encode("utf-8"))
    ct = base64.b64decode(ciphertext_b64)
    nonce = base64.b64decode(nonce_b64)
    ad = associated_data.encode("utf-8") if associated_data else None
    plaintext = aesgcm.decrypt(nonce, ct, ad)
    return json.loads(plaintext.decode("utf-8"))


def _get_platform_cert() -> str:
    """获取并缓存微信平台证书（用于回调验签）。12 小时刷新。"""
    global _platform_cert
    now = time.time()
    if _platform_cert["pem"] and now < _platform_cert["expires_at"]:
        return _platform_cert["pem"]
    path = "/v3/certificates"
    resp = requests.get(_API + path, headers=_auth_header("GET", path, ""), timeout=15)
    data = resp.json()
    if resp.status_code >= 300 or not data.get("data"):
        raise RuntimeError(f"get_platform_cert failed {resp.status_code}: {data}")
    for cert in data["data"]:
        try:
            enc = cert["encrypt_certificate"]
            plain = decrypt_resource(enc["ciphertext"], enc["nonce"], enc["associated_data"])
            _platform_cert = {"pem": plain["certificate"], "expires_at": now + 12 * 3600}
            return _platform_cert["pem"]
        except Exception:  # noqa: BLE001 —— 逐个证书尝试
            continue
    raise RuntimeError("no usable platform certificate")


def verify_notify_signature(headers: dict, body_str: str) -> bool:
    """校验微信支付回调签名（失败抛异常，应拒绝回调）。"""
    ts = headers.get("Wechatpay-Timestamp", "")
    nonce = headers.get("Wechatpay-Nonce", "")
    sig_b64 = headers.get("Wechatpay-Signature", "")
    serial = headers.get("Wechatpay-Serial", "")
    if not all([ts, nonce, sig_b64, serial]):
        raise ValueError("missing wechatpay signature headers")
    pem = _get_platform_cert()
    pub = serialization.load_pem_public_key(pem.encode("utf-8"))
    message = f"{ts}\n{nonce}\n{body_str}\n"
    try:
        pub.verify(base64.b64decode(sig_b64), message.encode("utf-8"),
                   padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception as e:  # noqa: BLE001 —— 验签失败即拒绝
        raise ValueError(f"wechatpay signature verify failed: {e}")


def parse_notify(body_str: str) -> dict:
    """解密支付回调 body，返回业务数据（out_trade_no / transaction_id / trade_state / amount）。"""
    raw = json.loads(body_str)
    res = raw.get("resource", {})
    if raw.get("event_type") == "TRANSACTION.SUCCESS":
        return decrypt_resource(res.get("ciphertext", ""), res.get("nonce", ""), res.get("associated_data", ""))
    return {}


# ---------- 退款 ----------

def refund(out_trade_no: str, out_refund_no: str, total_fen: int, refund_fen: int, reason: str = "") -> dict:
    """发起退款（V3 /v3/refund/domestic/refunds），返回退款受理结果。"""
    path = "/v3/refund/domestic/refunds"
    body = {
        "out_trade_no": out_trade_no,
        "out_refund_no": out_refund_no,
        "reason": (reason or "押金式培训达标全额退费")[:80],
        "notify_url": WXPAY_REFUND_NOTIFY_URL,
        "amount": {"refund": int(refund_fen), "total": int(total_fen), "currency": "CNY"},
    }
    body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    resp = requests.post(_API + path, data=body_str.encode("utf-8"),
                         headers=_auth_header("POST", path, body_str), timeout=15)
    data = resp.json()
    if resp.status_code >= 300:
        raise RuntimeError(f"refund failed {resp.status_code}: {data}")
    return data
