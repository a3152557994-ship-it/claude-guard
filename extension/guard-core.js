/**
 * Claude Guard Core Engine (Browser + Extension + Node Test Compatible)
 * - 100% Local Environment & IP/ASN/Timezone/WebRTC Risk Auditor
 * - Claude Code Hardened & Multi-Provider (Bedrock / Vertex / Relay) Config Generator
 * - Local Conversation & Artifact Markdown + Context Handoff Exporter
 * - Offline Ed25519 License Verification (OPC1.<payload>.<sig>)
 */

export const PUBLIC_SPKI_BASE64 = "MCowBQYDK2VwAyEAP5NCVP7CT0tgaGLSGMe4r87SjYRWTM6gN6igBZYSXys=";

const DATACENTER_KEYWORDS = [
  "cloudflare",
  "digitalocean",
  "choopa",
  "vultr",
  "linode",
  "akamai",
  "hetzner",
  "m247",
  "ovh",
  "contabo",
  "amazon",
  "aws",
  "google cloud",
  "gcp",
  "microsoft",
  "azure",
  "alibaba",
  "aliyun",
  "tencent",
  "huawei",
  "oracle",
  "rackspace",
  "leaseweb",
  "psychz",
  "multacom",
  "zenlayer",
  "dmit",
  "bandwagon",
  "it7",
  "datacamp",
  "hostinger",
  "kamatera",
];

const DATACENTER_ASNS = new Set([
  "AS13335", // Cloudflare
  "AS14061", // DigitalOcean
  "AS20473", // Choopa / Vultr
  "AS63949", // Linode / Akamai
  "AS24940", // Hetzner
  "AS9009",  // M247
  "AS16276", // OVH
  "AS16509", // AWS
  "AS14618", // AWS
  "AS15169", // Google
  "AS396982",// Google Cloud
  "AS8075",  // Microsoft Azure
  "AS45102", // Alibaba
  "AS45090", // Tencent
  "AS132203",// Tencent
  "AS31898", // Oracle
  "AS60068", // Datacamp / CDN77
  "AS25820", // IT7 / BandwagonHost
]);

const UNSUPPORTED_REGIONS = new Set(["CN", "HK", "MO", "RU", "BY", "IR", "KP", "SY"]);

const CN_TIMEZONES = new Set([
  "Asia/Shanghai",
  "Asia/Chongqing",
  "Asia/Harbin",
  "Asia/Urumqi",
  "Asia/Hong_Kong",
  "Asia/Macau",
]);

/**
 * Evaluate Claude Web & Claude Code ban risk from local + IP signals
 */
export function evaluateClaudeRisk(input = {}) {
  const {
    ip = "未知",
    asn = "",
    org = "",
    isp = "",
    countryCode = "",
    hosting = false,
    timezone = "UTC",
    utcOffsetMinutes = 0,
    languages = ["en-US"],
    webrtcLeakedIps = [],
    telemetryHardened = false,
    sharedAccount = false,
    virtualCardRisk = false,
  } = input;

  let penalty = 0;
  const findings = [];

  const cc = String(countryCode || "").toUpperCase().trim();
  const orgLower = `${asn} ${org} ${isp}`.toLowerCase();
  const normAsn = String(asn || "").toUpperCase().trim().split(/\s+/)[0];

  // 1. Region check
  if (cc && UNSUPPORTED_REGIONS.has(cc)) {
    penalty += 45;
    findings.push({
      id: "region-unsupported",
      severity: "critical",
      title: `出口地区属于非服务区 (${cc})`,
      detail: `当前出口 IP 归属地为 ${cc}，直连 claude.ai 或调用官方个人接口会直接触发区域拦截或关联封号。`,
      fix: "切换至美英日新等支持区域的原生静态住宅 ISP 节点，或直接改走 AWS Bedrock / Google Vertex AI 企业通道。",
      actionType: "residential-ip",
    });
  }

  // 2. ASN / Datacenter Hosting check
  const isDcKeyword = DATACENTER_KEYWORDS.some((kw) => orgLower.includes(kw));
  const isDcAsn = DATACENTER_ASNS.has(normAsn);
  if (hosting || isDcKeyword || isDcAsn) {
    penalty += 32;
    findings.push({
      id: "asn-datacenter",
      severity: "critical",
      title: `机房/广播共享 IP 风险 (${normAsn || "IDC"} · ${org || isp || "DataCenter"})`,
      detail: "检测到当前网络属于云厂商机房或公共代理 ASN。几百人共用同一机房出口是连坐封号的头号原因。",
      fix: "更换为独享双 ISP 静态原生住宅 IP（Residential ISP），或使用 Claude Code 对接免风控的 AWS Bedrock。",
      actionType: "residential-ip",
    });
  } else if (ip && ip !== "未知") {
    findings.push({
      id: "asn-clean",
      severity: "safe",
      title: `ISP 网络属性正常 (${normAsn || "ISP"} · ${org || isp || "Residential"})`,
      detail: "未命中常见高危云机房黑名单 ASN，建议固定单一节点避免频繁跨国跳变。",
      fix: "使用 Chrome 插件开启「出口 IP 锁定预警」，防止代理掉线瞬间裸连暴露。",
      actionType: "extension",
    });
  }

  // 3. Timezone vs Region mismatch
  const isCnTz = CN_TIMEZONES.has(timezone) || utcOffsetMinutes === 480;
  const isAsianAllowed = ["SG", "JP", "KR", "TW", "MY", "PH"].includes(cc);
  if (isCnTz && cc && !UNSUPPORTED_REGIONS.has(cc) && !isAsianAllowed) {
    penalty += 25;
    findings.push({
      id: "timezone-mismatch",
      severity: "critical",
      title: `系统时区 (${timezone}) 与出口国家 (${cc}) 跨洲错位`,
      detail: "客户端与网页 JS 可直接读取 Intl 系统时区。挂着欧美节点却暴露东八区 Asia/Shanghai 时区，是识别跨境代充/共享号的典型特征。",
      fix: "使用独立浏览器 Profile 容器将时区、语言与出口 IP 归属地对齐，或改走 AWS Bedrock / Google Cloud Vertex AI 合规企业通道。",
      actionType: "cc-kit",
    });
  } else if (CN_TIMEZONES.has(timezone)) {
    penalty += 15;
    findings.push({
      id: "timezone-cn-literal",
      severity: "warning",
      title: `本地时区标识直出 (${timezone})`,
      detail: "虽然当前时区偏移相近，但时区字符串直接暴露中国大陆城市名称（Asia/Shanghai）。",
      fix: "在独立浏览器容器中将时区覆盖为 Asia/Singapore 或 America/Los_Angeles，并在 Claude Code 中开启防遥测加固。",
      actionType: "cc-kit",
    });
  }

  // 4. WebRTC Leak check
  const leaked = Array.isArray(webrtcLeakedIps)
    ? webrtcLeakedIps.filter((x) => x && x !== ip && !/^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|127\.|::1|fe80:)/i.test(x))
    : [];
  if (leaked.length > 0) {
    penalty += 28;
    findings.push({
      id: "webrtc-leak",
      severity: "critical",
      title: `WebRTC 穿透泄露真实公网 IP (${leaked.join(", ")})`,
      detail: "虽然 HTTP 流量走了代理，但浏览器 WebRTC STUN 握手直接暴露了不一致的底层公网 IP。",
      fix: "立即在浏览器中禁用 WebRTC UDP 泄露，或使用防关联浏览器隔离网络栈。",
      actionType: "antidetect-browser",
    });
  }

  // 5. Browser Locale check
  const primaryLang = Array.isArray(languages) && languages.length > 0 ? String(languages[0]) : "";
  if (/^zh/i.test(primaryLang) && cc && !["CN", "HK", "TW", "SG"].includes(cc)) {
    penalty += 10;
    findings.push({
      id: "locale-zh",
      severity: "warning",
      title: `浏览器首选语言 (${primaryLang}) 与欧美节点不一致`,
      detail: "navigator.language 首选语言为中文，与欧美原生居民设备画像存在偏差。",
      fix: "将日常用 Claude 的独立浏览器 Profile 首选语言设为 en-US。",
      actionType: "extension",
    });
  }

  // 6. Claude Code Telemetry check
  if (!telemetryHardened) {
    penalty += 15;
    findings.push({
      id: "cc-telemetry",
      severity: "warning",
      title: "Claude Code 终端未开启防遥测与非必要流量屏蔽",
      detail: "默认配置下 Claude Code 会上报 Statsig 遥测、错误堆栈与本地环境元数据。",
      fix: "使用下方生成台一键写入 DISABLE_TELEMETRY=1 与 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1，或对接 Bedrock 企业源。",
      actionType: "cc-kit",
    });
  }

  // 7. Shared Account / Virtual Card flags
  if (sharedAccount) {
    penalty += 30;
    findings.push({
      id: "shared-account",
      severity: "critical",
      title: "多人拼车 / 多设备异地交替登录",
      detail: "同一账号短时间内出现不同设备指纹或跨州 IP 切换，极易触发整车连坐封禁。",
      fix: "严禁使用闲鱼拼车号；坚持一人一号独享环境，并用 Claude Guard 插件实时备份对话防丢。",
      actionType: "extension",
    });
  }

  if (virtualCardRisk) {
    penalty += 20;
    findings.push({
      id: "virtual-card",
      severity: "warning",
      title: "高危虚拟卡段 / 代充账单回滚风险",
      detail: "烂大街的廉价虚拟卡段已被 Stripe 高危标记，极易在扣款后数天内触发二次风控封号。",
      fix: "网页端不稳时优先走美区 App Store 礼品卡内购订阅，或直接用按量计费的合规 API / Bedrock 通道。",
      actionType: "cc-kit",
    });
  }

  const survivalScore = Math.max(5, Math.min(98, 100 - penalty));
  let riskLevel = "SAFE";
  let badgeText = "安全稳连 · 环境纯净度高";
  if (survivalScore < 55) {
    riskLevel = "CRITICAL";
    badgeText = "高危预警 · 极易触发风控秒封";
  } else if (survivalScore < 80) {
    riskLevel = "WARNING";
    badgeText = "中度风险 · 存在本地环境漏点";
  }

  return {
    survivalScore,
    riskLevel,
    badgeText,
    findings,
    summary: {
      ip,
      asn: normAsn || "未知",
      location: cc || "未知",
      timezone,
      primaryLang: primaryLang || "en-US",
      isDatacenter: Boolean(hosting || isDcKeyword || isDcAsn),
      isTimezoneMismatch: isCnTz && cc !== "CN",
    },
  };
}

/**
 * Generate Claude Code ~/.claude/settings.json and shell switcher snippet
 */
export function generateClaudeCodeConfig(options = {}) {
  const {
    mode = "official-hardened",
    awsRegion = "us-east-1",
    gcpProjectId = "your-gcp-project-id",
    gcpRegion = "us-east5",
    baseUrl = "https://openrouter.ai/api/v1",
    apiKeyPlaceholder = "sk-ant-or-your-key-here",
    modelPrimary = "claude-sonnet-4-20250514",
  } = options;

  const baseEnv = {
    DISABLE_TELEMETRY: "1",
    DISABLE_ERROR_REPORTING: "1",
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1",
  };

  let env = { ...baseEnv };
  let title = "官方账号 · 防遥测隐私加固模式";
  let shellExports = [
    "export DISABLE_TELEMETRY=1",
    "export DISABLE_ERROR_REPORTING=1",
    "export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1",
  ];

  if (mode === "aws-bedrock") {
    title = "AWS Bedrock · 企业级零封号直连模式";
    env = {
      ...baseEnv,
      CLAUDE_CODE_USE_BEDROCK: "1",
      AWS_REGION: awsRegion,
      ANTHROPIC_MODEL: `us.anthropic.${modelPrimary}-v1:0`,
    };
    shellExports.push(
      "export CLAUDE_CODE_USE_BEDROCK=1",
      `export AWS_REGION="${awsRegion}"`,
      `export ANTHROPIC_MODEL="us.anthropic.${modelPrimary}-v1:0"`
    );
  } else if (mode === "gcp-vertex") {
    title = "Google Cloud Vertex AI · 企业级零封号模式（可消耗 GCP 赠金）";
    env = {
      ...baseEnv,
      CLAUDE_CODE_USE_VERTEX: "1",
      CLOUD_ML_REGION: gcpRegion,
      ANTHROPIC_VERTEX_PROJECT_ID: gcpProjectId,
    };
    shellExports.push(
      "export CLAUDE_CODE_USE_VERTEX=1",
      `export CLOUD_ML_REGION="${gcpRegion}"`,
      `export ANTHROPIC_VERTEX_PROJECT_ID="${gcpProjectId}"`
    );
  } else if (mode === "openrouter" || mode === "custom-relay") {
    title = mode === "openrouter" ? "OpenRouter / 聚合网关 · 限流无缝热备模式" : "自定义兼容网关 / 国产大模型兜底模式";
    env = {
      ...baseEnv,
      ANTHROPIC_BASE_URL: baseUrl,
      ANTHROPIC_AUTH_TOKEN: apiKeyPlaceholder,
      ANTHROPIC_MODEL: modelPrimary,
    };
    shellExports.push(
      `export ANTHROPIC_BASE_URL="${baseUrl}"`,
      `export ANTHROPIC_AUTH_TOKEN="${apiKeyPlaceholder}"`,
      `export ANTHROPIC_MODEL="${modelPrimary}"`
    );
  }

  const settingsJsonObj = {
    env,
    permissions: {
      allow: ["Bash(git status)", "Bash(git diff)", "Bash(npm test)"],
      deny: [],
    },
  };

  return {
    mode,
    title,
    settingsJson: JSON.stringify(settingsJsonObj, null, 2),
    shellSnippet: shellExports.join("\n"),
  };
}

/**
 * Format a single captured Claude conversation into clean Markdown with Artifacts & Code blocks
 */
export function formatConversationMarkdown(conv = {}) {
  const title = conv.title || "Untitled Claude Conversation";
  const url = conv.url || "https://claude.ai/chat/local-backup";
  const capturedAt = conv.capturedAt || new Date().toISOString();
  const messages = Array.isArray(conv.messages) ? conv.messages : [];
  const artifacts = Array.isArray(conv.artifacts) ? conv.artifacts : [];

  const lines = [
    "---",
    `title: "${String(title).replace(/"/g, '\\"')}"`,
    `source_url: "${url}"`,
    `backed_up_at: "${capturedAt}"`,
    `message_count: ${messages.length}`,
    `artifact_count: ${artifacts.length}`,
    `vault_tool: "Claude Guard Local Vault"`,
    "---",
    "",
    `# ${title}`,
    "",
    `> Backed up locally via **Claude Guard** at \`${capturedAt}\` · Source: ${url}`,
    "",
  ];

  messages.forEach((m, idx) => {
    const roleLabel = m.role === "user" || m.role === "human" ? "🧑 User" : "🤖 Claude";
    lines.push(`## ${idx + 1}. ${roleLabel}`);
    lines.push("");
    lines.push(String(m.text || m.content || "").trim());
    lines.push("");
  });

  if (artifacts.length > 0) {
    lines.push("---");
    lines.push("");
    lines.push("## 📦 Extracted Code Blocks & Artifacts");
    lines.push("");
    artifacts.forEach((art, idx) => {
      const lang = art.language || "text";
      const name = art.title || `Artifact #${idx + 1}`;
      lines.push(`### ${idx + 1}. ${name}`);
      lines.push("");
      lines.push(`\`\`\`${lang}`);
      lines.push(String(art.code || art.content || "").trim());
      lines.push("```");
      lines.push("");
    });
  }

  return lines.join("\n");
}

/**
 * Build Pro Bulk Migration Bundle + New Account Context Recovery Prompt
 */
export function buildMigrationBundle(conversations = []) {
  const list = Array.isArray(conversations) ? conversations : [];
  const exportedAt = new Date().toISOString();
  let totalMessages = 0;
  let totalArtifacts = 0;

  const summaryItems = list.map((c, idx) => {
    const msgs = Array.isArray(c.messages) ? c.messages : [];
    const arts = Array.isArray(c.artifacts) ? c.artifacts : [];
    totalMessages += msgs.length;
    totalArtifacts += arts.length;
    const lastUserMsg = [...msgs].reverse().find((m) => m.role === "user" || m.role === "human");
    const lastAssistantMsg = [...msgs].reverse().find((m) => m.role === "assistant" || m.role === "claude");

    return [
      `### Project / Session ${idx + 1}: ${c.title || "Untitled"}`,
      `- **Updated**: ${c.capturedAt || exportedAt}`,
      `- **Messages**: ${msgs.length} | **Code/Artifacts**: ${arts.length}`,
      lastUserMsg ? `- **Last User Goal**: ${String(lastUserMsg.text || "").slice(0, 260).replace(/\n+/g, " ")}` : null,
      lastAssistantMsg ? `- **Latest Output Summary**: ${String(lastAssistantMsg.text || "").slice(0, 320).replace(/\n+/g, " ")}` : null,
    ]
      .filter(Boolean)
      .join("\n");
  });

  const handoffPrompt = [
    "# 🔄 Claude Context Recovery & Account Migration Handoff",
    "",
    "> **使用方法**：当旧账号遭遇限流或封禁时，将以下内容直接粘贴到新 Claude 账号、Claude Code 或 Cursor 的首条对话中，即可 1 秒接续之前的完整上下文。",
    "",
    "```markdown",
    "I am migrating my active work from a previous Claude session. Please load the following project context and continue seamlessly from the latest state:",
    "",
    ...summaryItems,
    "",
    "Please confirm you have loaded this context and wait for my next instruction.",
    "```",
    "",
    "---",
    "",
    "# 📚 Full Local Vault Archive",
    "",
    ...list.map((c) => formatConversationMarkdown(c)),
  ].join("\n");

  return {
    exportedAt,
    conversationCount: list.length,
    totalMessages,
    totalArtifacts,
    markdownArchive: handoffPrompt,
  };
}

function fromBase64UrlToUint8Array(b64url) {
  const padded = b64url.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((b64url.length + 3) % 4);
  if (typeof Buffer !== "undefined") {
    return new Uint8Array(Buffer.from(padded, "base64"));
  }
  const bin = atob(padded);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i += 1) out[i] = bin.charCodeAt(i);
  return out;
}

function decodeBase64ToUint8Array(b64) {
  if (typeof Buffer !== "undefined") {
    return new Uint8Array(Buffer.from(b64, "base64"));
  }
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i += 1) out[i] = bin.charCodeAt(i);
  return out;
}

/**
 * Offline Ed25519 verification for OPC1.<payload>.<sig>
 */
export async function verifyLicenseUniversal(token, expectedProduct = "claude-guard", pubSpkiBase64 = PUBLIC_SPKI_BASE64) {
  if (typeof token !== "string") return { valid: false, reason: "INVALID_TYPE" };
  const parts = token.trim().split(".");
  if (parts.length !== 3 || parts[0] !== "OPC1") {
    return { valid: false, reason: "BAD_FORMAT" };
  }
  try {
    const [, payloadB64, sigB64] = parts;
    const spkiBytes = decodeBase64ToUint8Array(pubSpkiBase64);
    const sigBytes = fromBase64UrlToUint8Array(sigB64);
    const msgBytes = new TextEncoder().encode(`OPC1.${payloadB64}`);

    const cryptoKey = await globalThis.crypto.subtle.importKey(
      "spki",
      spkiBytes.buffer.slice(spkiBytes.byteOffset, spkiBytes.byteOffset + spkiBytes.byteLength),
      { name: "Ed25519" },
      false,
      ["verify"]
    );

    const ok = await globalThis.crypto.subtle.verify(
      { name: "Ed25519" },
      cryptoKey,
      sigBytes.buffer.slice(sigBytes.byteOffset, sigBytes.byteOffset + sigBytes.byteLength),
      msgBytes
    );

    if (!ok) return { valid: false, reason: "BAD_SIGNATURE" };

    const payloadJson = new TextDecoder().decode(fromBase64UrlToUint8Array(payloadB64));
    const payload = JSON.parse(payloadJson);

    if (expectedProduct && payload.p !== expectedProduct && payload.p !== "*") {
      return { valid: false, reason: "PRODUCT_MISMATCH", payload };
    }
    if (payload.exp && payload.exp > 0 && Math.floor(Date.now() / 1000) > payload.exp) {
      return { valid: false, reason: "EXPIRED", payload };
    }
    return { valid: true, payload };
  } catch (err) {
    return { valid: false, reason: "VERIFY_ERROR", message: err.message };
  }
}

/**
 * Parse key=value output from `https://cloudflare.com/cdn-cgi/trace`
 */
export function parseCloudflareTrace(rawText) {
  const map = {};
  for (const line of String(rawText || "").split(/\r?\n/)) {
    const idx = line.indexOf("=");
    if (idx > 0) {
      map[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    }
  }
  return {
    ip: map.ip || "",
    countryCode: (map.loc || "").toUpperCase(),
    colo: map.colo || "",
  };
}

function isDatacenterAsnOrOrg(asn = "", org = "", isp = "") {
  const normAsn = String(asn || "").toUpperCase().trim().split(/\s+/)[0];
  const combined = `${normAsn} ${org} ${isp}`.toLowerCase();
  return (
    DATACENTER_ASNS.has(normAsn) ||
    DATACENTER_KEYWORDS.some((kw) => combined.includes(kw)) ||
    /\b(hosting|datacenter|data center|cloud|vps|dedi|colocation|proxy)\b/i.test(combined)
  );
}

async function fetchWithTimeout(fetchImpl, url, timeoutMs, acceptJson = true) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetchImpl(url, {
      method: "GET",
      headers: acceptJson ? { Accept: "application/json" } : { Accept: "text/plain" },
      signal: ctrl.signal,
    });
    if (!res || !res.ok) return null;
    return acceptJson ? await res.json() : await res.text();
  } catch (_err) {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Real-time Exit IP, ASN, Country, and Datacenter vs Residential ISP probe with multi-route redundancy:
 * 1) Primary: `https://ipwho.is/` (keyless CORS JSON with ASN + ISP + Org)
 * 2) Secondary: `https://ipinfo.io/json` / `https://ipapi.co/json/` (CORS JSON with ASN + Org)
 * 3) Tertiary: `https://cloudflare.com/cdn-cgi/trace` (CORS plaintext IP + country trace)
 * 4) Offline fallback: returns `{ online: false, ip: "离线", source: "offline" }` without faking `"local"`.
 */
export async function probePublicExitNetwork(options = {}) {
  const fetchImpl = options.fetchImpl || globalThis.fetch;
  const timeoutMs = Number(options.timeoutMs) > 0 ? Number(options.timeoutMs) : 2600;

  if (typeof fetchImpl !== "function") {
    return {
      online: false,
      source: "offline",
      ip: "离线",
      asn: "",
      org: "",
      isp: "",
      countryCode: "",
      hosting: false,
    };
  }

  // Route 1: ipwho.is
  const who = await fetchWithTimeout(fetchImpl, "https://ipwho.is/", timeoutMs, true);
  if (who && who.ip && who.success !== false) {
    const asn = who.connection?.asn ? `AS${String(who.connection.asn).replace(/^AS/i, "")}` : "";
    const org = who.connection?.org || who.connection?.isp || "";
    const isp = who.connection?.isp || "";
    const countryCode = String(who.country_code || "").toUpperCase();
    const hosting = Boolean(who.security?.hosting || isDatacenterAsnOrOrg(asn, org, isp));
    return {
      online: true,
      source: "ipwho.is",
      ip: String(who.ip),
      asn,
      org,
      isp,
      countryCode,
      hosting,
    };
  }

  // Route 2: ipinfo.io/json (e.g. org: "AS16509 Amazon.com, Inc.")
  const info = await fetchWithTimeout(fetchImpl, "https://ipinfo.io/json", timeoutMs, true);
  if (info && info.ip) {
    const rawOrg = String(info.org || "").trim();
    const asnMatch = rawOrg.match(/^(AS\d+)\s*(.*)$/i);
    const asn = asnMatch ? asnMatch[1].toUpperCase() : "";
    const org = asnMatch ? asnMatch[2] || rawOrg : rawOrg;
    const countryCode = String(info.country || "").toUpperCase();
    const hosting = isDatacenterAsnOrOrg(asn, org, org);
    return {
      online: true,
      source: "ipinfo.io",
      ip: String(info.ip),
      asn,
      org,
      isp: org,
      countryCode,
      hosting,
    };
  }

  // Route 2b: ipapi.co/json/
  const ipapi = await fetchWithTimeout(fetchImpl, "https://ipapi.co/json/", timeoutMs, true);
  if (ipapi && ipapi.ip && !ipapi.error) {
    const asn = ipapi.asn ? String(ipapi.asn).toUpperCase() : "";
    const org = String(ipapi.org || "");
    const countryCode = String(ipapi.country_code || "").toUpperCase();
    const hosting = isDatacenterAsnOrOrg(asn, org, org);
    return {
      online: true,
      source: "ipapi.co",
      ip: String(ipapi.ip),
      asn,
      org,
      isp: org,
      countryCode,
      hosting,
    };
  }

  // Route 3: cloudflare.com/cdn-cgi/trace
  const cfText = await fetchWithTimeout(fetchImpl, "https://cloudflare.com/cdn-cgi/trace", timeoutMs, false);
  if (cfText) {
    const parsed = parseCloudflareTrace(cfText);
    if (parsed.ip) {
      return {
        online: true,
        source: "cloudflare-trace",
        ip: parsed.ip,
        asn: "",
        org: parsed.colo ? `Edge Colo ${parsed.colo}` : "",
        isp: "",
        countryCode: parsed.countryCode,
        hosting: false,
      };
    }
  }

  return {
    online: false,
    source: "offline",
    ip: "离线",
    asn: "",
    org: "",
    isp: "",
    countryCode: "",
    hosting: false,
  };
}

/**
 * Encrypt Pro vault export locally using WebCrypto AES-256-GCM (`CGVAULT1.<saltB64>.<ivB64>.<ctB64>`)
 */
export async function encryptVaultMarkdown(markdownText, licenseToken) {
  const subtle = globalThis.crypto?.subtle;
  if (!subtle) throw new Error("WEBCRYPTO_UNAVAILABLE");
  const salt = new Uint8Array(16);
  const iv = new Uint8Array(12);
  globalThis.crypto.getRandomValues(salt);
  globalThis.crypto.getRandomValues(iv);

  const keyMat = await subtle.importKey(
    "raw",
    new TextEncoder().encode(String(licenseToken || "claude-guard-pro")),
    "PBKDF2",
    false,
    ["deriveKey"],
  );
  const aesKey = await subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" },
    keyMat,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt"],
  );
  const ctBuf = await subtle.encrypt(
    { name: "AES-GCM", iv },
    aesKey,
    new TextEncoder().encode(String(markdownText || "")),
  );
  const toB64 = (u8) =>
    typeof Buffer !== "undefined"
      ? Buffer.from(u8).toString("base64")
      : btoa(String.fromCharCode(...u8));
  return JSON.stringify(
    {
      format: "CGVAULT1-AES256GCM",
      kdf: "PBKDF2-SHA256-100000",
      salt: toB64(salt),
      iv: toB64(iv),
      ciphertext: toB64(new Uint8Array(ctBuf)),
    },
    null,
    2,
  );
}
