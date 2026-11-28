# Chat Vault & Env Guard — Microsoft Edge Add-ons (¥0 免费入驻) & Chrome / Firefox 商店一键上架包

> **零门槛免费吸粉 + 后端企业云代配与联盟变现**：
> 插件 100% 免费开放无限对话本地 Markdown/JSON 归档、AES-256-GCM 本地口令加密与环境时区/ASN 风险自检，通过插件弹窗直导 `claude-guard` 主站吃「静态住宅 ISP / 企业云赠金返佣 + ¥168 AWS Bedrock/Vertex 远程无损代配」。

## 1. 待上传成品文件清单（均已通过 `web-ext lint` 0 报错校验）
- **Microsoft Edge / Chrome 商店安装包**：`../../dist/claude-guard-mv3.zip`
- **Firefox Add-ons (AMO) 商店安装包**：`../../dist/claude-guard-firefox-mv3.zip`（已含 `gecko.id` 与 `data_collection_permissions: none`，`0 errors / 0 warnings`）
- **商店主宣传截图 (`1280×800` PNG)**：`./store_screenshot_1280x800.png`
- **商店磁贴宣传图 (`440×280` PNG)**：`./store_tile_440x280.png`
- **必填公开隐私政策网址 (Privacy Policy URL)**：`https://a3152557994-ship-it.github.io/claude-guard/privacy.html`
- **官方网站网址 (Homepage URL)**：`https://a3152557994-ship-it.github.io/claude-guard/`

## 2. 商店表单直接复制粘贴文案

- **名称 (Name)**：`Chat Vault & Env Guard — Local AI Chat Backup & Network Auditor`
- **简短摘要 (Short Summary, ≤132 字)**：`100% local encrypted AI conversation & code artifact backup vault + instant timezone/WebRTC/ASN environment health check.`
- **分类 (Category)**：`Developer Tools`（开发者工具）
- **权限审核说明 (Permissions Justification — 粘贴给审核员秒过)**：
  - `storage`: Stores encrypted and plain Markdown/JSON chat snapshots strictly locally inside `chrome.storage.local`. Zero cloud sync or external upload.
  - `activeTab` & `scripting`: Invoked only on user click to capture visible conversation code blocks/messages for local backup and verify browser timezone/language consistency.
