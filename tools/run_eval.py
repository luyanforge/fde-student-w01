#!/usr/bin/env python3
"""在 evals/ 目录用 Promptfoo 跑 W1 基础评估（Windows 适配）。

用法:
    .venv/Scripts/python.exe tools/with_env.py -- .venv/Scripts/python.exe tools/run_eval.py

依赖 Node.js 22.22.0+。国内网络默认走 npmmirror，可用 FDE_NPM_REGISTRY 覆盖。
输出：artifacts/w01/promptfoo-results.json
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE_DIR = Path(os.environ.get("FDE_NODE_DIR", r"C:\Users\imace\.workbuddy\binaries\node\versions\22.22.2-6"))
REGISTRY = os.environ.get("FDE_NPM_REGISTRY", "https://registry.npmmirror.com")
PROMPTFOO_VERSION = "0.122.2"


def main() -> int:
    node = NODE_DIR / "node.exe"
    if not node.is_file():
        print(f"找不到 node：{node}", file=sys.stderr)
        return 2
    version = subprocess.run([str(node), "-v"], capture_output=True, text=True).stdout.strip()
    print(f"node {version} | registry {REGISTRY} | promptfoo {PROMPTFOO_VERSION}")

    env = os.environ.copy()
    env["PATH"] = str(NODE_DIR) + os.pathsep + env.get("PATH", "")
    env.setdefault("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD", "1")
    env.setdefault("PROMPTFOO_DISABLE_TELEMETRY", "1")

    cmd = (
        f'npx --yes --registry={REGISTRY} promptfoo@{PROMPTFOO_VERSION} eval '
        f"--config promptfooconfig.yaml --no-cache "
        f"--output ../artifacts/w01/promptfoo-results.json"
    )
    print("执行:", cmd, flush=True)
    proc = subprocess.run(["cmd", "/c", cmd], cwd=str(ROOT / "evals"), env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
