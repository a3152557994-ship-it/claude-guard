#!/usr/bin/env bash
# ==============================================================================
# Claude Guard — Claude Code 5 源秒切与防遥测加固工具 (macOS / Linux)
# 自动备份并切换 ~/.claude/settings.json，解决封号、遥测泄露与 5 小时限流断活问题
# ==============================================================================
set -euo pipefail

CLAUDE_DIR="${HOME}/.claude"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
BACKUP_FILE="${CLAUDE_DIR}/settings.backup.$(date +%Y%m%d-%H%M%S).json"

mkdir -p "${CLAUDE_DIR}"

echo "================================================================"
echo "🛡️  Claude Guard — Claude Code 防断流多源一键切换器 (v1.0.0)"
echo "================================================================"
echo "当前配置文件路径: ${SETTINGS_FILE}"
echo ""
echo "请选择要激活的工作源模式："
echo "  [1] 🛡️ 官方账号 · 隐私防遥测加固模式 (屏蔽 Statsig/非必要流量)"
echo "  [2] 🔥 AWS Bedrock · 企业级 100% 永不封号直连模式"
echo "  [3] ☁️  Google Cloud Vertex AI · 企业级零封号模式 (可消耗 GCP 赠金)"
echo "  [4] ⚡ OpenRouter / 合规聚合网关 · 5小时限流无缝热备模式"
echo "  [5] 🔄 国产高性价比兼容源 · 应急兜底模式 (DeepSeek / GLM Anthropic 兼容接口)"
echo "================================================================"
read -rp "请输入模式编号 [1-5] (默认 1): " MODE_CHOICE
MODE_CHOICE="${MODE_CHOICE:-1}"

if [[ -f "${SETTINGS_FILE}" ]]; then
  cp "${SETTINGS_FILE}" "${BACKUP_FILE}"
  echo "📦 已自动备份原配置至: ${BACKUP_FILE}"
fi

case "${MODE_CHOICE}" in
  1)
    cat > "${SETTINGS_FILE}" <<'EOF'
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
EOF
    echo "✅ 已切换至 [模式 1: 官方账号 · 隐私防遥测加固模式]"
    ;;
  2)
    read -rp "请输入 AWS 区域 (默认 us-east-1): " AWS_REG
    AWS_REG="${AWS_REG:-us-east-1}"
    cat > "${SETTINGS_FILE}" <<EOF
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "${AWS_REG}",
    "ANTHROPIC_MODEL": "us.anthropic.claude-sonnet-4-20250514-v1:0"
  }
}
EOF
    echo "✅ 已切换至 [模式 2: AWS Bedrock 企业级零封号模式 (${AWS_REG})]"
    ;;
  3)
    read -rp "请输入 GCP Project ID: " GCP_PROJ
    GCP_PROJ="${GCP_PROJ:-your-gcp-project-id}"
    read -rp "请输入 Vertex 区域 (默认 us-east5): " GCP_REG
    GCP_REG="${GCP_REG:-us-east5}"
    cat > "${SETTINGS_FILE}" <<EOF
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_USE_VERTEX": "1",
    "CLOUD_ML_REGION": "${GCP_REG}",
    "ANTHROPIC_VERTEX_PROJECT_ID": "${GCP_PROJ}"
  }
}
EOF
    echo "✅ 已切换至 [模式 3: Google Vertex AI 企业级零封号模式 (${GCP_PROJ})]"
    ;;
  4)
    read -rp "请输入聚合网关 Base URL (默认 https://openrouter.ai/api/v1): " BASE_URL
    BASE_URL="${BASE_URL:-https://openrouter.ai/api/v1}"
    read -rp "请输入 API Key / Token: " API_TOKEN
    API_TOKEN="${API_TOKEN:-sk-or-v1-your-key}"
    cat > "${SETTINGS_FILE}" <<EOF
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "ANTHROPIC_BASE_URL": "${BASE_URL}",
    "ANTHROPIC_AUTH_TOKEN": "${API_TOKEN}"
  }
}
EOF
    echo "✅ 已切换至 [模式 4: OpenRouter / 聚合网关热备模式]"
    ;;
  5)
    read -rp "请输入兼容接口地址 (默认 https://api.deepseek.com/anthropic): " DOM_URL
    DOM_URL="${DOM_URL:-https://api.deepseek.com/anthropic}"
    read -rp "请输入对应 API Key: " DOM_KEY
    DOM_KEY="${DOM_KEY:-sk-your-key}"
    cat > "${SETTINGS_FILE}" <<EOF
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "ANTHROPIC_BASE_URL": "${DOM_URL}",
    "ANTHROPIC_AUTH_TOKEN": "${DOM_KEY}",
    "ANTHROPIC_MODEL": "deepseek-chat"
  }
}
EOF
    echo "✅ 已切换至 [模式 5: 国产兼容源应急兜底模式]"
    ;;
  *)
    echo "❌ 无效选项，未修改配置。"
    exit 1
    ;;
esac

echo "🎉 配置已写入 ${SETTINGS_FILE}，现在可直接运行 claude 启动！"
