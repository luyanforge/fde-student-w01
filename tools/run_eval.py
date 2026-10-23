#!/usr/bin/env python3
"""在 evals/ 目录用 Promptfoo 跑 W1 基础评估。

用法:
    .venv/Scripts/python.exe tools/with_env.py -- .venv/Scripts/python.exe tools/run_eval.py
    .venv/Scripts/python.exe tools/run_eval.py --check      # 只检查 Node 环境，不跑评估

依赖 Node.js 22.22.0+，默认从 PATH 上找 node，也可用 FDE_NODE_DIR 指定目录。
国内网络默认走 npmmirror，可用 FDE_NPM_REGISTRY 覆盖。
输出：artifacts/w01/promptfoo-results.json
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = os.environ.get("FDE_NPM_REGISTRY", "https://registry.npmmirror.com")
PROMPTFOO_VERSION = "0.122.2"


def resolve_node_dir():
    """按优先级定位 Node 目录：FDE_NODE_DIR → PATH 上的 node → 找不到返回 None。"""
    explicit = os.environ.get("FDE_NODE_DIR")
    if explicit:
        p = Path(explicit).expanduser()
        return p if p.is_dir() else None
    found = shutil.which("node")
    if found:
        return Path(found).resolve().parent
    return None


def main(argv) -> int:
    check_only = "--check" in argv

    node_dir = resolve_node_dir()
    if node_dir is None:
        print(
            "找不到 node。请把 Node.js 22.22.0+ 加入 PATH，"
            "或用环境变量 FDE_NODE_DIR 指向 node 所在目录。",
            file=sys.stderr,
        )
        print("检查命令：node -v", file=sys.stderr)
        return 2

    node = node_dir / ("node.exe" if os.name == "nt" else "node")
    if not node.is_file():
        print(f"目录里没有 node 可执行文件：{node}", file=sys.stderr)
        return 2

    version = subprocess.run([str(node), "-v"], capture_output=True, text=True).stdout.strip()
    print(f"node {version}（{node_dir}）| registry {REGISTRY} | promptfoo {PROMPTFOO_VERSION}")

    if check_only:
        print("仅检查环境，未执行评估。")
        return 0

    env = os.environ.copy()
    env["PATH"] = str(node_dir) + os.pathsep + env.get("PATH", "")
    env.setdefault("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD", "1")
    env.setdefault("PROMPTFOO_DISABLE_TELEMETRY", "1")

    cmd = (
        f'npx --yes --registry={REGISTRY} promptfoo@{PROMPTFOO_VERSION} eval '
        f"--config promptfooconfig.yaml --no-cache "
        f"--output ../artifacts/w01/promptfoo-results.json"
    )
    print("执行:", cmd, flush=True)
    if os.name == "nt":
        proc = subprocess.run(["cmd", "/c", cmd], cwd=str(ROOT / "evals"), env=env)
    else:
        proc = subprocess.run(["sh", "-c", cmd], cwd=str(ROOT / "evals"), env=env)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
