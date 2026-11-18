# 🛡️ Claude Guard (`claude-guard`)

> **100% Local Claude Environment Ban-Risk Auditor + Claude Code 5-Provider Switcher (Bedrock / Vertex / Relay) + Chrome/Edge Manifest V3 Auto-Backup Vault Extension**
>
> **纯本地 Claude 封号风险 10 秒自检雷达 + Claude Code 防断流 5 源一键切换器 + 浏览器对话与代码块自动本地防丢备份插件（零云端上传）**

- 🌐 **Live 10-Second Risk Radar & Configurator (在线体检与配置生成台)**: [https://a3152557994-ship-it.github.io/claude-guard/](https://a3152557994-ship.github.io/claude-guard/) *(Canonical: `https://a3152557994-ship-it.github.io/claude-guard/`)*
- 🧩 **Download Chrome/Edge MV3 Extension (`.zip`)**: [claude-guard-mv3.zip](https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-guard-mv3.zip)
- ⚡ **Download Claude Code 5-Source Switcher Kit (`.zip`)**: [claude-code-kit.zip](https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-code-kit.zip)

---

## Why Claude Guard? (为什么需要它？)

1. **查清为什么被封（10-Second Local Environment Audit）**
   - 纯前端/本地 CLI 检测 **高危数据中心机房 ASN IP**（如 Cloudflare / Vultr / DigitalOcean 万人共享节点）、**WebRTC 真实公网 IP 穿透泄露**、**`Asia/Shanghai` 东八区时区与欧美 IP 跨洲错位**、以及 **Claude Code 默认遥测上报开关**。
2. **Claude Code 写代码永不断流（5-Source 1-Click Switcher）**
   - 内置 `cc-switch.sh`（macOS/Linux）、`cc-switch.ps1`（Windows）与 `env-doctor.mjs`，一键在 **官方防遥测加固模式 (`DISABLE_TELEMETRY=1`)**、**AWS Bedrock 企业级 100% 零封号通道**、**Google Cloud Vertex AI 通道**、**OpenRouter 5小时限流热备源** 与 **国产兼容兜底源** 之间秒级切换。
3. **封号也不丢一行代码（Manifest V3 Local Auto-Vault）**
   - 等账号被秒封再装导出插件已经进不去对话页了！`Claude Guard` 插件在日常对话时 **100% 本地静默保存 Markdown 与 Artifacts 代码块**，支持一键导出全量历史 + **「新账号 1 秒接续上下文恢复 Prompt」**。

---

## Quick Start (30 秒上手)

### 1. CLI Environment Doctor & Claude Code Switcher
```bash
# 1. 运行本地终端防封环境自检
node kit/env-doctor.mjs

# 2. 一键加固防遥测或切换至 AWS Bedrock / Vertex AI
./kit/cc-switch.sh
```

### 2. Install Chrome / Edge Manifest V3 Extension
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
