#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把本地文件 PUT 到 GitHub 仓库 Gordon9999/life 的指定远程路径。
本机 git push 不可用，必须走 Contents API（带 sha 更新 / 无 sha 新建）。

用法:
  put_life.py <本地文件> <远程路径> [<本地文件> <远程路径> ...]

例:
  put_life.py trip-us-aug-2026.html us/index.html \
              orders-us-aug-2026.html us/orders-us-aug-2026.html \
              weather-luggage-us-aug-2026.html us/weather-luggage-us-aug-2026.html \
              trip-us-aug-2026.md us/trip-us-aug-2026.md

依赖: curl。
  - token：优先环境变量 GH_TOKEN / GITHUB_TOKEN（云端沙箱模式），否则 macOS git credential（本地模式）
  - 代理：云端模式直连 api.github.com 免代理；本地模式用 scutil 动态端口 + curl -x
  - 带 token 的 PUT 可能 302，curl 已加 -L 跟随
"""
import sys, os, base64, json, subprocess

REPO = "Gordon9999/life"  # 如需改仓库，改这里


def proxy_port():
    try:
        out = subprocess.run(["scutil", "--proxy"], capture_output=True, text=True).stdout
        for line in out.splitlines():
            if "HTTPPort" in line:
                return line.split()[-1]
    except Exception:
        pass
    return "7897"  # 兜底


def token():
    # 云端沙箱模式：优先读环境变量（沙箱无本地钥匙串）
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok.strip()
    # 本地模式：macOS git credential 取钥匙串里的 token
    cmd = 'printf "protocol=https\\nhost=github.com\\n" | git credential fill | grep "^password=" | cut -d= -f2'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True).stdout.strip()


def proxy_args():
    # 云端模式直连，无需代理；本地模式走动态代理端口
    if os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"):
        return []
    return ["-x", f"http://127.0.0.1:{proxy_port()}"]


def put(local, remote):
    tok = token()
    if not tok:
        print(f"[SKIP] {remote}: 取不到 token（设 GH_TOKEN 环境变量或配好本地钥匙串）")
        return
    url = f"https://api.github.com/repos/{REPO}/contents/{remote}"

    # 1) 取旧 sha（已存在则更新，否则新建）
    r = subprocess.run(
        ["curl", "-s"] + proxy_args() + ["-H", f"Authorization: Bearer {tok}", url],
        capture_output=True, text=True
    ).stdout
    sha = None
    try:
        sha = json.loads(r).get("sha")
    except Exception:
        pass

    data = open(local, "rb").read()
    body = {
        "message": f"update {remote}",
        "content": base64.b64encode(data).decode(),
    }
    if sha:
        body["sha"] = sha

    # 2) PUT
    rr = subprocess.run(
        ["curl", "-s", "-L"] + proxy_args() +
        ["-X", "PUT",
         "-H", f"Authorization: Bearer {tok}",
         "-H", "Content-Type: application/json",
         "--data", json.dumps(body), url],
        capture_output=True, text=True
    ).stdout

    res = json.loads(rr)
    new_sha = res.get("content", {}).get("sha")
    if new_sha:
        print(f"[OK]   {remote} -> {new_sha}")
    else:
        print(f"[ERR]  {remote}: {str(res)[:200]}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2 or len(args) % 2 != 0:
        print("用法: put_life.py <本地文件> <远程路径> [<本地文件> <远程路径> ...]")
        sys.exit(1)
    for i in range(0, len(args), 2):
        put(args[i], args[i + 1])
