# 🛡️ Claude Guard — Claude Code 不断流 5 源切换与防封急救手册

> 在线 10 秒 IP/ASN/WebRTC 体检台：https://a3152557994-ship-it.github.io/claude-guard/

---

## 一、 为什么你的 Claude / Claude Code 总是被封号？

1. **千人共用机场/机房 ASN IP**：Cloudflare、Vultr、DigitalOcean、搬瓦工等数据中心 IP 早已被加入高危 ASN 列表，同节点有人违规整批连坐。
2. **本地时区与出口 IP 跨洲错位**：挂着美国节点，但浏览器或终端直接暴露 `Asia/Shanghai (UTC+8)` 时区与默认遥测请求。
3. **廉价虚拟卡代充与多人拼车**：Stripe 账单回滚或同一账号多设备异地登录，100% 触发秒封。

---

## 二、 3 分钟一劳永逸解决方案（本工具包用法）

### 第 1 步：运行本地终端体检（查漏点）
在终端进入解压后的文件夹，运行：

```bash
node env-doctor.mjs
```

### 第 2 步：一键加固防遥测 / 切换至永不封号源
- **macOS / Linux 用户**：
  ```bash
  chmod +x cc-switch.sh
  ./cc-switch.sh
  ```
- **Windows 用户（PowerShell）**：
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\cc-switch.ps1
  ```

支持 5 种模式秒级切换（自动备份原配置）：
1. **官方账号 · 隐私防遥测加固模式**：自动注入 `DISABLE_TELEMETRY=1`、`DISABLE_ERROR_REPORTING=1`、`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`。
2. **AWS Bedrock 企业级直连模式（最稳推荐）**：走亚马逊云商业 API，**100% 绝不封号**，按实际消耗 Token 计费。
3. **Google Cloud Vertex AI 模式**：走谷歌云商业通道，同样 **100% 不封号**，且可直接消耗 GCP 开发者赠金。
4. **OpenRouter / 合规聚合网关模式**：当官方 Pro/Max 触发 5 小时限流窗时，1 秒切过去继续交活不断流。
5. **国产兼容源应急兜底模式**：支持 DeepSeek / 智谱 GLM 等 Anthropic 兼容接口，断网或月底救急零焦虑。

---

## 三、 网页版 Claude Pro / Max 独享防封与防丢配套

1. **网页端防封环境黄金组合**：
   - 使用**独享双 ISP 静态原生住宅 IP**（如 Proxy-Seller / IPRoyal 美英新原生家宽），拒绝万人机房节点；
   - 配合 **AdsPower 防关联指纹浏览器**，将浏览器时区、WebRTC、语言与静态住宅 IP 所在地 100% 锁定对齐。
2. **装上 `Claude Guard` 浏览器自动防丢备份插件（MV3）**：
   - 解压 `claude-guard-mv3.zip` → 打开 `chrome://extensions` 或 `edge://extensions` → 开启右上角「开发者模式」→ 点击「加载已解压的扩展程序」；
   - 日常聊天自动在本地保存对话与代码块，哪怕遇到突发封号也能一键导出全量 Markdown 与**「新号 1 秒接续上下文恢复 Prompt」**。
