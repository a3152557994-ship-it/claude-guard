# ==============================================================================
# Claude Guard — Claude Code 5 源秒切与防遥测加固工具 (Windows PowerShell v2.0)
# 核心特性：JSON 非破坏性深合并 —— 仅更新 env 路由键，100% 保留用户原有的
#           mcpServers、permissions、hooks、statusLine 等全部自定义配置！
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
Write-Host "🛡️  Claude Guard — Claude Code 防断流多源无损切换器 (Windows v2.0)" -ForegroundColor Yellow
Write-Host "================================================================"
Write-Host "安全承诺: 非破坏性 JSON 深合并，100% 保留 mcpServers / permissions / hooks"
Write-Host "  [1] 官方账号 · 隐私防遥测加固模式 (屏蔽 Statsig/非必要流量)"
Write-Host "  [2] AWS Bedrock · 企业级 100% 永不封号直连模式 (Claude Sonnet 4.6)"
Write-Host "  [3] Google Cloud Vertex AI · 企业级零封号模式 (可抵扣 GCP 赠金)"
Write-Host "  [4] OpenRouter / 聚合网关 · 5小时限流无缝热备模式"
Write-Host "  [5] 国产兼容源 · 应急兜底模式 (DeepSeek / GLM)"

$Choice = Read-Host "请输入模式编号 [1-5] (默认 1)"
if ([string]::IsNullOrWhiteSpace($Choice)) { $Choice = "1" }
if ($Choice -notin @("1", "2", "3", "4", "5")) {
  Write-Host "❌ 无效选项，未修改配置。" -ForegroundColor Red
  exit 1
}

$EnvPatch = @{
  "DISABLE_TELEMETRY" = "1"
  "DISABLE_ERROR_REPORTING" = "1"
  "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC" = "1"
}

if ($Choice -eq "2") {
  $Reg = Read-Host "请输入 AWS 区域 (默认 us-east-1)"
  if ([string]::IsNullOrWhiteSpace($Reg)) { $Reg = "us-east-1" }
  $Prof = Read-Host "请输入 AWS Profile (默认留空使用默认凭证)"
  $EnvPatch["CLAUDE_CODE_USE_BEDROCK"] = "1"
  $EnvPatch["AWS_REGION"] = $Reg
  $EnvPatch["ANTHROPIC_MODEL"] = "us.anthropic.claude-sonnet-4-6"
  $EnvPatch["ANTHROPIC_SMALL_FAST_MODEL"] = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
  if (-not [string]::IsNullOrWhiteSpace($Prof)) { $EnvPatch["AWS_PROFILE"] = $Prof }
} elseif ($Choice -eq "3") {
  $Proj = Read-Host "请输入 GCP Project ID"
  if ([string]::IsNullOrWhiteSpace($Proj)) { $Proj = "your-gcp-project-id" }
  $GcpReg = Read-Host "请输入 Vertex 区域 (默认 us-east5)"
  if ([string]::IsNullOrWhiteSpace($GcpReg)) { $GcpReg = "us-east5" }
  $EnvPatch["CLAUDE_CODE_USE_VERTEX"] = "1"
  $EnvPatch["CLOUD_ML_REGION"] = $GcpReg
  $EnvPatch["ANTHROPIC_VERTEX_PROJECT_ID"] = $Proj
  $EnvPatch["ANTHROPIC_MODEL"] = "claude-sonnet-4-6"
} elseif ($Choice -eq "4") {
  $Url = Read-Host "请输入网关 Base URL (默认 https://openrouter.ai/api/v1)"
  if ([string]::IsNullOrWhiteSpace($Url)) { $Url = "https://openrouter.ai/api/v1" }
  $Key = Read-Host "请输入 API Key"
  if ([string]::IsNullOrWhiteSpace($Key)) { $Key = "sk-or-v1-your-key" }
  $EnvPatch["ANTHROPIC_BASE_URL"] = $Url
  $EnvPatch["ANTHROPIC_AUTH_TOKEN"] = $Key
  $EnvPatch["ANTHROPIC_MODEL"] = "anthropic/claude-sonnet-4.6"
} elseif ($Choice -eq "5") {
  $Url = Read-Host "请输入兼容接口地址 (默认 https://api.deepseek.com/anthropic)"
  if ([string]::IsNullOrWhiteSpace($Url)) { $Url = "https://api.deepseek.com/anthropic" }
  $Key = Read-Host "请输入对应 API Key"
  if ([string]::IsNullOrWhiteSpace($Key)) { $Key = "sk-your-key" }
  $EnvPatch["ANTHROPIC_BASE_URL"] = $Url
  $EnvPatch["ANTHROPIC_AUTH_TOKEN"] = $Key
  $EnvPatch["ANTHROPIC_MODEL"] = "deepseek-chat"
}

if (Test-Path $SettingsFile) {
  Copy-Item $SettingsFile $BackupFile
  Write-Host "📦 已自动备份原配置至: $BackupFile" -ForegroundColor Cyan
}

$env:CG_SETTINGS_FILE = $SettingsFile
$env:CG_ENV_PATCH_JSON = ($EnvPatch | ConvertTo-Json -Compress)

if (Get-Command node -ErrorAction SilentlyContinue) {
  node -e '
    const fs = require("fs");
    const file = process.env.CG_SETTINGS_FILE;
    const patch = JSON.parse(process.env.CG_ENV_PATCH_JSON);
    let cfg = {};
    if (fs.existsSync(file)) {
      const raw = fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "").trim();
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
    const nextEnv = (cfg.env && typeof cfg.env === "object" && !Array.isArray(cfg.env)) ? { ...cfg.env } : {};
    const managedKeys = [
      "CLAUDE_CODE_USE_BEDROCK", "AWS_REGION", "AWS_PROFILE",
      "CLAUDE_CODE_USE_VERTEX", "CLOUD_ML_REGION", "ANTHROPIC_VERTEX_PROJECT_ID",
      "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY",
      "ANTHROPIC_MODEL", "ANTHROPIC_SMALL_FAST_MODEL"
    ];
    for (const k of managedKeys) delete nextEnv[k];
    Object.assign(nextEnv, patch);
    cfg.env = nextEnv;
    fs.writeFileSync(file, JSON.stringify(cfg, null, 2) + "\n", "utf8");
  '
  if ($LASTEXITCODE -ne 0) { throw "JSON 非破坏性合并失败，原配置未改动。" }
} else {
  $CfgObj = [ordered]@{}
  if (Test-Path $SettingsFile) {
    $Raw = (Get-Content -Path $SettingsFile -Raw -Encoding UTF8)
    if (-not [string]::IsNullOrWhiteSpace($Raw)) {
      $Parsed = $Raw | ConvertFrom-Json
      foreach ($p in $Parsed.PSObject.Properties) { $CfgObj[$p.Name] = $p.Value }
    }
  }
  $NextEnv = [ordered]@{}
  if ($CfgObj.Contains("env") -and $null -ne $CfgObj["env"]) {
    foreach ($ep in $CfgObj["env"].PSObject.Properties) { $NextEnv[$ep.Name] = $ep.Value }
  }
  foreach ($mk in @(
    "CLAUDE_CODE_USE_BEDROCK", "AWS_REGION", "AWS_PROFILE",
    "CLAUDE_CODE_USE_VERTEX", "CLOUD_ML_REGION", "ANTHROPIC_VERTEX_PROJECT_ID",
    "ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL", "ANTHROPIC_SMALL_FAST_MODEL"
  )) {
    $NextEnv.Remove($mk)
  }
  foreach ($kv in $EnvPatch.GetEnumerator()) { $NextEnv[$kv.Key] = $kv.Value }
  $CfgObj["env"] = $NextEnv
  $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($SettingsFile, ($CfgObj | ConvertTo-Json -Depth 20) + "`n", $Utf8NoBom)
}

Remove-Item Env:CG_SETTINGS_FILE -ErrorAction SilentlyContinue
Remove-Item Env:CG_ENV_PATCH_JSON -ErrorAction SilentlyContinue

Write-Host "✅ 配置已无损合并写入 $SettingsFile（原有 mcpServers / permissions / hooks 100% 保留）！" -ForegroundColor Green
