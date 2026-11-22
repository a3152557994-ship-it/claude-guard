#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

function crc32(buf) {
  let c = -1;
  for (let i = 0; i < buf.length; i += 1) {
    c ^= buf[i];
    for (let k = 0; k < 8; k += 1) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
  }
  return (c ^ -1) >>> 0;
}

function pngChunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const t = Buffer.from(type, "ascii");
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([t, data])), 0);
  return Buffer.concat([len, t, data, crc]);
}

function createShieldIconPng(size) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // RGBA

  const raw = Buffer.alloc(size * (size * 4 + 1));
  const cx = size / 2;
  const rMax = size * 0.42;

  for (let y = 0; y < size; y += 1) {
    const rowStart = y * (size * 4 + 1);
    raw[rowStart] = 0;
    for (let x = 0; x < size; x += 1) {
      const p = rowStart + 1 + x * 4;
      const dx = Math.abs(x - cx);
      const inShield =
        y >= size * 0.14 &&
        y <= size * 0.86 &&
        dx <= rMax * (1 - Math.max(0, (y - size * 0.45) / (size * 0.55)) * 0.72);

      if (inShield) {
        const isBorder = dx > rMax * 0.75 || y < size * 0.22;
        if (isBorder) {
          raw[p] = 245;
          raw[p + 1] = 158;
          raw[p + 2] = 11;
          raw[p + 3] = 255;
        } else {
          raw[p] = 16;
          raw[p + 1] = 185;
          raw[p + 2] = 129;
          raw[p + 3] = 255;
        }
      } else {
        raw[p] = 15;
        raw[p + 1] = 23;
        raw[p + 2] = 42;
        raw[p + 3] = 255;
      }
    }
  }

  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const idat = zlib.deflateSync(raw);
  return Buffer.concat([sig, pngChunk("IHDR", ihdr), pngChunk("IDAT", idat), pngChunk("IEND", Buffer.alloc(0))]);
}

// 1. Sync guard-core.mjs & affiliate-config.js -> docs/ & extension/
const coreSrc = path.join(ROOT, "src", "guard-core.mjs");
fs.copyFileSync(coreSrc, path.join(ROOT, "docs", "guard-core.js"));
fs.copyFileSync(coreSrc, path.join(ROOT, "extension", "guard-core.js"));
fs.copyFileSync(
  path.join(ROOT, "docs", "affiliate-config.js"),
  path.join(ROOT, "extension", "affiliate-config.js")
);

// 2. Generate extension icons
const iconsDir = path.join(ROOT, "extension", "icons");
fs.mkdirSync(iconsDir, { recursive: true });
for (const sz of [16, 48, 128]) {
  fs.writeFileSync(path.join(iconsDir, `icon${sz}.png`), createShieldIconPng(sz));
}

// 3. Ensure chmod +x on kit scripts
for (const f of ["cc-switch.sh", "env-doctor.mjs", "bedrock-vertex-1click.sh"]) {
  const p = path.join(ROOT, "kit", f);
  if (fs.existsSync(p)) fs.chmodSync(p, 0o755);
}

// 4. Build zip packages into dist/ and docs/downloads/
const distDir = path.join(ROOT, "dist");
const dlDir = path.join(ROOT, "docs", "downloads");
fs.mkdirSync(distDir, { recursive: true });
fs.mkdirSync(dlDir, { recursive: true });

// Sync 2026 Anti-Ban PDF into docs/downloads/
const playbookPdfSrc = path.join(ROOT, "release", "anti-ban-playbook-2026", "Claude-2026防封号与退款自救实战全书.pdf");
if (fs.existsSync(playbookPdfSrc)) {
  fs.copyFileSync(playbookPdfSrc, path.join(dlDir, "Claude-2026-Anti-Ban-Playbook.pdf"));
}

const mv3ZipDist = path.join(distDir, "claude-guard-mv3.zip");
const kitZipDist = path.join(distDir, "claude-code-kit.zip");

if (fs.existsSync(mv3ZipDist)) fs.unlinkSync(mv3ZipDist);
if (fs.existsSync(kitZipDist)) fs.unlinkSync(kitZipDist);

execSync(`cd "${path.join(ROOT, "extension")}" && zip -rq "${mv3ZipDist}" .`);
execSync(`cd "${path.join(ROOT, "kit")}" && zip -rq "${kitZipDist}" .`);

fs.copyFileSync(mv3ZipDist, path.join(dlDir, "claude-guard-mv3.zip"));
fs.copyFileSync(kitZipDist, path.join(dlDir, "claude-code-kit.zip"));

console.log("✅ Built packages:");
console.log("  -", mv3ZipDist);
console.log("  -", kitZipDist);
console.log("  - Synced to docs/downloads/ for GitHub Pages direct download");
