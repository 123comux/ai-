"""文件系统 / 对象存储兼容层（Serverless 部署用）。

Vercel 等 Serverless 平台的部署目录**只读**（只有 /tmp 可写，且实例间不共享），
本地开发时一切正常、上线才报 PermissionError —— 这个模块把差异收口：

- `is_readonly()`     判断当前是否只读环境（VERCEL / FS_READONLY / 写探测）；
- `safe_write_json()` 写 JSON 的**安全版**：只读或失败时告警并返回 False，绝不打断请求；
                       并且写临时文件再原子替换，避免并发写坏文件；
- `save_avatar()`     头像存储：优先 Vercel Blob（配了 BLOB_READ_WRITE_TOKEN 时），
                       否则写本地 static/avatars；两者都不可用返回 None（调用方给友好提示）。

设计原则：数据库是唯一事实来源，这些 JSON 只是给旧逻辑兜底/镜像用的，
写不进去不影响功能（进度、收藏、测评结果都在 MySQL 里）。
"""
import json
import logging
import os
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

_readonly_cache = None


def is_readonly() -> bool:
    """当前环境是否不允许写部署目录。"""
    global _readonly_cache
    if _readonly_cache is None:
        forced = os.getenv('FS_READONLY', '').strip().lower()
        if forced in ('1', 'true', 'yes', 'on'):
            _readonly_cache = True
        elif forced in ('0', 'false', 'no', 'off'):
            _readonly_cache = False
        elif os.getenv('VERCEL'):
            # Vercel 的部署目录只读（/tmp 除外）
            _readonly_cache = True
        else:
            probe = BASE_DIR / 'data' / '.write_probe'
            try:
                probe.parent.mkdir(parents=True, exist_ok=True)
                probe.write_text('1', encoding='utf-8')
                probe.unlink()
                _readonly_cache = False
            except Exception:
                _readonly_cache = True
    return _readonly_cache


def safe_write_json(path, data, indent: int = 2) -> bool:
    """写 JSON；只读文件系统或任何异常都只告警，返回是否真的写入。"""
    if is_readonly():
        logging.info('[fsx] 只读环境，跳过写文件（数据已在数据库中）：%s', path)
        return False
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + '.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        os.replace(tmp, p)
        return True
    except Exception as e:
        logging.warning('[fsx] 写 %s 失败（已忽略，不影响功能）：%s', path, e)
        return False


def blob_configured() -> bool:
    return bool(os.getenv('BLOB_READ_WRITE_TOKEN'))


def upload_blob(pathname: str, content: bytes, content_type: str) -> str:
    """上传到 Vercel Blob，返回公开 URL；失败抛异常（调用方兜底）。"""
    import requests

    token = os.getenv('BLOB_READ_WRITE_TOKEN', '')
    url = 'https://blob.vercel-storage.com/' + pathname.lstrip('/')
    resp = requests.put(url, data=content, timeout=30, headers={
        'Authorization': 'Bearer ' + token,
        'x-api-version': '7',
        'x-content-type': content_type or 'application/octet-stream',
        'x-add-random-suffix': '1',
    })
    resp.raise_for_status()
    return resp.json().get('url') or ''


def save_avatar(content: bytes, filename: str, content_type: str = '') -> str:
    """保存头像，返回可访问 URL；不可用时返回 ''（调用方提示用户）。

    顺序：Vercel Blob → 本地 static/avatars。
    """
    if blob_configured():
        try:
            return upload_blob('avatars/' + filename, content, content_type)
        except Exception as e:
            logging.warning('[fsx] Vercel Blob 上传失败：%s', e)
            return ''
    if is_readonly():
        logging.warning('[fsx] 只读环境且未配置 BLOB_READ_WRITE_TOKEN，头像无法保存')
        return ''
    try:
        avatar_dir = BASE_DIR / 'static' / 'avatars'
        avatar_dir.mkdir(parents=True, exist_ok=True)
        with open(avatar_dir / filename, 'wb') as f:
            f.write(content)
        return '/static/avatars/' + filename
    except Exception as e:
        logging.warning('[fsx] 本地头像写入失败：%s', e)
        return ''
