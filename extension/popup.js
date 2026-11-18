import {
  evaluateClaudeRisk,
  formatConversationMarkdown,
  buildMigrationBundle,
  verifyLicenseUniversal,
} from "./guard-core.js";

const WEB_RADAR_URL = "https://a3152557994-ship-it.github.io/claude-guard/";

let proActive = false;
let vaultList = [];
let currentChat = null;

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
    ip: "本地检测",
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
    badgeEl.textContent = `⚠️ 时区暴露 (${tz})`;
    detailEl.textContent = `检测到本地时区为 ${tz} (UTC+8)，首选语言 ${languages[0]}。若挂欧美节点直连极易触发跨洲指纹风控！`;
  } else if (report.riskLevel === "WARNING") {
    badgeEl.className = "env-pill warn";
    badgeEl.textContent = `中度注意 (${ report.survivalScore }分)`;
    detailEl.textContent = `当前时区 ${tz} · 语言 ${languages[0]}。建议点击下方链接做完整 ASN 机房与 WebRTC 穿透检测。`;
  } else {
    badgeEl.className = "env-pill safe";
    badgeEl.textContent = `🟢 指纹协调 (${ report.survivalScore }分)`;
    detailEl.textContent = `当前时区 ${tz} · 语言 ${languages[0]}，本地浏览器时区与语言未见明显东八区冲突。`;
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
      badge.textContent = "Pro 终身版";
      badge.classList.add("pro");
      document.getElementById("licenseMsg").textContent = `✅ Pro 已永久激活 (${res.payload.p})`;
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
        title: "示例对话（请在 claude.ai 或任意网页点击图标）",
        url: "https://claude.ai/chat/demo",
        capturedAt: new Date().toISOString(),
        messages: [
          { role: "user", text: "Help me configure Claude Code with AWS Bedrock so my account never gets suspended." },
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
      metaEl.textContent = `${currentChat.messages.length} 条消息 · ${currentChat.artifacts.length} 个代码块 (内置演示快照)`;
      return;
    }

    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"],
    });

    const resp = await chrome.tabs.sendMessage(tab.id, { type: "CAPTURE_CURRENT_CHAT" });
    if (resp?.ok && resp.data) {
      currentChat = resp.data;
      titleEl.textContent = currentChat.title || "当前页面会话";
      metaEl.textContent = `${currentChat.messages.length} 条消息段落 · ${currentChat.artifacts.length} 个代码块/Artifacts`;
    }
  } catch (err) {
    titleEl.textContent = "当前页面受浏览器保护（已加载演示快照）";
    currentChat = {
      id: "/fallback-session",
      title: "Claude Guard Local Backup Demo",
      url: "https://claude.ai/chat/local",
      capturedAt: new Date().toISOString(),
      messages: [{ role: "user", text: "Backup my Claude project context locally." }],
      artifacts: [],
    };
    metaEl.textContent = `${currentChat.messages.length} 条消息 · 可直接测试导出与保险箱`;
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
  triggerDownload(md, `${safeName}.md`, "text/markdown;charset=utf-8");
  document.getElementById("currentStatus").textContent = "✅ 已免费导出当前对话 Markdown！";
});

document.getElementById("exportJsonBtn").addEventListener("click", () => {
  if (!currentChat) return;
  const safeName = (currentChat.title || "claude-chat").replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]+/g, "-").slice(0, 40);
  triggerDownload(JSON.stringify(currentChat, null, 2), `${safeName}.json`, "application/json;charset=utf-8");
  document.getElementById("currentStatus").textContent = "✅ 已免费导出当前对话 JSON！";
});

document.getElementById("stageVaultBtn").addEventListener("click", async () => {
  if (!currentChat) return;
  const existingIdx = vaultList.findIndex((x) => x.url === currentChat.url && x.title === currentChat.title);
  if (existingIdx >= 0) {
    vaultList[existingIdx] = currentChat;
  } else {
    vaultList.unshift(currentChat);
  }
  await chrome.storage.local.set({ claude_guard_vault: vaultList });
  document.getElementById("vaultCount").textContent = String(vaultList.length);
  document.getElementById("currentStatus").textContent = `🛡️ 已存入本地保险箱（当前共守护 ${vaultList.length} 场对话）！`;
});

document.getElementById("exportMigrationBtn").addEventListener("click", () => {
  const msgEl = document.getElementById("vaultMsg");
  if (!proActive) {
    msgEl.className = "status err";
    msgEl.textContent = `🔒 你的保险箱已有 ${vaultList.length} 场对话。请在下方输入 OPC1. 激活码解锁全量打包与新号秒级恢复 Prompt（¥15 终身买断）。`;
    return;
  }
  const sourceList = vaultList.length > 0 ? vaultList : currentChat ? [currentChat] : [];
  if (sourceList.length === 0) {
    msgEl.className = "status err";
    msgEl.textContent = "保险箱为空，请先点击上方「🛡️ 存入防丢保险箱」。";
    return;
  }
  const bundle = buildMigrationBundle(sourceList);
  triggerDownload(
    bundle.markdownArchive,
    `claude-vault-migration-${bundle.conversationCount}chats.md`,
    "text/markdown;charset=utf-8"
  );
  msgEl.className = "status";
  msgEl.textContent = `✅ 已导出 ${bundle.conversationCount} 场对话 + 新号无缝接续 Prompt！`;
});

document.getElementById("clearVaultBtn").addEventListener("click", async () => {
  vaultList = [];
  await chrome.storage.local.set({ claude_guard_vault: [] });
  document.getElementById("vaultCount").textContent = "0";
  const msgEl = document.getElementById("vaultMsg");
  msgEl.className = "status";
  msgEl.textContent = "已清空本地保险箱。";
});

document.getElementById("verifyBtn").addEventListener("click", async () => {
  const token = document.getElementById("licenseInput").value.trim();
  const msgEl = document.getElementById("licenseMsg");
  const res = await verifyLicenseUniversal(token, "claude-guard");
  if (res.valid) {
    proActive = true;
    await chrome.storage.local.set({ opc1_token: token });
    const badge = document.getElementById("tierBadge");
    badge.textContent = "Pro 终身版";
    badge.classList.add("pro");
    msgEl.className = "status";
    msgEl.textContent = `✅ 验签成功！已永久解锁全量导出与新号迁移包 (${res.payload.p})`;
  } else {
    msgEl.className = "status err";
    msgEl.textContent = `❌ 激活码无效：${res.reason}`;
  }
});

document.getElementById("buyKeyLink").addEventListener("click", (e) => {
  e.preventDefault();
  const subject = encodeURIComponent("[购买激活码] Claude Guard Pro 终身买断 (¥15 / $4.99)");
  const body = encodeURIComponent(
    "你好！我想购买 Claude Guard (`claude-guard`) 浏览器防丢备份插件 Pro 终身激活码 (¥15 / $4.99)。\n接收激活码邮箱："
  );
  chrome.tabs.create({ url: `mailto:3152557994@qq.com?cc=a3152557994@gmail.com&subject=${subject}&body=${body}` });
});

runLocalEnvCheck();
loadState().then(captureActiveTab);
