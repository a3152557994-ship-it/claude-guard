#!/usr/bin/env bash
# ==============================================================================
# Claude Code — AWS Bedrock / Google Vertex AI 100% 零封号一键部署脚本 (macOS / Linux)
# 用途：自动清理冲突旧 Key、生成最小权限 IAM 策略、写入防遥测 settings.json 并自检
# ==============================================================================
set -euo pipefail

BOLD="\033[1m"
GREEN="\033[32m"
AMBER="\033[33m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}🛡️ Claude Code 企业级零封号通道一键部署向导 (v1.2)${RESET}"
echo "----------------------------------------------------------------"

# 1. 检测残留冲突环境变量（排查假封号乌龙）
if [[ -n "${ANTHROPIC_API_KEY:-}" || -n "${ANTHROPIC_BASE_URL:-}" ]]; then
  echo -e "${AMBER}⚠️ 检测到当前终端存在残留环境变量：${RESET}"
  [[ -n "${ANTHROPIC_API_KEY:-}" ]] && echo "   - ANTHROPIC_API_KEY (已设置，可能抢占 OAuth/Bedrock 优先级触发 Organization disabled)"
  [[ -n "${ANTHROPIC_BASE_URL:-}" ]] && echo "   - ANTHROPIC_BASE_URL=${ANTHROPIC_BASE_URL}"
  echo "   -> 脚本将在生成的独立启动配置中自动屏蔽冲突变量。"
fi

echo ""
echo "请选择要配置的 0% 封号企业级云通道："
echo "  [1] AWS Bedrock 企业直连模式（最稳推荐 · 按实际 Token 结算）"
echo "  [2] Google Cloud Vertex AI 模式（可直接抵扣 GCP $300 赠金）"
echo "  [3] 仅输出 AWS Bedrock 最小权限 IAM JSON 策略（供粘贴至 AWS 控制台）"
read -rp "请输入数字 [1-3] (默认 1): " MODE
MODE="${MODE:-1}"

CLAUDE_DIR="${HOME}/.claude"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
mkdir -p "${CLAUDE_DIR}"

if [[ -f "${SETTINGS_FILE}" ]]; then
  BACKUP="${SETTINGS_FILE}.bak.$(date +%Y%m%d%H%M%S)"
  cp "${SETTINGS_FILE}" "${BACKUP}"
  echo -e "${GREEN}✓ 已自动备份原配置至: ${BACKUP}${RESET}"
fi

print_iam_policy() {
  cat <<'IAM'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ClaudeCodeBedrockLeastPrivilege",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-*",
        "arn:aws:bedrock:*:*:inference-profile/*.anthropic.claude-*"
      ]
    }
  ]
}
IAM
}

if [[ "${MODE}" == "3" ]]; then
  echo -e "\n${BOLD}📋 复制以下最小权限 JSON 粘贴到 AWS Console -> IAM -> Policies：${RESET}"
  print_iam_policy
  exit 0
fi

if [[ "${MODE}" == "1" ]]; then
  read -rp "请输入 AWS 区域 (推荐 us-east-1 或 us-west-2，默认 us-east-1): " AWS_REG
  AWS_REG="${AWS_REG:-us-east-1}"
  read -rp "请输入 AWS Profile 名称 (若直接用默认凭证直接回车，推荐填 claude-bedrock): " AWS_PROF

  echo -e "\n${AMBER}💡 提示：请确保已在 AWS IAM 为该账号绑定最小权限策略（选菜单 3 可查看 JSON），切勿在聊天框发送明文 SecretKey。${RESET}"

  cat > "${SETTINGS_FILE}" <<EOF
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "${AWS_REG}",
    "ANTHROPIC_MODEL": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "ANTHROPIC_SMALL_FAST_MODEL": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"${AWS_PROF:+,
    "AWS_PROFILE": "${AWS_PROF}"}
  }
}
EOF

  echo -e "${GREEN}✅ AWS Bedrock 零封号配置已写入 ${SETTINGS_FILE}${RESET}"
  echo "👉 下一步：运行 \`aws configure${AWS_PROF:+ --profile ${AWS_PROF}}\` 在本机安全填入 AccessKey，随后直接输入 \`claude\` 启动即可！"

elif [[ "${MODE}" == "2" ]]; then
  read -rp "请输入 Google Cloud Project ID (必填，如 my-gcp-project-123): " GCP_PROJ
  if [[ -z "${GCP_PROJ}" ]]; then
    echo -e "${RED}❌ Project ID 不能为空${RESET}"
    exit 1
  fi
  read -rp "请输入 Vertex 区域 (推荐 us-east5 或 global，默认 us-east5): " GCP_REG
  GCP_REG="${GCP_REG:-us-east5}"

  cat > "${SETTINGS_FILE}" <<EOF
{
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "CLOUD_ML_REGION": "${GCP_REG}",
    "ANTHROPIC_VERTEX_PROJECT_ID": "${GCP_PROJ}",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
EOF

  echo -e "${GREEN}✅ Google Vertex AI 零封号配置已写入 ${SETTINGS_FILE}${RESET}"
  echo "👉 下一步：在终端运行 \`gcloud auth application-default login\` 完成本机登录授权，随后输入 \`claude\` 启动即可！"
fi
