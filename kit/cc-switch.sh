#!/usr/bin/env bash
# ==============================================================================
# Claude Guard — Claude Code 5 源秒切与防遥测加固工具 (macOS / Linux v2.0)
# 核心特性：JSON 非破坏性深合并 —— 仅更新 env 路由键，100% 保留用户原有的
#           mcpServers、permissions、hooks、statusLine 等全部自定义配置！
# ==============================================================================
set -euo pipefail

CLAUDE_DIR="${HOME}/.claude"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
BACKUP_FILE="${CLAUDE_DIR}/settings.backup.$(date +%Y%m%d-%H%M%S).json"

mkdir -p "${CLAUDE_DIR}"

echo "================================================================"
echo "🛡️  Claude Guard — Claude Code 防断流多源无损切换器 (v2.0.0)"
echo "================================================================"
echo "当前配置文件路径: ${SETTINGS_FILE}"
echo "安全承诺: 非破坏性 JSON 深合并，100% 保留 mcpServers / permissions / hooks"
echo ""
echo "请选择要激活的工作源模式："
echo "  [1] 🛡️ 官方账号 · 隐私防遥测加固模式 (屏蔽 Statsig/非必要流量)"
echo "  [2] 🔥 AWS Bedrock · 企业级 100% 永不封号直连模式 (Claude Sonnet 4.6)"
echo "  [3] ☁️  Google Cloud Vertex AI · 企业级零封号模式 (可抵扣 GCP 赠金)"
echo "  [4] ⚡ OpenRouter / 合规聚合网关 · 5小时限流无缝热备模式"
echo "  [5] 🔄 国产高性价比兼容源 · 应急兜底模式 (DeepSeek / GLM Anthropic 兼容接口)"
echo "================================================================"
read -rp "请输入模式编号 [1-5] (默认 1): " MODE_CHOICE
MODE_CHOICE="${MODE_CHOICE:-1}"

AWS_REG=""
AWS_PROF=""
GCP_PROJ=""
GCP_REG=""
BASE_URL=""
API_TOKEN=""
DOM_URL=""
DOM_KEY=""

case "${MODE_CHOICE}" in
  1)
    MODE_DESC="模式 1: 官方账号 · 隐私防遥测加固模式"
    ;;
  2)
    read -rp "请输入 AWS 区域 (默认 us-east-1): " AWS_REG
    AWS_REG="${AWS_REG:-us-east-1}"
    read -rp "请输入 AWS Profile (默认留空使用默认凭证): " AWS_PROF
    MODE_DESC="模式 2: AWS Bedrock 企业级零封号模式 (${AWS_REG})"
    ;;
  3)
    read -rp "请输入 GCP Project ID: " GCP_PROJ
    GCP_PROJ="${GCP_PROJ:-your-gcp-project-id}"
    read -rp "请输入 Vertex 区域 (默认 us-east5): " GCP_REG
    GCP_REG="${GCP_REG:-us-east5}"
    MODE_DESC="模式 3: Google Vertex AI 企业级零封号模式 (${GCP_PROJ})"
    ;;
  4)
    read -rp "请输入聚合网关 Base URL (默认 https://openrouter.ai/api/v1): " BASE_URL
    BASE_URL="${BASE_URL:-https://openrouter.ai/api/v1}"
    read -rp "请输入 API Key / Token: " API_TOKEN
    API_TOKEN="${API_TOKEN:-sk-or-v1-your-key}"
    MODE_DESC="模式 4: OpenRouter / 聚合网关热备模式"
    ;;
  5)
    read -rp "请输入兼容接口地址 (默认 https://api.deepseek.com/anthropic): " DOM_URL
    DOM_URL="${DOM_URL:-https://api.deepseek.com/anthropic}"
    read -rp "请输入对应 API Key: " DOM_KEY
    DOM_KEY="${DOM_KEY:-sk-your-key}"
    MODE_DESC="模式 5: 国产兼容源应急兜底模式"
    ;;
  *)
    echo "❌ 无效选项，未修改配置。"
    exit 1
    ;;
esac

if [[ -f "${SETTINGS_FILE}" ]]; then
  cp "${SETTINGS_FILE}" "${BACKUP_FILE}"
  echo "📦 已自动备份原配置至: ${BACKUP_FILE}"
fi

export SETTINGS_FILE MODE_CHOICE AWS_REG AWS_PROF GCP_PROJ GCP_REG BASE_URL API_TOKEN DOM_URL DOM_KEY

if command -v node >/dev/null 2>&1; then
  node -e '
    const fs = require("fs");
    const file = process.env.SETTINGS_FILE;
    let cfg = {};
    if (fs.existsSync(file)) {
      const raw = fs.readFileSync(file, "utf8").trim();
      if (raw) {
        try {
          cfg = JSON.parse(raw);
        } catch (err) {
          console.error("❌ 原 settings.json 存在语法错误，已中止写入以保护原文件:", err.message);
          process.exit(2);
        }
      }
    }
    if (!cfg || typeof cfg !== "object" || Array.isArray(cfg)) cfg = {};
    const prevEnv = (cfg.env && typeof cfg.env === "object" && !Array.isArray(cfg.env)) ? { ...cfg.env } : {};

    // 仅清理本工具托管的通道切换键，100% 保留用户自定义 env 变量及顶层 mcpServers/permissions/hooks
    const managedKeys = [
      "CLAUDE_CODE_USE_BEDROCK", "AWS_REGION", "AWS_PROFILE",
      "CLAUDE_CODE_USE_VERTEX", "CLOUD_ML_REGION", "ANTHROPIC_VERTEX_PROJECT_ID",
      "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY",
      "ANTHROPIC_MODEL", "ANTHROPIC_SMALL_FAST_MODEL"
    ];
    for (const k of managedKeys) delete prevEnv[k];

    prevEnv.DISABLE_TELEMETRY = "1";
    prevEnv.DISABLE_ERROR_REPORTING = "1";
    prevEnv.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1";

    const m = process.env.MODE_CHOICE;
    if (m === "2") {
      prevEnv.CLAUDE_CODE_USE_BEDROCK = "1";
      prevEnv.AWS_REGION = process.env.AWS_REG;
      prevEnv.ANTHROPIC_MODEL = "us.anthropic.claude-sonnet-4-6";
      prevEnv.ANTHROPIC_SMALL_FAST_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0";
      if (process.env.AWS_PROF) prevEnv.AWS_PROFILE = process.env.AWS_PROF;
    } else if (m === "3") {
      prevEnv.CLAUDE_CODE_USE_VERTEX = "1";
      prevEnv.CLOUD_ML_REGION = process.env.GCP_REG;
      prevEnv.ANTHROPIC_VERTEX_PROJECT_ID = process.env.GCP_PROJ;
      prevEnv.ANTHROPIC_MODEL = "claude-sonnet-4-6";
    } else if (m === "4") {
      prevEnv.ANTHROPIC_BASE_URL = process.env.BASE_URL;
      prevEnv.ANTHROPIC_AUTH_TOKEN = process.env.API_TOKEN;
      prevEnv.ANTHROPIC_MODEL = "anthropic/claude-sonnet-4.6";
    } else if (m === "5") {
      prevEnv.ANTHROPIC_BASE_URL = process.env.DOM_URL;
      prevEnv.ANTHROPIC_AUTH_TOKEN = process.env.DOM_KEY;
      prevEnv.ANTHROPIC_MODEL = "deepseek-chat";
    }

    cfg.env = prevEnv;
    fs.writeFileSync(file, JSON.stringify(cfg, null, 2) + "\n", "utf8");
  '
elif command -v python3 >/dev/null 2>&1; then
  python3 -c '
import json, os, sys
p = os.environ["SETTINGS_FILE"]
cfg = {}
if os.path.exists(p):
    raw = open(p, "r", encoding="utf-8").read().strip()
    if raw:
        try:
            cfg = json.loads(raw)
        except Exception as e:
            sys.stderr.write(f"❌ 原 settings.json 存在语法错误，已中止写入: {e}\n")
            sys.exit(2)
if not isinstance(cfg, dict):
    cfg = {}
env = dict(cfg.get("env")) if isinstance(cfg.get("env"), dict) else {}
for k in [
    "CLAUDE_CODE_USE_BEDROCK", "AWS_REGION", "AWS_PROFILE",
    "CLAUDE_CODE_USE_VERTEX", "CLOUD_ML_REGION", "ANTHROPIC_VERTEX_PROJECT_ID",
    "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL", "ANTHROPIC_SMALL_FAST_MODEL",
]:
    env.pop(k, None)
env.update({
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
})
m = os.environ["MODE_CHOICE"]
if m == "2":
    env["CLAUDE_CODE_USE_BEDROCK"] = "1"
    env["AWS_REGION"] = os.environ["AWS_REG"]
    env["ANTHROPIC_MODEL"] = "us.anthropic.claude-sonnet-4-6"
    env["ANTHROPIC_SMALL_FAST_MODEL"] = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    if os.environ.get("AWS_PROF"):
        env["AWS_PROFILE"] = os.environ["AWS_PROF"]
elif m == "3":
    env["CLAUDE_CODE_USE_VERTEX"] = "1"
    env["CLOUD_ML_REGION"] = os.environ["GCP_REG"]
    env["ANTHROPIC_VERTEX_PROJECT_ID"] = os.environ["GCP_PROJ"]
    env["ANTHROPIC_MODEL"] = "claude-sonnet-4-6"
elif m == "4":
    env["ANTHROPIC_BASE_URL"] = os.environ["BASE_URL"]
    env["ANTHROPIC_AUTH_TOKEN"] = os.environ["API_TOKEN"]
    env["ANTHROPIC_MODEL"] = "anthropic/claude-sonnet-4.6"
elif m == "5":
    env["ANTHROPIC_BASE_URL"] = os.environ["DOM_URL"]
    env["ANTHROPIC_AUTH_TOKEN"] = os.environ["DOM_KEY"]
    env["ANTHROPIC_MODEL"] = "deepseek-chat"
cfg["env"] = env
with open(p, "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
    f.write("\n")
'
else
  echo "❌ 未检测到 node 或 python3，无法安全合并 JSON 配置。"
  exit 1
fi

echo "✅ 已无损合并切换至 [${MODE_DESC}]（原有 mcpServers / permissions / hooks 完整保留）"
echo "🎉 配置已更新至 ${SETTINGS_FILE}，现在可直接运行 claude 启动！"
