/**
 * Claude Guard 商业变现与联盟返佣全局配置 (affiliate-config.js)
 * 老板后续只需修改此文件中的链接，全站诊断卡片与推荐位自动生效。
 */
export const MONETIZATION_CONFIG = {
  // 1. 静态原生住宅 IP 联盟链接 (Proxy-Seller 最高 50% 佣金 / IPRoyal 10% 终身循环)
  residentialProxyUrl: "https://proxy-seller.com/?partner=CLAUDEGUARD",
  residentialProxyBackupUrl: "https://iproyal.com/?r=claudeguard",

  // 2. 防关联指纹浏览器联盟链接 (AdsPower 最高 30% 订阅分成)
  antidetectBrowserUrl: "https://www.adspower.com/share?code=claudeguard",

  // 3. 合规 API 聚合网关 (OpenRouter / AWS Bedrock 指引)
  apiGatewayUrl: "https://openrouter.ai/",

  // 4. 自营产品下载与购买通道
  mv3ExtensionZipUrl: "./downloads/claude-guard-mv3.zip",
  ccKitZipUrl: "./downloads/claude-code-kit.zip",
  opcToolsHubUrl: "https://a3152557994-ship-it.github.io/opc-tools/",
  orderEmail: "3152557994@qq.com",
  backupEmail: "a3152557994@gmail.com",
  proPriceText: "¥15 / $4.99 终身买断",
  kitPriceText: "¥9.9 懒人包 / ¥49 远程代配",
};
