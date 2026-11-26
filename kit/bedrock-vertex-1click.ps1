# ==============================================================================
# Claude Code — AWS Bedrock / Google Vertex AI 零封号一键无损部署脚本 (Windows PowerShell v2.0)
# 核心特性：JSON 非破坏性深合并，100% 保留用户原有的 mcpServers / permissions / hooks！
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "🛡️ Claude Code 企业级零封号通道一键无损部署向导 (Windows v2.0)" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------"

if ($env:ANTHROPIC_API_KEY -or $env:ANTHROPIC_BASE_URL) {
    Write-Host "⚠️ 检测到当前系统存在残留 ANTHROPIC_API_KEY / ANTHROPIC_BASE_URL，建议在系统环境变量中清理以防抢占优先级报错。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "请选择要配置的 0% 封号企业级云通道："
Write-Host "  [1] AWS Bedrock 企业直连模式（最稳推荐 · 默认 Claude Sonnet 4.6 跨区推理）"
Write-Host "  [2] Google Cloud Vertex AI 模式（可消耗 GCP `$300 赠金）"
$mode = Read-Host "请输入数字 [1-2] (默认 1)"
if ([string]::IsNullOrWhiteSpace($mode)) { $mode = "1" }

$claudeDir = Join-Path $HOME ".claude"
if (!(Test-Path $claudeDir)) { New-Item -ItemType Directory -Path $claudeDir | Out-Null }
$settingsFile = Join-Path $claudeDir "settings.json"

$patch = @{
    DISABLE_TELEMETRY = "1"
    DISABLE_ERROR_REPORTING = "1"
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
}

if ($mode -eq "1") {
    $awsReg = Read-Host "请输入 AWS 区域 (默认 us-east-1)"
    if ([string]::IsNullOrWhiteSpace($awsReg)) { $awsReg = "us-east-1" }
    $patch["CLAUDE_CODE_USE_BEDROCK"] = "1"
    $patch["AWS_REGION"] = $awsReg
    $patch["ANTHROPIC_MODEL"] = "us.anthropic.claude-sonnet-4-6"
    $patch["ANTHROPIC_SMALL_FAST_MODEL"] = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
} elseif ($mode -eq "2") {
    $gcpProj = Read-Host "请输入 Google Cloud Project ID (必填)"
    if ([string]::IsNullOrWhiteSpace($gcpProj)) { throw "Project ID 不能为空" }
    $gcpReg = Read-Host "请输入 Vertex 区域 (默认 us-east5)"
    if ([string]::IsNullOrWhiteSpace($gcpReg)) { $gcpReg = "us-east5" }
    $patch["CLAUDE_CODE_USE_VERTEX"] = "1"
    $patch["CLOUD_ML_REGION"] = $gcpReg
    $patch["ANTHROPIC_VERTEX_PROJECT_ID"] = $gcpProj
    $patch["ANTHROPIC_MODEL"] = "claude-sonnet-4-6"
} else {
    throw "无效选项"
}

if (Test-Path $settingsFile) {
    $stamp = Get-Date -Format "yyyyMMddHHmmss"
    Copy-Item $settingsFile "$settingsFile.bak.$stamp"
    Write-Host "✓ 已自动备份原配置至: $settingsFile.bak.$stamp" -ForegroundColor Green
}

$env:CG_SETTINGS_FILE = $settingsFile
$env:CG_PATCH_JSON = ($patch | ConvertTo-Json -Compress)
node -e '
  const fs = require("fs");
  const file = process.env.CG_SETTINGS_FILE;
  const patch = JSON.parse(process.env.CG_PATCH_JSON);
  let cfg = {};
  if (fs.existsSync(file)) {
    const raw = fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "").trim();
    if (raw) cfg = JSON.parse(raw);
  }
  if (!cfg || typeof cfg !== "object" || Array.isArray(cfg)) cfg = {};
  const env = (cfg.env && typeof cfg.env === "object" && !Array.isArray(cfg.env)) ? { ...cfg.env } : {};
  for (const k of [
    "CLAUDE_CODE_USE_BEDROCK", "AWS_REGION", "AWS_PROFILE",
    "CLAUDE_CODE_USE_VERTEX", "CLOUD_ML_REGION", "ANTHROPIC_VERTEX_PROJECT_ID",
    "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL", "ANTHROPIC_SMALL_FAST_MODEL"
  ]) delete env[k];
  Object.assign(env, patch);
  cfg.env = env;
  fs.writeFileSync(file, JSON.stringify(cfg, null, 2) + "\n", "utf8");
'
Remove-Item Env:CG_SETTINGS_FILE -ErrorAction SilentlyContinue
Remove-Item Env:CG_PATCH_JSON -ErrorAction SilentlyContinue

if ($mode -eq "1") {
    Write-Host "✅ AWS Bedrock 零封号配置已无损合并写入 $settingsFile" -ForegroundColor Green
    Write-Host "👉 下一步：运行 aws configure 在本机填入 AccessKey，随后直接运行 claude 即可！"
} else {
    Write-Host "✅ Google Vertex AI 零封号配置已无损合并写入 $settingsFile" -ForegroundColor Green
    Write-Host "👉 下一步：运行 gcloud auth application-default login 授权后直接启动 claude 即可！"
}
