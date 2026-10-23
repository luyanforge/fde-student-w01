#!/usr/bin/env python3
"""为被策略拦截的 uuid_utils 原生扩展打纯 Python 回退补丁（幂等）。

背景：本机启用了应用程序控制策略（Smart App Control），
`uuid_utils/_uuid_utils.pyd` 未签名，导入时报
`ImportError: DLL load failed ... 应用程序控制策略已阻止此文件`。

该扩展只被两处使用：`langchain_core.utils.uuid` 与 `langsmith._internal._uuid`，
二者都只需要 uuid7。本脚本在这两处加 try/except，失败时用纯 Python 实现
（RFC 9562 Method 1，毫秒时间戳 + 单调计数器）。不改动 uuid_utils 包本身。

重装依赖后需重新执行：`.venv/Scripts/python.exe tools/patch_uuid_utils_fallback.py`
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "# FDE-PATCH: uuid_utils fallback"

FALLBACK = '''
# FDE-PATCH: uuid_utils fallback
def _fde_fallback_uuid7(timestamp=None, nanos=None):
    """纯 Python uuid7；签名与 uuid_utils.uuid7 一致（timestamp 为秒，nanos 为余纳秒）。"""
    import os
    import threading
    import time
    from uuid import UUID

    global _fde_last_ms, _fde_counter
    if timestamp is None:
        total_ns = time.time_ns()
        seconds, rest_ns = divmod(total_ns, 1_000_000_000)
    else:
        seconds, rest_ns = int(timestamp), int(nanos or 0)
    ms = seconds * 1000 + rest_ns // 1_000_000

    with _fde_lock:
        if ms <= _fde_last_ms:
            _fde_counter += 1
        else:
            _fde_last_ms = ms
            _fde_counter = int.from_bytes(os.urandom(5), "big") & ((1 << 40) - 1)
        counter = _fde_counter
        if counter >> 42:  # 计数器溢出则借位到毫秒
            _fde_last_ms += 1
            _fde_counter = int.from_bytes(os.urandom(5), "big") & ((1 << 40) - 1)
            ms = _fde_last_ms
            counter = _fde_counter
        rnd = int.from_bytes(os.urandom(4), "big")

    value = (ms & ((1 << 48) - 1)) << 80
    value |= 0x7 << 76
    value |= (counter & ((1 << 12) - 1)) << 64
    value |= 0b10 << 62
    value |= ((counter >> 12) & ((1 << 30) - 1)) << 32
    value |= rnd
    return UUID(int=value)


_fde_lock = __import__("threading").Lock()
_fde_last_ms = 0
_fde_counter = 0
'''

PATCHES = {
    "langchain_core/utils/uuid.py": (
        "from uuid_utils.compat import uuid7 as _uuid_utils_uuid7",
        "from uuid_utils.compat import uuid7 as _uuid_utils_uuid7",
    ),
    "langsmith/_internal/_uuid.py": (
        "from uuid_utils.compat import uuid7 as _uuid_utils_uuid7",
        "from uuid_utils.compat import uuid7 as _uuid_utils_uuid7",
    ),
}


def patch(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return "already"
    original = "from uuid_utils.compat import uuid7 as _uuid_utils_uuid7"
    if original not in text:
        return "skip:import-not-found"
    replacement = (
        FALLBACK
        + "\ntry:  # FDE-PATCH: 原生扩展可能被系统策略拦截\n"
        + "    from uuid_utils.compat import uuid7 as _uuid_utils_uuid7\n"
        + "except Exception:  # noqa: BLE001\n"
        + "    _uuid_utils_uuid7 = _fde_fallback_uuid7\n"
    )
    path.write_text(text.replace(original, replacement, 1), encoding="utf-8")
    return "patched"


def main() -> int:
    site = ROOT / ".venv/Lib/site-packages"
    if not site.is_dir():
        site = ROOT / ".venv/lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    if not site.is_dir():
        print("找不到 site-packages，请先创建 .venv", file=sys.stderr)
        return 2
    for rel in PATCHES:
        p = site / rel
        print(f"{rel}: {patch(p) if p.is_file() else 'skip:missing'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
