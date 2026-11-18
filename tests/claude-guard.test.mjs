import test from "node:test";
import assert from "node:assert/strict";
import {
  evaluateClaudeRisk,
  generateClaudeCodeConfig,
  formatConversationMarkdown,
  buildMigrationBundle,
  verifyLicenseUniversal,
} from "../src/guard-core.mjs";
import { issueLicense } from "../../ai-20-matrix/bin/issue-license.mjs";

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
});
