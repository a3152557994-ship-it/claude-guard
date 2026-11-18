import {
  evaluateClaudeRisk,
  formatConversationMarkdown,
  buildMigrationBundle,
  verifyLicenseUniversal,
} from "./guard-core.js";

const WEB_RADAR_URL = "https://a3152557994-ship-it.github.io/claude-guard/";
const FREE_VAULT_LIMIT = 20;
const isZh = (navigator.language || "").toLowerCase().startsWith("zh");
const tr = (zh, en) => (isZh ? zh : en);

let proActive = false;
let vaultList = [];
let currentChat = null;

function applyI18nLabels() {
  if (!isZh) return;
  document.getElementById("tierBadge").textContent = "免费畅享版 (含20场归档)";
  document.getElementById("lblEnvTitle").textContent = "🔍 浏览器环境风控监测";
  document.getElementById("affProxyLink").textContent = "🌐 获取纯净静态住宅IP";
  document.getElementById("affBrowserLink").textContent = "🔒 隔离时区指纹";
  document.getElementById("openWebRadarLink").textContent = "📡 完整体检";
  document.getElementById("lblCurTitle").textContent = "💬 当前对话与代码快照";
  document.getElementById("refreshBtn").textContent = "刷新";
  document.getElementById("exportMdBtn").textContent = "📥 导出 .md (免费)";
  document.getElementById("exportJsonBtn").textContent = "导出 .json";
  document.getElementById("stageVaultBtn").textContent = "🛡️ 存入保险箱";
  document.getElementById("lblVaultTitle").textContent = "📦 本地防丢保险箱 (20场内全免费)";
  document.getElementById("lblVaultDesc").textContent =
    "免费一键导出全量 Markdown +「新号 1 秒接续上下文恢复 Prompt」，不怕限流或封号丢进度。";
  document.getElementById("exportMigrationBtn").textContent =
    "🚀 一键导出全量归档 + 新号无缝恢复包 (20场内免费)";
  document.getElementById("clearVaultBtn").textContent = "清空";
  document.getElementById("lblProTitle").textContent = "🔑 重度无限容量解锁 (>20场 · ¥15 / $4.99 终身)";
  document.getElementById("licenseInput").placeholder = "粘贴 OPC1. 离线激活码...";
  document.getElementById("verifyBtn").textContent = "激活";
}

function triggerDownload(text, filename, mimeType = "text/markdown;charset=utf-8") {
  const blob = new Blob([text], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

function runLocalEnvCheck() {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  const utcOffsetMinutes = -new Date().getTimezoneOffset();
  const languages = navigator.languages ? Array.from(navigator.languages) : [navigator.language || "en-US"];

  const report = evaluateClaudeRisk({
    ip: "local",
    countryCode: "US",
    timezone: tz,
    utcOffsetMinutes,
    languages,
    telemetryHardened: true,
  });

  const badgeEl = document.getElementById("envBadge");
  const detailEl = document.getElementById("envDetail");

  if (report.riskLevel === "CRITICAL" || tz.includes("Shanghai") || tz.includes("Chongqing") || utcOffsetMinutes === 480) {
    badgeEl.className = "env-pill crit";
    badgeEl.textContent = tr(`⚠️ 时区暴露 (${tz})`, `⚠️ TZ Mismatch (${tz})`);
    detailEl.textContent = tr(
      `检测到东八区时区 ${tz}，若挂欧美节点直连易触发跨洲异常！建议配置下方静态住宅 IP 与时区隔离。`,
      `Local timezone ${tz} conflicts with US/EU proxies. Use a dedicated Static ISP IP & isolated browser profile below.`
    );
  } else {
    badgeEl.className = "env-pill safe";
    badgeEl.textContent = tr(`🟢 指纹正常`, `🟢 Locale Matched`);
    detailEl.textContent = tr(
      `当前时区 ${tz} · 语言 ${languages[0]}。可点下方「完整体检」核查机房 ASN。`,
      `Timezone ${tz} · Locale ${languages[0]}. Click 'Full ASN Audit' to check datacenter IP score.`
    );
  }
}

async function loadState() {
  const stored = await chrome.storage.local.get(["opc1_token", "claude_guard_vault"]);
  vaultList = Array.isArray(stored.claude_guard_vault) ? stored.claude_guard_vault : [];
  document.getElementById("vaultCount").textContent = String(vaultList.length);

  if (stored.opc1_token) {
    document.getElementById("licenseInput").value = stored.opc1_token;
    const res = await verifyLicenseUniversal(stored.opc1_token, "claude-guard");
    if (res.valid) {
      proActive = true;
      const badge = document.getElementById("tierBadge");
      badge.textContent = tr("Pro 无限容量版", "Pro Unlimited");
      badge.classList.add("pro");
      document.getElementById("licenseMsg").textContent = tr(`✅ 已激活无限容量`, `✅ Unlimited Vault Active`);
    }
  }
}

async function captureActiveTab() {
  const titleEl = document.getElementById("currentTitle");
  const metaEl = document.getElementById("currentMeta");

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id || !tab.url || /^(chrome|edge|about):/i.test(tab.url)) {
      currentChat = {
        id: "/demo-session",
        title: tr("内置演示会话（在 claude.ai 打开即可自动抓取）", "Demo Session (Open claude.ai to capture live)"),
        url: "https://claude.ai/chat/demo",
        capturedAt: new Date().toISOString(),
        messages: [
          { role: "user", text: "Configure Claude Code with AWS Bedrock so my account never gets suspended." },
          { role: "assistant", text: "Set CLAUDE_CODE_USE_BEDROCK=1 and DISABLE_TELEMETRY=1 in ~/.claude/settings.json." },
        ],
        artifacts: [
          {
            title: "settings.json",
            language: "json",
            code: '{\n  "env": {\n    "CLAUDE_CODE_USE_BEDROCK": "1",\n    "DISABLE_TELEMETRY": "1"\n  }\n}',
          },
        ],
      };
      titleEl.textContent = currentChat.title;
      metaEl.textContent = tr(
        `${currentChat.messages.length} 条消息 · ${currentChat.artifacts.length} 个代码块`,
        `${currentChat.messages.length} msgs · ${currentChat.artifacts.length} code blocks`
      );
      return;
    }

    await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["content.js"] });
    const resp = await chrome.tabs.sendMessage(tab.id, { type: "CAPTURE_CURRENT_CHAT" });
    if (resp?.ok && resp.data) {
      currentChat = resp.data;
      titleEl.textContent = currentChat.title || "Session";
      metaEl.textContent = tr(
        `${currentChat.messages.length} 条消息 · ${currentChat.artifacts.length} 个代码块`,
        `${currentChat.messages.length} msgs · ${currentChat.artifacts.length} code blocks`
      );
    }
  } catch (_err) {
    currentChat = {
      id: "/fallback",
      title: "Claude Guard Local Backup",
      url: "https://claude.ai/chat/local",
      capturedAt: new Date().toISOString(),
      messages: [{ role: "user", text: "Backup project context locally." }],
      artifacts: [],
    };
    titleEl.textContent = currentChat.title;
  }
}

document.getElementById("openWebRadarLink").addEventListener("click", (e) => {
  e.preventDefault();
  chrome.tabs.create({ url: WEB_RADAR_URL });
});

document.getElementById("refreshBtn").addEventListener("click", captureActiveTab);

document.getElementById("exportMdBtn").addEventListener("click", () => {
  if (!currentChat) return;
  const md = formatConversationMarkdown(currentChat);
  const safeName = (currentChat.title || "claude-chat").replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]+/g, "-").slice(0, 40);
  triggerDownload(md, `${safeName}.md`);
  document.getElementById("currentStatus").textContent = tr("✅ 已免费导出 Markdown！", "✅ Exported Markdown!");
});

document.getElementById("exportJsonBtn").addEventListener("click", () => {
  if (!currentChat) return;
  const safeName = (currentChat.title || "claude-chat").replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]+/g, "-").slice(0, 40);
  triggerDownload(JSON.stringify(currentChat, null, 2), `${safeName}.json`, "application/json;charset=utf-8");
  document.getElementById("currentStatus").textContent = tr("✅ 已免费导出 JSON！", "✅ Exported JSON!");
});

document.getElementById("stageVaultBtn").addEventListener("click", async () => {
  if (!currentChat) return;
  if (!proActive && vaultList.length >= FREE_VAULT_LIMIT) {
    document.getElementById("currentStatus").className = "status err";
    document.getElementById("currentStatus").textContent = tr(
      `免费版最多保存 ${FREE_VAULT_LIMIT} 场会话，可先免费导出清空或激活下方无限版。`,
      `Free vault holds ${FREE_VAULT_LIMIT} chats. Export & clear for free, or unlock Unlimited below.`
    );
    return;
  }
  const idx = vaultList.findIndex((x) => x.url === currentChat.url && x.title === currentChat.title);
  if (idx >= 0) vaultList[idx] = currentChat;
  else vaultList.unshift(currentChat);
  await chrome.storage.local.set({ claude_guard_vault: vaultList });
  document.getElementById("vaultCount").textContent = String(vaultList.length);
  document.getElementById("currentStatus").className = "status";
  document.getElementById("currentStatus").textContent = tr(
    `🛡️ 已存入保险箱 (${vaultList.length}/${proActive ? "∞" : FREE_VAULT_LIMIT})`,
    `🛡️ Saved to local vault (${vaultList.length}/${proActive ? "∞" : FREE_VAULT_LIMIT})`
  );
});

document.getElementById("exportMigrationBtn").addEventListener("click", () => {
  const msgEl = document.getElementById("vaultMsg");
  const sourceList = vaultList.length > 0 ? vaultList : currentChat ? [currentChat] : [];
  if (sourceList.length === 0) {
    msgEl.className = "status err";
    msgEl.textContent = tr("保险箱为空，请先点上方存入。", "Vault is empty.");
    return;
  }
  if (!proActive && sourceList.length > FREE_VAULT_LIMIT) {
    msgEl.className = "status err";
    msgEl.textContent = tr("超过 20 场大容量归档请激活下方无限版。", "Unlock Unlimited below for >20 chats.");
    return;
  }
  const bundle = buildMigrationBundle(sourceList);
  triggerDownload(bundle.markdownArchive, `claude-migration-${bundle.conversationCount}chats.md`);
  msgEl.className = "status";
  msgEl.textContent = tr(
    `✅ 已免费导出 ${bundle.conversationCount} 场对话 + 新号恢复 Prompt！`,
    `✅ Exported ${bundle.conversationCount} chats + Context Handoff Prompt!`
  );
});

document.getElementById("clearVaultBtn").addEventListener("click", async () => {
  vaultList = [];
  await chrome.storage.local.set({ claude_guard_vault: [] });
  document.getElementById("vaultCount").textContent = "0";
  document.getElementById("vaultMsg").textContent = tr("已清空。", "Cleared.");
});

document.getElementById("verifyBtn").addEventListener("click", async () => {
  const token = document.getElementById("licenseInput").value.trim();
  const msgEl = document.getElementById("licenseMsg");
  const res = await verifyLicenseUniversal(token, "claude-guard");
  if (res.valid) {
    proActive = true;
    await chrome.storage.local.set({ opc1_token: token });
    const badge = document.getElementById("tierBadge");
    badge.textContent = tr("Pro 无限容量版", "Pro Unlimited");
    badge.classList.add("pro");
    msgEl.className = "status";
    msgEl.textContent = tr("✅ 已永久解锁无限容量归档！", "✅ Unlimited Vault unlocked forever!");
  } else {
    msgEl.className = "status err";
    msgEl.textContent = `❌ ${res.reason}`;
  }
});

applyI18nLabels();
runLocalEnvCheck();
loadState().then(captureActiveTab);
