import {
  evaluateClaudeRisk,
  probePublicExitNetwork,
  formatConversationMarkdown,
  buildMigrationBundle,
  encryptVaultMarkdown,
  verifyLicenseUniversal,
} from "./guard-core.js";
import { MONETIZATION_CONFIG } from "./affiliate-config.js";

const FREE_VAULT_LIMIT = 20;
const isZh = (navigator.language || "").toLowerCase().startsWith("zh");
const tr = (zh, en) => (isZh ? zh : en);

let proActive = false;
let activeToken = "";
let vaultList = [];
let currentChat = null;

function wireConfigLinks() {
  document.getElementById("openPlaybookLink").href = MONETIZATION_CONFIG.playbookWebUrl;
  document.getElementById("bedrockGuideLink").href = MONETIZATION_CONFIG.bedrockVertexGuideUrl;
  document.getElementById("agentGuardLink").href = MONETIZATION_CONFIG.agentGuardUrl;
  document.getElementById("openWebRadarLink").href = MONETIZATION_CONFIG.webRadarUrl;
  document.getElementById("buySingleBtn").href = `${MONETIZATION_CONFIG.webRadarUrl}#checkout-single`;
  document.getElementById("buyBundleBtn").href = `${MONETIZATION_CONFIG.webRadarUrl}#checkout-bundle`;
}

function applyI18nLabels() {
  if (!isZh) {
    return;
  }
  document.getElementById("tierBadge").textContent = "免费版 (20场额度)";
  document.getElementById("lblEnvTitle").textContent = "🔍 出口 IP · ASN · 指纹风控监测";
  document.getElementById("openPlaybookLink").textContent = "📖 2026 防封全书";
  document.getElementById("bedrockGuideLink").textContent = "☁️ Bedrock/Vertex 零封号";
  document.getElementById("agentGuardLink").textContent = "⚡ Agent-Guard 熔断器";
  document.getElementById("openWebRadarLink").textContent = "📡 完整雷达";
  document.getElementById("lblCurTitle").textContent = "💬 当前对话与代码快照";
  document.getElementById("refreshBtn").textContent = "刷新";
  document.getElementById("exportMdBtn").textContent = "📥 导出 .md (免费)";
  document.getElementById("exportJsonBtn").textContent = "导出 .json";
  document.getElementById("stageVaultBtn").textContent = "🛡️ 存入保险箱";
  document.getElementById("lblVaultTitle").textContent = "📦 本地防丢保险箱";
  document.getElementById("lblVaultDesc").textContent =
    "纯本地保存 Markdown 与代码块；升级 Pro 解锁无限本地归档容量与 AES-256-GCM 加密迁移包导出。";
  document.getElementById("exportMigrationBtn").textContent = "🚀 导出新号恢复包";
  document.getElementById("exportEncryptedBtn").textContent = "🔐 Pro 加密导出 (.enc)";
  document.getElementById("lblProTitle").textContent = "🔑 升级 Pro 解锁无限归档与加密导出";
  document.getElementById("buySingleBtn").textContent = "🛒 单品买断 (¥15 / $4.99)";
  document.getElementById("buyBundleBtn").textContent = "🎁 全站通票 (¥39 / $14.99)";
  document.getElementById("licenseInput").placeholder = "粘贴 OPC1. 离线激活码...";
  document.getElementById("verifyBtn").textContent = "验签激活";
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

async function runExitNetworkAndEnvCheck() {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  const utcOffsetMinutes = -new Date().getTimezoneOffset();
  const languages = navigator.languages ? Array.from(navigator.languages) : [navigator.language || "en-US"];

  const badgeEl = document.getElementById("envBadge");
  const ipLineEl = document.getElementById("envIpLine");
  const detailEl = document.getElementById("envDetail");

  badgeEl.className = "env-pill warn";
  badgeEl.textContent = tr("探测中...", "Probing...");
  ipLineEl.textContent = tr("正在实时探测出口 IP、国家与 ASN 机房属性...", "Probing exit IP, country & ASN...");

  const net = await probePublicExitNetwork({ timeoutMs: 2600 });

  if (!net.online) {
    // Graceful offline fallback — show offline local fingerprint status without synthesizing any exit IP
    const isCnTz = tz.includes("Shanghai") || tz.includes("Chongqing") || utcOffsetMinutes === 480;
    badgeEl.className = isCnTz ? "env-pill warn" : "env-pill safe";
    badgeEl.textContent = tr("📡 离线/仅本地环境指纹检测", "📡 Offline / Local Fingerprint Only");
    ipLineEl.textContent = tr(
      `出口网络离线 · 本地时区 ${tz} (UTC${utcOffsetMinutes >= 0 ? "+" : ""}${utcOffsetMinutes / 60})`,
      `Network offline · Local TZ ${tz} (UTC${utcOffsetMinutes >= 0 ? "+" : ""}${utcOffsetMinutes / 60})`,
    );
    detailEl.textContent = isCnTz
      ? tr(
          `当前断网仅检测本地指纹：检测到东八区时区 (${tz})，联网挂欧美代理时请务必对齐时区或走 Bedrock 企业通道。`,
          `Offline local check: UTC+8 timezone (${tz}) detected; align timezone when using US/EU proxies or use AWS Bedrock.`,
        )
      : tr(
          `当前断网仅完成本地环境指纹检测：时区 ${tz} · 首选语言 ${languages[0]}。`,
          `Offline local fingerprint check complete: TZ ${tz} · Locale ${languages[0]}.`,
        );
    return;
  }

  const report = evaluateClaudeRisk({
    ip: net.ip,
    asn: net.asn,
    org: net.org,
    isp: net.isp,
    countryCode: net.countryCode,
    hosting: net.hosting,
    timezone: tz,
    utcOffsetMinutes,
    languages,
    telemetryHardened: true,
  });

  const asnLabel = [net.asn, net.org || net.isp].filter(Boolean).join(" · ") || tr("ISP 未知", "ISP Unknown");
  ipLineEl.textContent = `${net.ip} (${net.countryCode || "?"}) · ${asnLabel}`;

  if (report.riskLevel === "CRITICAL") {
    badgeEl.className = "env-pill crit";
    badgeEl.textContent = tr(`🚨 高危 (${report.survivalScore}分)`, `🚨 High Risk (${report.survivalScore})`);
    detailEl.textContent = report.summary.isDatacenter
      ? tr(
          `命中机房/共享云 ASN (${net.asn || "IDC"}) 或跨洲时区错位 (${tz})！极易连坐封号，建议切 AWS Bedrock/Vertex。`,
          `Datacenter ASN (${net.asn || "IDC"}) or timezone mismatch (${tz}) detected! High ban risk—use Bedrock/Vertex.`,
        )
      : tr(
          `${report.findings[0]?.title || "环境高危"} · 时区 ${tz}，建议阅读下方防封全书加固。`,
          `${report.findings[0]?.title || "Critical mismatch"} · TZ ${tz}. Check the Anti-Ban Guide below.`,
        );
  } else if (report.riskLevel === "WARNING") {
    badgeEl.className = "env-pill warn";
    badgeEl.textContent = tr(`⚠️ 中度风险 (${report.survivalScore}分)`, `⚠️ Warning (${report.survivalScore})`);
    detailEl.textContent = tr(
      `出口住宅属性正常，但本地时区 (${tz}) 或语言 (${languages[0]}) 存在偏差，建议备份对话防丢。`,
      `Residential ISP OK, but local timezone (${tz}) or locale (${languages[0]}) differs from exit region.`,
    );
  } else {
    badgeEl.className = "env-pill safe";
    badgeEl.textContent = tr(`🟢 原生稳连 (${report.survivalScore}分)`, `🟢 Clean ISP (${report.survivalScore})`);
    detailEl.textContent = tr(
      `住宅 ISP 属性正常 · 时区 ${tz} 与出口地区 (${net.countryCode}) 匹配良好。`,
      `Residential ISP verified · Timezone ${tz} matches exit region (${net.countryCode}).`,
    );
  }
}

function updateProBadgeUI(payload) {
  const badge = document.getElementById("tierBadge");
  badge.textContent = payload?.p === "*" ? tr("全站通票版", "All-Access Pro") : tr("Pro 无限版", "Pro Unlimited");
  badge.classList.add("pro");
  document.getElementById("vaultCapText").textContent = "∞";
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
      activeToken = stored.opc1_token;
      updateProBadgeUI(res.payload);
      document.getElementById("licenseMsg").textContent = tr(
        "✅ 已永久解锁无限归档与 AES-256-GCM 加密导出",
        "✅ Unlimited Vault & Encrypted Export Active",
      );
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
        `${currentChat.messages.length} msgs · ${currentChat.artifacts.length} code blocks`,
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
        `${currentChat.messages.length} msgs · ${currentChat.artifacts.length} code blocks`,
      );
    }
  } catch (_err) {
    currentChat = {
      id: "/fallback",
      title: "Chat Vault Local Backup",
      url: "https://claude.ai/chat/local",
      capturedAt: new Date().toISOString(),
      messages: [{ role: "user", text: "Backup project context locally." }],
      artifacts: [],
    };
    titleEl.textContent = currentChat.title;
  }
}

document.getElementById("refreshBtn").addEventListener("click", captureActiveTab);

document.getElementById("exportMdBtn").addEventListener("click", () => {
  if (!currentChat) return;
  const md = formatConversationMarkdown(currentChat);
  const safeName = (currentChat.title || "claude-chat").replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]+/g, "-").slice(0, 40);
  triggerDownload(md, `${safeName}.md`);
  document.getElementById("currentStatus").className = "status";
  document.getElementById("currentStatus").textContent = tr("✅ 已导出当前会话 Markdown！", "✅ Exported Markdown!");
});

document.getElementById("exportJsonBtn").addEventListener("click", () => {
  if (!currentChat) return;
  const safeName = (currentChat.title || "claude-chat").replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]+/g, "-").slice(0, 40);
  triggerDownload(JSON.stringify(currentChat, null, 2), `${safeName}.json`, "application/json;charset=utf-8");
  document.getElementById("currentStatus").className = "status";
  document.getElementById("currentStatus").textContent = tr("✅ 已导出当前会话 JSON！", "✅ Exported JSON!");
});

document.getElementById("stageVaultBtn").addEventListener("click", async () => {
  if (!currentChat) return;
  const idx = vaultList.findIndex((x) => x.url === currentChat.url && x.title === currentChat.title);
  if (idx < 0 && !proActive && vaultList.length >= FREE_VAULT_LIMIT) {
    document.getElementById("currentStatus").className = "status err";
    document.getElementById("currentStatus").textContent = tr(
      `🔒 免费归档容量已满（${FREE_VAULT_LIMIT}/${FREE_VAULT_LIMIT} 场）。请升级下方 Pro（¥15 单品 / ¥39 全站通票）解锁无限本地归档与 AES-256-GCM 加密导出！`,
      `🔒 Free vault full (${FREE_VAULT_LIMIT}/${FREE_VAULT_LIMIT}). Upgrade to Pro (¥15 / $4.99 or ¥39 / $14.99 All-Access) below for unlimited local archiving & encrypted export!`,
    );
    document.getElementById("licenseInput")?.focus();
    return;
  }
  if (idx >= 0) vaultList[idx] = currentChat;
  else vaultList.unshift(currentChat);
  await chrome.storage.local.set({ claude_guard_vault: vaultList });
  document.getElementById("vaultCount").textContent = String(vaultList.length);
  document.getElementById("currentStatus").className = "status";
  document.getElementById("currentStatus").textContent = tr(
    `🛡️ 已存入本地保险箱 (${vaultList.length}/${proActive ? "∞" : FREE_VAULT_LIMIT})`,
    `🛡️ Saved to local vault (${vaultList.length}/${proActive ? "∞" : FREE_VAULT_LIMIT})`,
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
    msgEl.textContent = tr(
      "🔒 超出免费容量，请升级下方 Pro（¥15 单品 / ¥39 全站通票）解锁无限归档导出。",
      "🔒 Upgrade to Pro below for unlimited vault export.",
    );
    return;
  }
  const bundle = buildMigrationBundle(sourceList);
  triggerDownload(bundle.markdownArchive, `claude-migration-${bundle.conversationCount}chats.md`);
  msgEl.className = "status";
  msgEl.textContent = tr(
    `✅ 已导出 ${bundle.conversationCount} 场对话 + 新号无缝恢复 Prompt！`,
    `✅ Exported ${bundle.conversationCount} chats + Context Recovery Prompt!`,
  );
});

document.getElementById("exportEncryptedBtn").addEventListener("click", async () => {
  const msgEl = document.getElementById("vaultMsg");
  if (!proActive) {
    msgEl.className = "status err";
    msgEl.textContent = tr(
      "🔒 AES-256-GCM 加密保险箱导出为 Pro 专属功能，请点下方获取 ¥15 单品码或 ¥39 全站通票！",
      "🔒 AES-256-GCM encrypted vault export requires Pro (¥15 / $4.99 or ¥39 / $14.99 All-Access).",
    );
    document.getElementById("licenseInput")?.focus();
    return;
  }
  const sourceList = vaultList.length > 0 ? vaultList : currentChat ? [currentChat] : [];
  const bundle = buildMigrationBundle(sourceList);
  const encryptedJson = await encryptVaultMarkdown(bundle.markdownArchive, activeToken);
  triggerDownload(encryptedJson, `claude-vault-encrypted-${bundle.conversationCount}chats.enc`, "application/json;charset=utf-8");
  msgEl.className = "status";
  msgEl.textContent = tr(
    `🔐 已生成 AES-256-GCM 加密归档包 (${bundle.conversationCount} 场)！`,
    `🔐 Exported AES-256-GCM encrypted vault (${bundle.conversationCount} chats)!`,
  );
});

document.getElementById("verifyBtn").addEventListener("click", async () => {
  const token = document.getElementById("licenseInput").value.trim();
  const msgEl = document.getElementById("licenseMsg");
  const res = await verifyLicenseUniversal(token, "claude-guard");
  if (res.valid) {
    proActive = true;
    activeToken = token;
    await chrome.storage.local.set({ opc1_token: token });
    updateProBadgeUI(res.payload);
    msgEl.className = "status";
    msgEl.textContent = tr(
      "✅ Ed25519 验签通过！已永久解锁无限本地归档与加密导出！",
      "✅ Unlimited Vault & Encrypted Export unlocked forever!",
    );
  } else {
    msgEl.className = "status err";
    msgEl.textContent = `❌ ${res.reason}`;
  }
});

wireConfigLinks();
applyI18nLabels();
runExitNetworkAndEnvCheck();
loadState().then(captureActiveTab);
