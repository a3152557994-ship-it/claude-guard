#!/usr/bin/env bash
# ==============================================================================
# Claude Guard 1-Line Installer & Instant Environment Doctor
# Usage: curl -fsSL https://a3152557994-ship-it.github.io/claude-guard/install.sh | bash
# ==============================================================================
set -euo pipefail

INSTALL_DIR="${HOME}/.claude-guard"
mkdir -p "${INSTALL_DIR}"

echo "🛡️  正在下载 Claude Guard 本地防封体检与 5 源切换工具包..."
curl -fsSL "https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-code-kit.zip" -o "${INSTALL_DIR}/claude-code-kit.zip"
unzip -qo "${INSTALL_DIR}/claude-code-kit.zip" -d "${INSTALL_DIR}"
chmod +x "${INSTALL_DIR}/cc-switch.sh" "${INSTALL_DIR}/env-doctor.mjs"

echo ""
if command -v node >/dev/null 2>&1; then
  node "${INSTALL_DIR}/env-doctor.mjs"
else
  echo "✅ 已解压至 ${INSTALL_DIR}"
fi

echo ""
echo "🚀 快速使用指令："
echo "  • 一键切换 Claude Code 源 (官方加固 / Bedrock / Vertex / OpenRouter)："
echo "    ${INSTALL_DIR}/cc-switch.sh"
echo "  • 在线 10 秒检测 IP ASN 机房属性与 WebRTC 穿透："
echo "    https://a3152557994-ship-it.github.io/claude-guard/"
