import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  evaluateClaudeRisk,
  probePublicExitNetwork,
  parseCloudflareTrace,
  encryptVaultMarkdown,
  generateClaudeCodeConfig,
  formatConversationMarkdown,
  buildMigrationBundle,
  verifyLicenseUniversal,
} from "../src/guard-core.mjs";
import { MONETIZATION_CONFIG } from "../docs/affiliate-config.js";
import { issueLicense } from "../../ai-20-matrix/bin/issue-license.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

test("evaluateClaudeRisk flags datacenter ASN + Asia/Shanghai timezone mismatch as CRITICAL", () => {
  const res = evaluateClaudeRisk({
    ip: "104.28.14.88",
    asn: "AS13335",
    org: "Cloudflare, Inc.",
    countryCode: "US",
    hosting: true,
    timezone: "Asia/Shanghai",
    utcOffsetMinutes: 480,
    languages: ["zh-CN", "en-US"],
    webrtcLeakedIps: ["114.114.114.114"],
    telemetryHardened: false,
  });

  assert.equal(res.riskLevel, "CRITICAL");
  assert.ok(res.survivalScore < 40, `Expected low survival score, got ${res.survivalScore}`);
  const ids = res.findings.map((f) => f.id);
  assert.ok(ids.includes("asn-datacenter"));
  assert.ok(ids.includes("timezone-mismatch"));
  assert.ok(ids.includes("webrtc-leak"));
  assert.ok(ids.includes("cc-telemetry"));
});

test("evaluateClaudeRisk rewards clean US residential ISP with matched timezone and hardened telemetry", () => {
  const res = evaluateClaudeRisk({
    ip: "73.162.44.12",
    asn: "AS7922",
    org: "Comcast Cable Communications, LLC",
    countryCode: "US",
    hosting: false,
    timezone: "America/Los_Angeles",
    utcOffsetMinutes: -480,
    languages: ["en-US"],
    webrtcLeakedIps: [],
    telemetryHardened: true,
  });

  assert.equal(res.riskLevel, "SAFE");
  assert.ok(res.survivalScore >= 90, `Expected high survival score, got ${res.survivalScore}`);
});

test("generateClaudeCodeConfig outputs valid JSON for official-hardened, aws-bedrock, and gcp-vertex", () => {
  const bedrock = generateClaudeCodeConfig({ mode: "aws-bedrock", awsRegion: "us-west-2" });
  const parsed = JSON.parse(bedrock.settingsJson);
  assert.equal(parsed.env.CLAUDE_CODE_USE_BEDROCK, "1");
  assert.equal(parsed.env.AWS_REGION, "us-west-2");
  assert.equal(parsed.env.DISABLE_TELEMETRY, "1");

  const vertex = generateClaudeCodeConfig({ mode: "gcp-vertex", gcpProjectId: "my-gcp-123" });
  const vParsed = JSON.parse(vertex.settingsJson);
  assert.equal(vParsed.env.CLAUDE_CODE_USE_VERTEX, "1");
  assert.equal(vParsed.env.ANTHROPIC_VERTEX_PROJECT_ID, "my-gcp-123");
});

test("formatConversationMarkdown & buildMigrationBundle preserve messages and artifacts", () => {
  const sampleConv = {
    title: "Refactor Payment Webhook",
    url: "https://claude.ai/chat/abc-123",
    capturedAt: "2026-11-18T03:00:00Z",
    messages: [
      { role: "user", text: "Fix the Stripe signature verification in webhook.ts" },
      { role: "assistant", text: "Here is the patched raw body handler." },
    ],
    artifacts: [
      { title: "webhook.ts", language: "typescript", code: "export async function handleWebhook(req) { return true; }" },
    ],
  };

  const md = formatConversationMarkdown(sampleConv);
  assert.ok(md.includes("# Refactor Payment Webhook"));
  assert.ok(md.includes("```typescript"));

  const bundle = buildMigrationBundle([sampleConv]);
  assert.equal(bundle.conversationCount, 1);
  assert.equal(bundle.totalMessages, 2);
  assert.equal(bundle.totalArtifacts, 1);
  assert.ok(bundle.markdownArchive.includes("Claude Context Recovery & Account Migration Handoff"));
});

test("verifyLicenseUniversal verifies real Ed25519 OPC1 token for claude-guard", async () => {
  const issued = issueLicense({
    product: "claude-guard",
    email: "pro-buyer@example.com",
    plan: "pro",
  });

  const verified = await verifyLicenseUniversal(issued.token, "claude-guard");
  assert.equal(verified.valid, true);
  assert.equal(verified.payload.p, "claude-guard");

  const bad = await verifyLicenseUniversal(`${issued.token}tampered`, "claude-guard");
  assert.equal(bad.valid, false);

  const wildcard = issueLicense({ product: "*", email: "bundle@example.com", plan: "all-access" });
  const wildcardOk = await verifyLicenseUniversal(wildcard.token, "claude-guard");
  assert.equal(wildcardOk.valid, true);
  assert.equal(wildcardOk.payload.p, "*");
});

test("probePublicExitNetwork detects AWS/DigitalOcean/Vultr/Hetzner datacenter ASN vs residential ISP and handles offline fallback", async () => {
  // 1. Primary JSON endpoint identifies DigitalOcean datacenter ASN
  const dcRes = await probePublicExitNetwork({
    fetchImpl: async () => ({
      ok: true,
      json: async () => ({
        ip: "143.198.110.22",
        success: true,
        country_code: "US",
        connection: { asn: 14061, org: "DigitalOcean, LLC", isp: "DigitalOcean" },
      }),
    }),
  });
  assert.equal(dcRes.online, true);
  assert.equal(dcRes.asn, "AS14061");
  assert.equal(dcRes.hosting, true);

  // 2. Residential ISP detected cleanly via secondary ipinfo fallback when ipwho fails
  const resIsp = await probePublicExitNetwork({
    fetchImpl: async (url) => {
      if (url.includes("ipwho.is")) return { ok: false };
      if (url.includes("ipinfo.io")) {
        return {
          ok: true,
          json: async () => ({ ip: "73.162.88.19", country: "US", org: "AS7922 Comcast Cable Communications, LLC" }),
        };
      }
      return { ok: false };
    },
  });
  assert.equal(resIsp.online, true);
  assert.equal(resIsp.asn, "AS7922");
  assert.equal(resIsp.hosting, false);

  // 3. Tertiary Cloudflare trace fallback
  const cfTrace = parseCloudflareTrace("fl=29f12\nip=8.8.4.4\nloc=US\ncolo=LAX\n");
  assert.equal(cfTrace.ip, "8.8.4.4");
  assert.equal(cfTrace.countryCode, "US");

  // 4. Graceful offline fallback (never fakes ip: 'local')
  const offline = await probePublicExitNetwork({
    fetchImpl: async () => {
      throw new Error("ENETUNREACH");
    },
  });
  assert.equal(offline.online, false);
  assert.equal(offline.ip, "离线");
});

test("Zero-paywall & backend monetization audit: popup.js is 100% free/unlimited, supports custom/random AES-256 passphrase, zero OPC1 paywall, and full 2026 PDF synced (<20MB)", async () => {
  const popupJs = fs.readFileSync(path.join(ROOT, "extension", "popup.js"), "utf8");
  const popupHtml = fs.readFileSync(path.join(ROOT, "extension", "popup.html"), "utf8");
  assert.equal(/ip:\s*["']local["']/.test(popupJs), false, "popup.js must not hardcode fake ip: 'local'");
  assert.match(popupJs, /probePublicExitNetwork/);
  assert.match(popupJs, /const\s+proActive\s*=\s*true/);
  assert.equal(/FREE_VAULT_LIMIT/.test(popupJs), false, "popup.js must have zero FREE_VAULT_LIMIT cap");
  assert.equal(/licenseInput|verifyBtn|¥15|¥39/.test(popupHtml), false, "popup.html must remove OPC1 license paywall & ¥15/¥39 buttons");
  assert.match(popupHtml, /vaultPassphraseInput/, "popup.html must support custom/random AES-256 passphrase input");
  assert.match(popupHtml, /hubRemoteServiceLink/, "popup.html must include 1v1 remote setup backend entry");

  // AES-256-GCM local passphrase vault encryption works
  const encJson = await encryptVaultMarkdown("# Secret Chat", "my-custom-passphrase-2026");
  const parsedEnc = JSON.parse(encJson);
  assert.equal(parsedEnc.format, "CGVAULT1-AES256GCM");

  // Zero bare third-party competitor links across config, extension, and docs
  const configValues = JSON.stringify(MONETIZATION_CONFIG);
  assert.equal(/adspower|nf\.video|proxy-seller|iproyal/i.test(configValues), false, "affiliate-config.js must have zero bare competitor URLs");
  assert.match(MONETIZATION_CONFIG.agentGuardUrl, /agent-guard/);
  assert.match(MONETIZATION_CONFIG.opcToolsHubUrl, /opc-tools/);
  assert.match(MONETIZATION_CONFIG.serviceUrl, /#service/);
  assert.match(MONETIZATION_CONFIG.softwarePriceText, /¥0/);

  for (const rel of ["docs/index.html", "docs/claude-anti-ban-playbook-2026.html", "extension/popup.html", "extension/affiliate-config.js"]) {
    const content = fs.readFileSync(path.join(ROOT, rel), "utf8");
    assert.equal(/adspower\.com|nf\.video|proxy-seller\.com|iproyal\.com/i.test(content), false, `${rel} must not contain bare competitor links`);
    assert.equal(/¥15\s*单品|¥39\s*全站通票|\$4\.99|\$14\.99/.test(content), false, `${rel} must not contain legacy ¥15/¥39 license paywall copy`);
  }

  // Verify 1v1 remote setup & zero-paywall section in docs/index.html
  const indexHtml = fs.readFileSync(path.join(ROOT, "docs", "index.html"), "utf8");
  assert.match(indexHtml, /¥0\s*免费开源免码直下/);
  assert.match(indexHtml, /3152557994@qq\.com/);
  assert.match(indexHtml, /a3152557994@gmail\.com/);
  assert.match(indexHtml, /serviceModal/);

  // Verify full 2026 Anti-Ban PDF is synced and < 20MB
  const targetPdf = path.join(ROOT, "docs", "downloads", "Claude-2026-Anti-Ban-Playbook.pdf");
  const stat = fs.statSync(targetPdf);
  assert.ok(stat.size > 1_200_000, `Expected full 2026 playbook PDF (>1.2MB), got ${stat.size} bytes`);
  assert.ok(stat.size < 20 * 1024 * 1024, "PDF must be strictly < 20MB");
});
