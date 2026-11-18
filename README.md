# 🛡️ Claude Guard (`claude-guard`)

> **100% Local Claude Environment Ban-Risk Auditor + Claude Code 5-Provider Switcher (Bedrock / Vertex / Relay) + Chrome/Edge Manifest V3 Auto-Backup Vault Extension**
>
> **纯本地 Claude 封号风险 10 秒自检雷达 + Claude Code 防断流 5 源一键切换器 + 浏览器对话与代码块自动本地防丢备份插件（零云端上传）**

- 🌐 **Live 10-Second Risk Radar & Configurator (在线体检与配置生成台)**: [https://a3152557994-ship-it.github.io/claude-guard/](https://a3152557994-ship-it.github.io/claude-guard/)
- 🧩 **Download Chrome/Edge MV3 Extension (`.zip`)**: [claude-guard-mv3.zip](https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-guard-mv3.zip)
- ⚡ **Download Claude Code 5-Source Switcher Kit (`.zip`)**: [claude-code-kit.zip](https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-code-kit.zip)
- 🤖 **Full LLM / AI Agent Context (`llms-full.txt`)**: [llms-full.txt](https://a3152557994-ship-it.github.io/claude-guard/llms-full.txt)

---

## ⚡ One-Line Terminal Audit & `cc-switch` Installer (终端一行命令自检与安装)

Run in macOS / Linux terminal to audit your local timezone, proxy env vars, and `~/.claude/settings.json` telemetry status, and install `cc-switch`:

```bash
curl -fsSL https://a3152557994-ship-it.github.io/claude-guard/install.sh | bash
```

---

## 📚 Deep-Dive Technical Guides (防封与零断流专题库)

- [Claude 账号被封 (`Account Suspended / Disabled`) 原因自查、聊天记录抢救与防封指南](https://a3152557994-ship-it.github.io/claude-guard/claude-account-banned-fix.html)
- [Claude Code 接入 AWS Bedrock 与 Google Vertex AI 零封号配置教程 (含 `settings.json`)](https://a3152557994-ship-it.github.io/claude-guard/claude-code-bedrock-vertex-setup.html)
- [`cc-switch` 多源切换教程：Claude Code 遭遇 5 小时限流如何 1 秒切备用源不断活](https://a3152557994-ship-it.github.io/claude-guard/cc-switch-multi-provider-guide.html)
- [Claude 聊天记录与 Artifacts 代码块自动本地备份导出工具 (Markdown / JSON / Obsidian)](https://a3152557994-ship-it.github.io/claude-guard/claude-chat-artifact-exporter.html)
- [Claude 防封网络环境指南：如何检测机房 ASN (`AS13335`) 与配置双 ISP 静态住宅 IP](https://a3152557994-ship-it.github.io/claude-guard/claude-static-residential-ip-guide.html)

---

## Why Claude Guard? (为什么需要它？)

1. **查清为什么被封（10-Second Local Environment Audit）**
   - 纯前端/本地 CLI 检测 **高危数据中心机房 ASN IP**（如 Cloudflare `AS13335` / Vultr `AS20473` / DigitalOcean `AS14061` 万人共享节点）、**WebRTC 真实公网 IP 穿透泄露**、**`Asia/Shanghai` 东八区时区与欧美 IP 跨洲错位**、以及 **Claude Code 默认遥测上报开关**。
2. **Claude Code 写代码永不断流（5-Source 1-Click Switcher）**
   - 内置 `cc-switch.sh`（macOS/Linux）、`cc-switch.ps1`（Windows）与 `env-doctor.mjs`，一键在 **官方防遥测加固模式 (`DISABLE_TELEMETRY=1`)**、**AWS Bedrock 企业级 100% 零封号通道 (`CLAUDE_CODE_USE_BEDROCK=1`)**、**Google Cloud Vertex AI 通道 (`CLAUDE_CODE_USE_VERTEX=1`)**、**OpenRouter 5小时限流热备源** 与 **国产兼容兜底源** 之间秒级切换。
3. **封号也不丢一行代码（Manifest V3 Local Auto-Vault）**
   - 等账号被秒封再装导出插件已经进不去对话页了！`Claude Guard` 插件在日常对话时 **100% 本地静默保存 Markdown 与 Artifacts 代码块**，支持一键导出全量历史 + **「新账号 1 秒接续上下文恢复 Prompt」**。

---

## Install Chrome / Edge Manifest V3 Extension

1. Download [`claude-guard-mv3.zip`](https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-guard-mv3.zip) and unzip it.
2. Open `chrome://extensions` or `edge://extensions` and enable **Developer mode (开发者模式)**.
3. Click **Load unpacked (加载已解压的扩展程序)** and select the unzipped folder.

---

## Pricing & Offline Ed25519 Licensing

- **Free Forever**:
  - 10-second Web & CLI Ban-Risk Scanner
  - `claude-code-kit.zip` (`cc-switch` + `env-doctor`)
  - Single-conversation `.md` & `.json` export in the MV3 browser extension
- **Pro Lifetime Buyout (`¥15 / $4.99` · 一次买断永久有效)**:
  - Unlocks **1-Click Bulk Vault Archive Export** + **Automatic New-Account Context Handoff Prompt Generator**.
  - Verified 100% offline via WebCrypto `Ed25519` (`OPC1.<payload>.<sig>`).
  - Order Key: `3152557994@qq.com` / `a3152557994@gmail.com`

## License
MIT
