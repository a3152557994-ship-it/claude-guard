# ==============================================================================
# Claude Code — AWS Bedrock / Google Vertex AI 零封号一键部署脚本 (Windows PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "🛡️ Claude Code 企业级零封号通道一键部署向导 (Windows v1.2)" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------"

if ($env:ANTHROPIC_API_KEY -or $env:ANTHROPIC_BASE_URL) {
    Write-Host "⚠️ 检测到当前系统存在残留 ANTHROPIC_API_KEY / ANTHROPIC_BASE_URL，建议在系统环境变量中清理以防抢占优先级报错。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "请选择要配置的 0% 封号企业级云通道："
Write-Host "  [1] AWS Bedrock 企业直连模式（最稳推荐 · 按实际 Token 结算）"
Write-Host "  [2] Google Cloud Vertex AI 模式（可消耗 GCP $300 赠金）"
$mode = Read-Host "请输入数字 [1-2] (默认 1)"
if ([string]::IsNullOrWhiteSpace($mode)) { $mode = "1" }

$claudeDir = Join-Path $HOME ".claude"
if (!(Test-Path $claudeDir)) { New-Item -ItemType Directory -Path $claudeDir | Out-Null }
$settingsFile = Join-Path $claudeDir "settings.json"

if (Test-Path $settingsFile) {
    $stamp = Get-Date -Format "yyyyMMddHHmmss"
    Copy-Item $settingsFile "$settingsFile.bak.$stamp"
    Write-Host "✓ 已自动备份原配置至: $settingsFile.bak.$stamp" -ForegroundColor Green
}

if ($mode -eq "1") {
    $awsReg = Read-Host "请输入 AWS 区域 (默认 us-east-1)"
    if ([string]::IsNullOrWhiteSpace($awsReg)) { $awsReg = "us-east-1" }

    $cfg = @{
        env = @{
            CLAUDE_CODE_USE_BEDROCK = "1"
            AWS_REGION = $awsReg
            ANTHROPIC_MODEL = "us.anthropic.claude-sonnet-4-20250514-v1:0"
            ANTHROPIC_SMALL_FAST_MODEL = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
            DISABLE_TELEMETRY = "1"
            DISABLE_ERROR_REPORTING = "1"
            CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
        }
    }
    $cfg | ConvertTo-Json -Depth 4 | Set-Content -Path $settingsFile -Encoding UTF8
    Write-Host "✅ AWS Bedrock 零封号配置已写入 $settingsFile" -ForegroundColor Green
    Write-Host "👉 下一步：运行 aws configure 在本机填入 AccessKey，随后直接运行 claude 即可！"
} elseif ($mode -eq "2") {
    $gcpProj = Read-Host "请输入 Google Cloud Project ID (必填)"
    if ([string]::IsNullOrWhiteSpace($gcpProj)) { throw "Project ID 不能为空" }
    $gcpReg = Read-Host "请输入 Vertex 区域 (默认 us-east5)"
    if ([string]::IsNullOrWhiteSpace($gcpReg)) { $gcpReg = "us-east5" }

    $cfg = @{
        env = @{
            CLAUDE_CODE_USE_VERTEX = "1"
            CLOUD_ML_REGION = $gcpReg
            ANTHROPIC_VERTEX_PROJECT_ID = $gcpProj
            DISABLE_TELEMETRY = "1"
            DISABLE_ERROR_REPORTING = "1"
            CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
        }
    }
    $cfg | ConvertTo-Json -Depth 4 | Set-Content -Path $settingsFile -Encoding UTF8
    Write-Host "✅ Google Vertex AI 零封号配置已写入 $settingsFile" -ForegroundColor Green
    Write-Host "👉 下一步：运行 gcloud auth application-default login 授权后直接启动 claude 即可！"
}
