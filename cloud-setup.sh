#!/usr/bin/env bash
# WorkBuddy 云端沙箱技能拉起脚本
# 用法：bash cloud-setup.sh  （在 workbuddy-skills 仓库根目录执行，或直接粘贴运行）
set -e

SKILL_DIR="/root/.codebuddy/skills"
PROXY_URL="https://gh-proxy.com/https://github.com/Gordon9999/workbuddy-skills.git"
TMP=$(mktemp -d)

echo "[1/3] clone 仓库（走加速站）..."
git clone --depth 1 "$PROXY_URL" "$TMP/wbs"

echo "[2/3] 拷贝 skills ..."
cp -r "$TMP/wbs/skills/"*/ "$SKILL_DIR/"

echo "[3/3] 安装结果："
ls -la "$SKILL_DIR/"

rm -rf "$TMP"
echo "完成。新会话说「拉 skill」即可重跑本脚本。"
