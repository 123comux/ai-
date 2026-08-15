"""轻量进程内 TTL 缓存（只读静态数据用）。

- 缓存课程/方向/Banner 等不变或极少变的数据，降低重复 DB/JSON 读取。
- 短 TTL（默认 60s）+ 显式 clear：进程重启自动清空；数据重新生成后重启即失效，
  不会长期返回陈旧数据。
- 进度、视频完成态等会变的数据一律不缓存。
"""

import threading
import time

DEFAULT_TTL = 60  # 秒

_lock = threading.Lock()
_cache: dict[str, tuple[float, object]] = {}


def get(key: str) -> object | None:
    item = _cache.get(key)
    if item is None:
        return None
    expires, value = item
    if time.time() > expires:
        with _lock:
            _cache.pop(key, None)
        return None
    return value


def set(key: str, value: object, ttl: int = DEFAULT_TTL) -> None:
    with _lock:
        _cache[key] = (time.time() + ttl, value)


def clear(key: str | None = None) -> None:
    with _lock:
        if key is None:
            _cache.clear()
        else:
            _cache.pop(key, None)
