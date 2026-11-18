# ==============================================================================
# Claude Guard — Claude Code 5 源秒切与防遥测加固工具 (Windows PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

$ClaudeDir = Join-Path $HOME ".claude"
$SettingsFile = Join-Path $ClaudeDir "settings.json"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupFile = Join-Path $ClaudeDir "settings.backup.$Stamp.json"

if (-not (Test-Path $ClaudeDir)) {
  New-Item -ItemType Directory -Path $ClaudeDir | Out-Null
}

Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "🛡️  Claude Guard — Claude Code 防断流多源切换器 (Windows 版)" -ForegroundColor Yellow
Write-Host "================================================================"
Write-Host "  [1] 官方账号 · 隐私防遥测加固模式 (屏蔽 Statsig/非必要流量)"
Write-Host "  [2] AWS Bedrock · 企业级 100% 永不封号直连模式"
Write-Host "  [3] Google Cloud Vertex AI · 企业级零封号模式"
Write-Host "  [4] OpenRouter / 聚合网关 · 5小时限流无缝热备模式"
Write-Host "  [5] 国产兼容源 · 应急兜底模式 (DeepSeek / GLM)"

$Choice = Read-Host "请输入模式编号 [1-5] (默认 1)"
if ([string]::IsNullOrWhiteSpace($Choice)) { $Choice = "1" }

if (Test-Path $SettingsFile) {
  Copy-Item $SettingsFile $BackupFile
  Write-Host "📦 已备份原配置至: $BackupFile" -ForegroundColor Cyan
}

$EnvMap = @{
  "DISABLE_TELEMETRY" = "1"
  "DISABLE_ERROR_REPORTING" = "1"
  "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC" = "1"
}

if ($Choice -eq "2") {
  $Reg = Read-Host "请输入 AWS 区域 (默认 us-east-1)"
  if ([string]::IsNullOrWhiteSpace($Reg)) { $Reg = "us-east-1" }
  $EnvMap["CLAUDE_CODE_USE_BEDROCK"] = "1"
  $EnvMap["AWS_REGION"] = $Reg
  $EnvMap["ANTHROPIC_MODEL"] = "us.anthropic.claude-sonnet-4-20250514-v1:0"
} elseif ($Choice -eq "3") {
  $Proj = Read-Host "请输入 GCP Project ID"
  if ([string]::IsNullOrWhiteSpace($Proj)) { $Proj = "your-gcp-project-id" }
  $EnvMap["CLAUDE_CODE_USE_VERTEX"] = "1"
  $EnvMap["CLOUD_ML_REGION"] = "us-east5"
  $EnvMap["ANTHROPIC_VERTEX_PROJECT_ID"] = $Proj
} elseif ($Choice -eq "4") {
  $Url = Read-Host "请输入网关 Base URL (默认 https://openrouter.ai/api/v1)"
  if ([string]::IsNullOrWhiteSpace($Url)) { $Url = "https://openrouter.ai/api/v1" }
  $Key = Read-Host "请输入 API Key"
  $EnvMap["ANTHROPIC_BASE_URL"] = $Url
  $EnvMap["ANTHROPIC_AUTH_TOKEN"] = $Key
} elseif ($Choice -eq "5") {
  $Url = Read-Host "请输入兼容接口地址 (默认 https://api.deepseek.com/anthropic)"
  if ([string]::IsNullOrWhiteSpace($Url)) { $Url = "https://api.deepseek.com/anthropic" }
  $Key = Read-Host "请输入对应 API Key"
  $EnvMap["ANTHROPIC_BASE_URL"] = $Url
  $EnvMap["ANTHROPIC_AUTH_TOKEN"] = $Key
  $EnvMap["ANTHROPIC_MODEL"] = "deepseek-chat"
}

$OutObj = @{ env = $EnvMap }
$Json = $OutObj | ConvertTo-Json -Depth 5
Set-Content -Path $SettingsFile -Value $Json -Encoding UTF8
Write-Host "✅ 配置已成功写入 $SettingsFile ！" -ForegroundColor Green
