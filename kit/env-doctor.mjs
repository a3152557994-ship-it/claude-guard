#!/usr/bin/env node
/**
 * Claude Guard — 本地终端环境与 Claude Code 封号漏点自检器 (env-doctor.mjs)
 * 运行方式: node env-doctor.mjs
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
const offsetHours = -new Date().getTimezoneOffset() / 60;
const settingsPath = path.join(os.homedir(), ".claude", "settings.json");

let settings = {};
let hasSettings = false;
if (fs.existsSync(settingsPath)) {
  try {
    settings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
    hasSettings = true;
  } catch (_e) {}
}

const envBlock = settings.env || {};
const telemetryOff =
  envBlock.DISABLE_TELEMETRY === "1" || process.env.DISABLE_TELEMETRY === "1";
const nonEssentialOff =
  envBlock.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC === "1" ||
  process.env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC === "1";
const usingBedrock =
  envBlock.CLAUDE_CODE_USE_BEDROCK === "1" || process.env.CLAUDE_CODE_USE_BEDROCK === "1";
const usingVertex =
  envBlock.CLAUDE_CODE_USE_VERTEX === "1" || process.env.CLAUDE_CODE_USE_VERTEX === "1";

const proxyVars = ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]
  .filter((k) => Boolean(process.env[k]))
  .map((k) => `${k}=${process.env[k]}`);

console.log("================================================================");
console.log("🛡️  Claude Guard — 本地终端防封环境自检报告 (CLI Doctor)");
console.log("================================================================");
console.log(`• 操作系统平台  : ${os.platform()} (${os.arch()})`);
console.log(`• 系统 Intl 时区: ${tz} (UTC${offsetHours >= 0 ? "+" : ""}${offsetHours})`);
console.log(`• 终端代理变量  : ${proxyVars.length > 0 ? proxyVars.join(", ") : "未显式设置 (走系统/TUN或直连)"}`);
console.log(`• 配置文件状态  : ${hasSettings ? `已找到 (${settingsPath})` : "未创建 (~/.claude/settings.json)"}`);
console.log("----------------------------------------------------------------");

let score = 100;
if (tz.includes("Shanghai") || tz.includes("Chongqing") || offsetHours === 8) {
  score -= 20;
  console.log("⚠️  [风险 -20] 系统时区为东八区 (" + tz + ")，若挂欧美机房节点直连官方个人号易触发跨洲异常标记。");
} else {
  console.log("✅ [通过] 系统时区未见明显东八区直出特征。");
}

if (!telemetryOff || !nonEssentialOff) {
  score -= 25;
  console.log("🚨 [风险 -25] 未在 ~/.claude/settings.json 中完整开启 DISABLE_TELEMETRY=1 与非必要流量屏蔽！");
  console.log("   👉 修复：运行本目录 ./cc-switch.sh (或 Windows 下 cc-switch.ps1) 一键加固。");
} else {
  console.log("✅ [通过] 已开启防遥测加固 (DISABLE_TELEMETRY=1 & CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1)。");
}

if (usingBedrock || usingVertex) {
  score = Math.max(score, 95);
  console.log(`🎉 [企业级通道] 当前已启用 ${usingBedrock ? "AWS Bedrock" : "Google Vertex AI"} 企业通道，100% 免除个人号封号风险！`);
}

console.log("----------------------------------------------------------------");
console.log(`📊 终端环境安全评分: ${score} / 100`);
console.log("🌐 完整 IP ASN 机房检测与 WebRTC 穿透体检: https://a3152557994-ship-it.github.io/claude-guard/");
console.log("================================================================");
