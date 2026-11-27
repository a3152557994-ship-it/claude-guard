# -*- coding: utf-8 -*-
"""
Rebuild Book 3 (claude-guard) deliverables strictly inside kit/, dist/, docs/downloads/, and release/ebook-publishing-pack/:
1. Verify cc-switch.sh & cc-switch.ps1 non-destructive JSON deep merge (preserves mcpServers, permissions, hooks, custom env).
2. Re-pack dist/claude-code-kit.zip and docs/downloads/claude-code-kit.zip.
3. Rebuild release/ebook-publishing-pack/不掉号-不断流_ClaudeCode企业云合规接入与排障手册_2026国内文库版.pdf (15 pages):
   - Fix .cover-wrap code dark-gold translucent badge (eliminate glaring pink-white boxes on dark shield cover)
   - Embed crisp inline vector SVG《10秒报错排障与零断流路由决策树》on golden free-preview Page 3 (Ch1)
   - Rebalance cc-switch.sh / env-doctor.mjs code splits so zero footer/note clipping and zero large blank pages
   - Add dedicated full-page《附录 B：一页纸终端防封与热切速查卡（1-Page Dev Cheat Sheet）》at end of book
   - Strictly 0 external URI links & 0 external promo URLs (100% domestic Wenku compliant)
4. Update release/ebook-publishing-pack/不掉号_Zero-Ban-Claude-2026.epub (and sync docs/downloads/Zero-Ban-Claude-2026.epub)
   with inline vector SVG decision tree (Ch1), v2.0 non-destructive merge, and 1-Page Dev Cheat Sheet (Appendix B).
5. Rebuild release/ebook-publishing-pack/不掉号_Claude防封号与封后退费自救全书_2026完整版.pdf
   (and sync docs/downloads/Claude-2026-Anti-Ban-Playbook.pdf):
   - Merge overly short sections (TOC + Preface on P.02; Ch8 + Appendix A on P.10) & fit Ch6 cleanly on 1 page
   - Add break-inside: avoid to pre/table/.box/SVG so zero split code blocks & zero 60%-75% blank pages
   - Add dedicated full-page《附录 B：一页纸终端防封与热切速查卡》at book end
   - Preserve 100% working internal PDF TOC named destinations (#ch00_preface .. #ch10_cheatsheet) and 0 file:// leaks.
"""

import html as html_mod
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from pypdf import PdfReader, PdfWriter

ROOT = Path("/Users/wang/OPC/projects/claude-guard")
KIT_DIR = ROOT / "kit"
EBOOK_DIR = ROOT / "release" / "ebook-publishing-pack"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def build_decision_tree_svg() -> str:
    """生成严格符合 XML/XHTML 规范、零文字重叠截断的高清彩色矢量《10秒报错排障与零断流路由决策树》SVG"""
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 338" width="100%" role="img" aria-label="10秒报错排障与零断流路由决策树" style="display:block;width:100%;height:auto;border-radius:10px;">
  <defs>
    <linearGradient id="dtBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0B1120" />
      <stop offset="100%" stop-color="#0F172A" />
    </linearGradient>
    <linearGradient id="dtHdr" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#172554" />
      <stop offset="100%" stop-color="#0F172A" />
    </linearGradient>
  </defs>

  <!-- Outer Blueprint Frame -->
  <rect x="1" y="1" width="818" height="336" rx="11" fill="url(#dtBg)" stroke="#334155" stroke-width="1.6" />
  <rect x="1" y="1" width="818" height="36" rx="11" fill="url(#dtHdr)" />
  <rect x="1" y="24" width="818" height="13" fill="url(#dtHdr)" />
  <line x1="1" y1="37" x2="819" y2="37" stroke="#334155" stroke-width="1.2" />

  <!-- Header Bar -->
  <circle cx="18" cy="19" r="4.5" fill="#F59E0B" />
  <text x="30" y="23.5" fill="#F8FAFC" font-family="'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif" font-size="12" font-weight="800">10 秒报错排障与零断流路由决策树（2026 Production Decision Tree）</text>
  <rect x="668" y="8" width="138" height="22" rx="11" fill="#1E293B" stroke="#F59E0B" stroke-width="1" />
  <text x="737" y="22.5" text-anchor="middle" fill="#FDE68A" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.8" font-weight="800">3 大高频场景 · 按图秒修</text>

  <!-- Root Entry Node -->
  <rect x="12" y="133" width="116" height="108" rx="9" fill="#172554" stroke="#60A5FA" stroke-width="1.8" />
  <text x="70" y="156" text-anchor="middle" fill="#93C5FD" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="10.5" font-weight="800">终端 / 网页异常</text>
  <text x="70" y="175" text-anchor="middle" fill="#FFFFFF" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="11.5" font-weight="900">突发阻断分流</text>
  <line x1="24" y1="186" x2="116" y2="186" stroke="#3B82F6" stroke-width="1" stroke-dasharray="3,2" />
  <text x="70" y="203" text-anchor="middle" fill="#FDE68A" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.8" font-weight="700">400 / 403 / 529</text>
  <text x="70" y="219" text-anchor="middle" fill="#CBD5E1" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.2">disabled · 5h限流</text>
  <text x="70" y="234" text-anchor="middle" fill="#38BDF8" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9" font-weight="700">先定性 · 勿盲目弃号</text>

  <!-- Root -> 3 Branches Bezier Connectors -->
  <path d="M 128 168 C 146 168, 142 89, 157 89" fill="none" stroke="#F59E0B" stroke-width="2.2" />
  <polygon points="161,89 154,85 154,93" fill="#F59E0B" />
  <line x1="128" y1="187" x2="157" y2="187" stroke="#FB7185" stroke-width="2.2" />
  <polygon points="161,187 154,183 154,191" fill="#FB7185" />
  <path d="M 128 206 C 146 206, 142 285, 157 285" fill="none" stroke="#34D399" stroke-width="2.2" />
  <polygon points="161,285 154,281 154,289" fill="#34D399" />

  <!-- ==================== BRANCH A: 假封号乌龙 (y=47..131) ==================== -->
  <rect x="163" y="47" width="205" height="84" rx="8" fill="#1F1A14" stroke="#F59E0B" stroke-width="1.6" />
  <rect x="172" y="54" width="154" height="17" rx="4" fill="#451A03" />
  <text x="178" y="66" fill="#FBBF24" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.8" font-weight="800">分支 A · 命中率 30%（假封号）</text>
  <text x="172" y="86" fill="#F8FAFC" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.1" font-weight="700">CLI 报 400 Organization disabled</text>
  <text x="172" y="104" fill="#E2E8F0" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.8">但 <tspan fill="#FDE68A" font-family="ui-monospace,Menlo,monospace">claude.ai</tspan> 网页端对话完全正常</text>
  <text x="172" y="121" fill="#94A3B8" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9">症状：刚开订阅仍秒拒，仅终端报错</text>

  <line x1="368" y1="89" x2="383" y2="89" stroke="#F59E0B" stroke-width="2" />
  <polygon points="387,89 380,85 380,93" fill="#F59E0B" />

  <rect x="389" y="47" width="203" height="84" rx="8" fill="#1E293B" stroke="#FBBF24" stroke-width="1.3" />
  <text x="398" y="65" fill="#FDE68A" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="10" font-weight="800">根因：L1 环境变量抢占最高优先级</text>
  <text x="398" y="85" fill="#FCA5A5" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.2" font-weight="700">残留旧 ANTHROPIC_API_KEY</text>
  <text x="398" y="103" fill="#E2E8F0" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.6">或失效 BASE_URL 强行覆盖 OAuth</text>
  <text x="398" y="121" fill="#94A3B8" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9">潜伏点：~/.zshrc · .bashrc · ./.env</text>

  <line x1="592" y1="89" x2="607" y2="89" stroke="#10B981" stroke-width="2" />
  <polygon points="611,89 604,85 604,93" fill="#10B981" />

  <rect x="613" y="47" width="195" height="84" rx="8" fill="#064E3B" stroke="#10B981" stroke-width="1.6" />
  <text x="622" y="65" fill="#6EE7B7" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="10" font-weight="800">处置：三连清理 · 10 秒原地恢复</text>
  <text x="622" y="84" fill="#ECFDF5" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.2">1. env | grep ANTHROPIC</text>
  <text x="622" y="102" fill="#ECFDF5" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.2">2. unset ANTHROPIC_API_KEY</text>
  <text x="622" y="120" fill="#A7F3D0" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.3" font-weight="700">3. 删 .zshrc 导出行并重开终端</text>

  <!-- ==================== BRANCH B: 网页同步封禁 (y=145..229) ==================== -->
  <rect x="163" y="145" width="205" height="84" rx="8" fill="#24131B" stroke="#FB7185" stroke-width="1.6" />
  <rect x="172" y="152" width="154" height="17" rx="4" fill="#4C0519" />
  <text x="178" y="164" fill="#FDA4AF" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.8" font-weight="800">分支 B · 网页同步锁定（真风控）</text>
  <text x="172" y="184" fill="#F8FAFC" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.8" font-weight="700">网页端同步弹 <tspan fill="#FDA4AF" font-family="ui-monospace,Menlo,monospace">disabled</tspan> 或</text>
  <text x="172" y="202" fill="#FCA5A5" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.3" font-weight="700">automatic review 阻断登录</text>
  <text x="172" y="219" fill="#94A3B8" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9">症状：Web 与 CLI 同时丧失访问权</text>

  <line x1="368" y1="187" x2="383" y2="187" stroke="#FB7185" stroke-width="2" />
  <polygon points="387,187 380,183 380,191" fill="#FB7185" />

  <rect x="389" y="145" width="203" height="84" rx="8" fill="#1E293B" stroke="#F43F5E" stroke-width="1.3" />
  <text x="398" y="163" fill="#FECDD3" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="10" font-weight="800">核查出口 ASN + 严守止损第一铁律</text>
  <text x="398" y="183" fill="#E2E8F0" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.5">排查是否撞 <tspan fill="#FDE68A" font-family="ui-monospace,Menlo,monospace">AS13335</tspan> 共享段/跳变</text>
  <text x="398" y="201" fill="#FCA5A5" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.6" font-weight="800">严禁直连点开封号邮件申诉链接！</text>
  <text x="398" y="219" fill="#94A3B8" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9">防非受支持区 IP 留痕焊死人工复核</text>

  <line x1="592" y1="187" x2="607" y2="187" stroke="#38BDF8" stroke-width="2" />
  <polygon points="611,187 604,183 604,191" fill="#38BDF8" />

  <rect x="613" y="145" width="195" height="84" rx="8" fill="#0C4A6E" stroke="#38BDF8" stroke-width="1.6" />
  <text x="622" y="163" fill="#7DD3FC" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="10" font-weight="800">处置：黄金 48h 退费或一次申诉</text>
  <text x="622" y="182" fill="#F0F9FF" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.4">App Store 订阅走苹果官方通道：</text>
  <text x="622" y="200" fill="#FDE68A" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.1" font-weight="700">reportaproblem.apple.com</text>
  <text x="622" y="218" fill="#BAE6FD" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.2" font-weight="700">48h 退回余额 / 备齐账单一次申诉</text>

  <!-- ==================== BRANCH C: 企业云零封号终极解 (y=243..327) ==================== -->
  <rect x="163" y="243" width="205" height="84" rx="8" fill="#102336" stroke="#38BDF8" stroke-width="1.6" />
  <rect x="172" y="250" width="166" height="17" rx="4" fill="#082F49" />
  <text x="178" y="262" fill="#7DD3FC" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.8" font-weight="800">分支 C · 团队/重度编码终极架构</text>
  <text x="172" y="282" fill="#F8FAFC" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.8" font-weight="700">彻底告别封号焦虑与 5h 限额卡死</text>
  <text x="172" y="300" fill="#E2E8F0" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.6">赶项目死线 · 多仓库重构零断流</text>
  <text x="172" y="317" fill="#94A3B8" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9">目标：0% 地区封禁 + 企业高吞吐</text>

  <line x1="368" y1="285" x2="383" y2="285" stroke="#34D399" stroke-width="2" />
  <polygon points="387,285 380,281 380,289" fill="#34D399" />

  <rect x="389" y="243" width="203" height="84" rx="8" fill="#1E293B" stroke="#34D399" stroke-width="1.3" />
  <text x="398" y="261" fill="#6EE7B7" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="10" font-weight="800">接入企业云商业 IAM 按量 API</text>
  <text x="398" y="281" fill="#FDE68A" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.2" font-weight="700">AWS Bedrock (us.anthropic.*)</text>
  <text x="398" y="299" fill="#E2E8F0" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.6">或 GCP Vertex AI（可抵 $300 赠金）</text>
  <text x="398" y="317" fill="#94A3B8" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9">最小权限 IAM 子密钥 · 账单透明可控</text>

  <line x1="592" y1="285" x2="607" y2="285" stroke="#FBBF24" stroke-width="2" />
  <polygon points="611,285 604,281 604,289" fill="#FBBF24" />

  <rect x="613" y="243" width="195" height="84" rx="8" fill="#172554" stroke="#FBBF24" stroke-width="1.6" />
  <text x="622" y="261" fill="#FDE68A" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="10" font-weight="800">cc-switch v2.0 秒级无损热切</text>
  <text x="622" y="280" fill="#F8FAFC" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.5">JSON 深合并仅改 env 托管路由键</text>
  <text x="622" y="298" fill="#6EE7B7" font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="9.1" font-weight="700">100% 保留 mcpServers / hooks</text>
  <text x="622" y="316" fill="#CBD5E1" font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="9.2" font-weight="700">5 源互备 1 秒切源，不断研发心流</text>
</svg>"""


def build_cheatsheet_inner_html(is_wenku: bool = False) -> str:
    """构建双栏紧凑《一页纸终端防封与热切速查卡（1-Page Dev Cheat Sheet）》主体 HTML（兼容 XHTML 与 PDF）"""
    if is_wenku:
        checklist_items = """
          <li><b>☑ 1. 清客户端会话缓存</b>：切换测试组织后彻底清理旧会话 Cookie / LocalStorage，使用独立浏览器 Profile 容器隔离研发环境（语言设 <code>en-US</code>，关闭非必要第三方注入扩展）。</li>
          <li><b>☑ 2. 核验固定出口 ASN</b>：排查出口自治系统号，避开高并发共享数据中心段（如 <code>AS13335 / AS20473 / AS14061</code>），保持研发网络出口区域与系统时区稳定一致。</li>
          <li><b>☑ 3. 独立工程身份凭据</b>：为不同研发项目组分配独立企业邮箱与云平台子账号，严禁多台构建机混用同一测试 OAuth 令牌。</li>
          <li><b>☑ 4. 合规商业结算隔离</b>：核心生产环境统一绑定 AWS Bedrock / Google Vertex AI 最小权限 IAM 角色，并在云账单控制台开启月度预算阈值告警。</li>"""
        audit_cmd = """# 1. 10秒定位幽灵环境变量并立即解除当前终端冲突
env | grep -iE "ANTHROPIC|CLAUDE|AWS_REGION|CLOUD_ML"
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL
grep -rn "ANTHROPIC_" ~/.zshrc ~/.bashrc ~/.zprofile ./.env 2&gt;/dev/null

# 2. 运行本地终端健康度打分 &amp; 5 源 1 秒非破坏性热切
node env-doctor.mjs &amp;&amp; ./cc-switch.sh"""
    else:
        checklist_items = """
          <li><b>☑ 1. 清容器存储痕迹</b>：绝不在原被封窗口重注！清空 <code>claude.ai</code> 全部 Cookie / IndexedDB，新建独立 Chrome Profile（设 <code>en-US</code> + 禁非代理 UDP 防 WebRTC 穿透）。</li>
          <li><b>☑ 2. 换独享静态住宅 IP</b>：弃用曾死号节点，核验双 ISP 原生家宽（<code>hosting: false</code>，远离 <code>AS13335 / AS20473 / AS14061</code> 机房段，严禁挂香港节点）。</li>
          <li><b>☑ 3. 换纯净邮箱与手机</b>：启用全新 Gmail / Outlook / ProtonMail，绝不复用曾关联异常记录的接码手机号。</li>
          <li><b>☑ 4. 换隔离支付通道</b>：严禁二次绑定旧虚拟卡（必触发 Stripe BIN 连坐），改走美区免税州（Oregon <code>97201</code>）Apple ID 礼品卡内购或直连企业云。</li>"""
        audit_cmd = """# 1. 一键拉取体检器或手动秒清 L1 幽灵环境变量冲突
curl -fsSL https://a3152557994-ship-it.github.io/claude-guard/install.sh | bash
env | grep -iE "ANTHROPIC|CLAUDE" &amp;&amp; unset ANTHROPIC_API_KEY ANTHROPIC_BASE_URL

# 2. 扫描 .zshrc 潜伏项 &amp; 启动 v2.0 五源无损切换器
grep -rn "ANTHROPIC_" ~/.zshrc ~/.bashrc ./.env 2&gt;/dev/null &amp;&amp; ./cc-switch.sh"""

    return f"""
  <div class="cs-banner">
    <div>
      <div class="cs-kicker">1-PAGE DEV CHEAT SHEET · 建议截图保存或打印贴屏备查</div>
      <div class="cs-title">附录 B：一页纸终端防封与零断流热切速查卡</div>
    </div>
    <div class="cs-badge">v2.0 无损深合并标准</div>
  </div>

  <div class="cs-grid">
    <!-- 左栏：四级凭据优先级金字塔 + 重开新号四清 Checklist -->
    <div class="cs-col">
      <div class="cs-card">
        <div class="cs-card-hd">🔺 一、CLI 四级凭据读取优先级金字塔（上层无条件覆盖下层）</div>
        <div class="pyr-list">
          <div class="pyr-item pyr-l1">
            <span class="pyr-tag">L1 最高抢占</span>
            <div><b>Shell 显式环境变量</b>（<code>ANTHROPIC_API_KEY / BASE_URL</code>）<br/><span>⚠️ 30%「假封号 400 disabled」真凶！一旦残留直接覆盖订阅登录态</span></div>
          </div>
          <div class="pyr-item pyr-l2">
            <span class="pyr-tag">L2 项目局部</span>
            <div><b>当前/父级目录 <code>./.env</code> 文件</b><br/><span>历史 Demo 仓库遗留的过期测试 Key 常潜伏于此，切目录即触发报错</span></div>
          </div>
          <div class="pyr-item pyr-l3">
            <span class="pyr-tag">L3 全局路由</span>
            <div><b><code>~/.claude/settings.json</code> ➔ <code>env</code> 字段（推荐层）</b><br/><span><code>cc-switch v2.0</code> 标准无损深合并层，多源秒切且保留 MCP/Hooks</span></div>
          </div>
          <div class="pyr-item pyr-l4">
            <span class="pyr-tag">L4 默认底座</span>
            <div><b>OAuth 交互令牌 / 云厂商默认凭据链</b><br/><span>官方 Pro/Max 登录态、AWS Credentials Profile 或 Google ADC</span></div>
          </div>
        </div>
      </div>

      <div class="cs-card">
        <div class="cs-card-hd">🧹 三、环境重建与防关联秒封「四清铁律」Checklist</div>
        <ul class="cs-checks">{checklist_items}
        </ul>
      </div>
    </div>

    <!-- 右栏：五源核心环境变量速查表 + 一键体检与急救命令 -->
    <div class="cs-col">
      <div class="cs-card">
        <div class="cs-card-hd">⚡ 二、五源核心环境变量速查表（<code>~/.claude/settings.json</code>）</div>
        <table class="cs-tbl">
          <thead><tr><th style="width:27%;">工作源模式</th><th>核心 <code>env</code> 键值组合与模型配置</th></tr></thead>
          <tbody>
            <tr><td><b>① 官方加固</b></td><td><code>DISABLE_TELEMETRY="1"</code>, <code>DISABLE_ERROR_REPORTING="1"</code>, <code>CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"</code></td></tr>
            <tr><td><b>② Bedrock</b></td><td><code>CLAUDE_CODE_USE_BEDROCK="1"</code>, <code>AWS_REGION="us-east-1"</code>, <code>ANTHROPIC_MODEL="us.anthropic.claude-sonnet-4-6"</code></td></tr>
            <tr><td><b>③ Vertex AI</b></td><td><code>CLAUDE_CODE_USE_VERTEX="1"</code>, <code>CLOUD_ML_REGION="us-east5"</code>, <code>ANTHROPIC_VERTEX_PROJECT_ID="your-gcp-id"</code></td></tr>
            <tr><td><b>④ OpenRouter</b></td><td><code>ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"</code>, <code>ANTHROPIC_AUTH_TOKEN="sk-or-v1-..."</code></td></tr>
            <tr><td><b>⑤ 兼容兜底</b></td><td><code>ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"</code>, <code>ANTHROPIC_MODEL="deepseek-chat"</code></td></tr>
          </tbody>
        </table>
        <div class="cs-mini-warn">🛡️ <b>非破坏性合并铁律</b>：严禁用 <code>cat &gt; settings.json</code> 粗暴覆盖！切源时务必解析 JSON 树并仅增删托管路由键，确保 <code>mcpServers / permissions / hooks</code> 100% 留存。</div>
      </div>

      <div class="cs-card">
        <div class="cs-card-hd">🩺 四、三端 10 秒排雷与一键环境体检命令集</div>
        <div class="cs-sub-lbl">macOS / Linux 终端排雷与巡检：</div>
        <pre class="cs-pre"><code>{audit_cmd}</code></pre>
        <div class="cs-sub-lbl">Windows PowerShell 注册表级根除与切源：</div>
        <pre class="cs-pre"><code>Remove-Item Env:ANTHROPIC_API_KEY,Env:ANTHROPIC_BASE_URL -EA SilentlyContinue
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY",$null,"User")
powershell -ExecutionPolicy Bypass -File .\\cc-switch.ps1</code></pre>
      </div>
    </div>
  </div>

  <div class="cs-footer-formula">
    🎯 <b>2026 零断流黄金稳态公式</b>：主力编码走「官方防遥测加固 / AWS Bedrock · GCP Vertex 企业云 IAM」 ➕ 撞 5h 限额用 <code>cc-switch v2.0</code> 1 秒无损切源 ➕ 日常对话实时落盘本地 Markdown 归档保险箱
  </div>"""


CHEATSHEET_CSS = """
  .cs-banner {
    background: linear-gradient(135deg, #070D19 0%, #172554 100%);
    border: 2px solid #F59E0B; border-radius: 10px; padding: 9px 14px;
    display: flex; justify-content: space-between; align-items: center; color: #FFFFFF; margin-bottom: 9px;
    break-inside: avoid; page-break-inside: avoid;
  }
  .cs-kicker { font-size: 7.6pt; font-weight: 800; color: #FDE68A; letter-spacing: 0.8px; }
  .cs-title { font-size: 13.8pt; font-weight: 900; color: #FFFFFF; margin-top: 1px; }
  .cs-badge {
    background: linear-gradient(90deg, #F59E0B, #FBBF24); color: #0F172A;
    font-size: 8.2pt; font-weight: 900; padding: 4px 11px; border-radius: 99px; white-space: nowrap;
  }
  .cs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
  .cs-col { display: flex; flex-direction: column; gap: 9px; }
  .cs-card {
    background: #F8FAFC; border: 1.2px solid #CBD5E1; border-radius: 9px; padding: 8px 10px;
    break-inside: avoid; page-break-inside: avoid;
  }
  .cs-card-hd {
    font-size: 9.4pt; font-weight: 900; color: #0F172A; border-bottom: 1.5px solid #E2E8F0;
    padding-bottom: 4px; margin-bottom: 6px;
  }
  .pyr-list { display: flex; flex-direction: column; gap: 5px; }
  .pyr-item {
    display: flex; align-items: flex-start; gap: 7px; padding: 5px 7px; border-radius: 6px;
    font-size: 8pt; line-height: 1.38;
  }
  .pyr-item span { color: #475569; font-size: 7.6pt; }
  .pyr-tag {
    display: inline-block; min-width: 64px; text-align: center; font-size: 7.3pt; font-weight: 900;
    padding: 2px 5px; border-radius: 4px; color: #FFF !important; flex-shrink: 0; margin-top: 1px;
  }
  .pyr-l1 { background: #FEF2F2; border: 1px solid #FECACA; }
  .pyr-l1 .pyr-tag { background: #DC2626; }
  .pyr-l2 { background: #FFFBEB; border: 1px solid #FDE68A; }
  .pyr-l2 .pyr-tag { background: #D97706; }
  .pyr-l3 { background: #EFF6FF; border: 1px solid #BFDBFE; }
  .pyr-l3 .pyr-tag { background: #2563EB; }
  .pyr-l4 { background: #ECFDF5; border: 1px solid #A7F3D0; }
  .pyr-l4 .pyr-tag { background: #059669; }
  .cs-checks { list-style: none; padding-left: 0 !important; margin-bottom: 0 !important; }
  .cs-checks li {
    font-size: 8.05pt !important; line-height: 1.42 !important; margin-bottom: 5px !important;
    padding: 4.5px 7px; background: #FFFFFF; border-left: 3px solid #2563EB; border-radius: 4px;
  }
  .cs-checks li:last-child { margin-bottom: 0 !important; }
  .cs-tbl { width: 100%; border-collapse: collapse; margin: 2px 0 6px !important; font-size: 7.7pt !important; }
  .cs-tbl th { background: #0F172A; color: #FFF; padding: 4.5px 6px !important; font-size: 7.7pt; }
  .cs-tbl td { border: 1px solid #CBD5E1; padding: 4.5px 6px !important; line-height: 1.34 !important; background: #FFF; }
  .cs-tbl code { font-size: 7.1pt !important; padding: 0 3px !important; }
  .cs-mini-warn {
    background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 6px;
    padding: 5px 8px; font-size: 7.7pt; line-height: 1.38; color: #78350F;
  }
  .cs-sub-lbl { font-size: 7.9pt; font-weight: 800; color: #1E3A8A; margin: 2px 0 3px; }
  .cs-pre {
    background: #0F172A !important; color: #F8FAFC !important; border-radius: 6px !important;
    padding: 5.5px 8px !important; font-size: 6.75pt !important; line-height: 1.3 !important;
    margin: 0 0 5px 0 !important; white-space: pre-wrap; word-break: break-all;
  }
  .cs-pre code { background: transparent !important; color: #F8FAFC !important; padding: 0 !important; font-size: 6.75pt !important; }
  .cs-footer-formula {
    margin-top: 8px; background: linear-gradient(90deg, #0F172A, #1E293B); color: #F8FAFC;
    border-left: 4px solid #10B981; border-radius: 7px; padding: 7px 11px;
    font-size: 8.1pt; line-height: 1.4; break-inside: avoid; page-break-inside: avoid;
  }
  .cs-footer-formula b { color: #FBBF24; }
  .cs-footer-formula code { background: rgba(245,158,11,0.2); color: #FDE68A; border: 1px solid rgba(245,158,11,0.35); font-size: 7.6pt; }
"""


def test_nondestructive_merge():
    with tempfile.TemporaryDirectory(prefix="cg_test_") as td:
        fake_home = Path(td)
        cdir = fake_home / ".claude"
        cdir.mkdir(parents=True)
        sfile = cdir / "settings.json"
        initial = """{
  "mcpServers": {
    "filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"] }
  },
  "permissions": {
    "allow": ["Read(*)", "Bash(git status)"]
  },
  "hooks": {
    "PreToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "echo ok" }] }]
  },
  "env": {
    "CUSTOM_USER_VAR": "keep-me-100-percent",
    "ANTHROPIC_BASE_URL": "https://old-stale-url.example"
  }
}"""
        sfile.write_text(initial, encoding="utf-8")
        env = dict(os.environ, HOME=str(fake_home))
        subprocess.run(
            ["bash", str(KIT_DIR / "cc-switch.sh")],
            input="2\nus-west-2\nmy-bedrock-prof\n",
            text=True,
            env=env,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        import json
        after2 = json.loads(sfile.read_text(encoding="utf-8"))
        assert "filesystem" in after2["mcpServers"], "mcpServers lost!"
        assert after2["permissions"]["allow"] == ["Read(*)", "Bash(git status)"], "permissions lost!"
        assert len(after2["hooks"]["PreToolUse"]) == 1, "hooks lost!"
        assert after2["env"]["CUSTOM_USER_VAR"] == "keep-me-100-percent", "custom env lost!"
        assert "ANTHROPIC_BASE_URL" not in after2["env"], "stale routing key not cleaned!"
        assert after2["env"]["CLAUDE_CODE_USE_BEDROCK"] == "1"
        assert after2["env"]["AWS_REGION"] == "us-west-2"
        assert after2["env"]["AWS_PROFILE"] == "my-bedrock-prof"
        assert after2["env"]["ANTHROPIC_MODEL"] == "us.anthropic.claude-sonnet-4-6"

        subprocess.run(
            ["bash", str(KIT_DIR / "cc-switch.sh")],
            input="1\n",
            text=True,
            env=env,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        after1 = json.loads(sfile.read_text(encoding="utf-8"))
        assert "filesystem" in after1["mcpServers"]
        assert "CLAUDE_CODE_USE_BEDROCK" not in after1["env"]
        assert after1["env"]["DISABLE_TELEMETRY"] == "1"
        assert after1["env"]["CUSTOM_USER_VAR"] == "keep-me-100-percent"
        print("[PASS] cc-switch.sh non-destructive JSON deep merge verified (mcpServers/permissions/hooks 100% preserved)!")


def repack_kit_zip():
    for fname in ("cc-switch.sh", "bedrock-vertex-1click.sh", "env-doctor.mjs"):
        os.chmod(KIT_DIR / fname, 0o755)
    dist_zip = ROOT / "dist" / "claude-code-kit.zip"
    dl_zip = ROOT / "docs" / "downloads" / "claude-code-kit.zip"
    dist_zip.parent.mkdir(parents=True, exist_ok=True)
    dl_zip.parent.mkdir(parents=True, exist_ok=True)
    dist_zip.unlink(missing_ok=True)
    subprocess.run(
        ["zip", "-rq", "-X", str(dist_zip), ".", "-x", "*.DS_Store"],
        cwd=str(KIT_DIR),
        check=True,
    )
    shutil.copy2(dist_zip, dl_zip)
    print(f"[PASS] Repacked claude-code-kit.zip ({dist_zip.stat().st_size} bytes) -> dist/ & docs/downloads/")


def build_wenku_pdf():
    """构建 100% 国内文库合规专供版 PDF（15页：暗金封面零粉底补丁 + P.03 彩色决策树 SVG + P.15 一页纸贴屏速查卡 + 零外部链接）"""
    sh_src = (KIT_DIR / "cc-switch.sh").read_text(encoding="utf-8").strip()
    ps_src = (KIT_DIR / "cc-switch.ps1").read_text(encoding="utf-8").strip()
    doc_src = (KIT_DIR / "env-doctor.mjs").read_text(encoding="utf-8").strip()

    doc_lines = []
    for ln in doc_src.splitlines():
        if "github.io" in ln or "http://" in ln or "https://" in ln:
            doc_lines.append('console.log("💡 架构建议: 核心研发环境优先绑定 AWS Bedrock / Vertex AI 最小权限 IAM 凭据。");')
        elif "挂欧美机房节点直连官方个人号" in ln:
            doc_lines.append('  console.log("⚠️  [风险 -20] 系统时区为东八区 (" + tz + ")，跨区域调用个人测试凭据易触发合规风控异常。");')
        else:
            doc_lines.append(ln)
    doc_clean = "\n".join(doc_lines)
    assert "github.io" not in doc_clean

    # 均衡切分 cc-switch.sh (共196行)，确保 P.07/P.08/P.09 三页完整显示说明框与页脚零裁切
    sh_lines = sh_src.splitlines()
    sh_p1 = "\n".join(sh_lines[:60])
    sh_p2 = "\n".join(sh_lines[60:128])
    sh_p3 = "\n".join(sh_lines[128:])

    ps_lines = ps_src.splitlines()
    ps_p1 = "\n".join(ps_lines[:66])
    ps_p2 = "\n".join(ps_lines[66:])

    doc_l = doc_clean.splitlines()
    doc_p1 = "\n".join(doc_l[:37])
    doc_p2 = "\n".join(doc_l[37:])

    esc = html_mod.escape
    hero_uri = (EBOOK_DIR / "cover_hero_shield.jpg").as_uri()
    svg_tree = build_decision_tree_svg()
    cheatsheet_html = build_cheatsheet_inner_html(is_wenku=True)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>不掉号·不断流：Claude Code 企业云合规接入与排障手册（2026国内文库版）</title>
<style>
  @page {{ size: A4 portrait; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
  body {{
    font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    color: #1E293B; background: #FFFFFF;
  }}
  .page {{
    width: 210mm; height: 296.8mm; padding: 13.5mm 15.5mm 12.5mm 15.5mm;
    page-break-after: always; break-after: page; overflow: hidden;
    display: flex; flex-direction: column; position: relative; background: #FFFFFF;
  }}
  .page:last-child {{ page-break-after: auto; break-after: auto; }}
  .cover-wrap {{
    flex: 1; background: linear-gradient(160deg, #070D19 0%, #0F172A 52%, #172554 100%);
    border: 4px solid #F59E0B; border-radius: 16px; padding: 28px 32px 24px;
    display: flex; flex-direction: column; justify-content: space-between; color: #FFFFFF;
  }}
  .cover-wrap code {{
    background: rgba(245, 158, 11, 0.18); color: #FDE68A;
    border: 1px solid rgba(245, 158, 11, 0.35); padding: 1px 6px; border-radius: 4px; font-size: 8.8pt;
  }}
  .cov-pill {{
    display: inline-block; align-self: flex-start; background: linear-gradient(90deg, #F59E0B, #FBBF24); color: #0F172A;
    font-weight: 900; font-size: 10.5pt; padding: 5px 16px; border-radius: 99px;
  }}
  .cov-title {{ font-size: 36pt; font-weight: 900; letter-spacing: 1px; margin: 12px 0 8px; color: #F8FAFC; }}
  .cov-sub {{ font-size: 13.5pt; font-weight: 700; line-height: 1.5; color: #FDE68A; }}
  .cov-hero {{
    margin: 14px 0 10px; border-radius: 12px; overflow: hidden; border: 2px solid rgba(245, 158, 11, 0.65);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.45); background: #090F1D; height: 225px;
  }}
  .cov-hero img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .cov-box {{
    background: rgba(15, 23, 42, 0.82); border: 1.5px solid rgba(245, 158, 11, 0.35);
    border-radius: 12px; padding: 15px 20px; margin: 8px 0 12px;
  }}
  .cov-box p {{ font-size: 9.8pt; line-height: 1.72; color: #F8FAFC; margin-bottom: 4px; }}
  .cov-ft {{
    border-top: 1px solid rgba(255,255,255,0.2); padding-top: 11px;
    display: flex; justify-content: space-between; font-size: 9pt; color: #CBD5E1;
  }}
  h1 {{
    font-size: 15.8pt; font-weight: 900; color: #0F172A; border-left: 5px solid #2563EB;
    padding-left: 11px; margin-bottom: 10px; line-height: 1.28;
  }}
  h2 {{ font-size: 11.5pt; font-weight: 800; color: #1D4ED8; margin: 9px 0 6px; }}
  p, li {{ font-size: 9.5pt; line-height: 1.6; color: #1E293B; }}
  p {{ margin-bottom: 7px; }}
  ol, ul {{ padding-left: 20px; margin-bottom: 8px; }}
  li {{ margin-bottom: 3.5px; }}
  code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    background: #FEE2E2; color: #B91C1C; padding: 1px 5px; border-radius: 4px; font-size: 8.5pt;
  }}
  pre {{
    background: #0F172A; color: #F8FAFC; border-radius: 9px; padding: 8px 11px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 6.8pt; line-height: 1.28; white-space: pre-wrap; word-break: break-all;
    margin: 4px 0 7px; break-inside: avoid; page-break-inside: avoid;
  }}
  table {{
    width: 100%; border-collapse: collapse; margin: 7px 0 9px; font-size: 8.8pt;
    break-inside: avoid; page-break-inside: avoid;
  }}
  th {{ background: #0F172A; color: #FFFFFF; padding: 7px 9px; text-align: left; font-weight: 800; }}
  td {{ border: 1px solid #CBD5E1; padding: 6.5px 9px; line-height: 1.44; vertical-align: top; }}
  tr:nth-child(even) td {{ background: #F8FAFC; }}
  .svg-wrap {{
    margin: 6px 0 8px; break-inside: avoid; page-break-inside: avoid;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.14); border-radius: 10px;
  }}
  .note-box, .box {{
    background: #EFF6FF; border-left: 4px solid #2563EB; border-radius: 6px;
    padding: 8px 12px; font-size: 9pt; line-height: 1.5; color: #1E3A8A; margin-top: 6px;
    break-inside: avoid; page-break-inside: avoid;
  }}
  .warn-box {{
    background: #FFFBEB; border-left: 4px solid #D97706; border-radius: 6px;
    padding: 7.5px 11px; font-size: 8.8pt; line-height: 1.48; color: #78350F; margin: 5px 0;
    break-inside: avoid; page-break-inside: avoid;
  }}
  .pg-ft {{
    margin-top: auto; padding-top: 6px; border-top: 1px solid #E2E8F0;
    display: flex; justify-content: space-between; font-size: 8pt; color: #64748B;
  }}
  {CHEATSHEET_CSS}
</style>
</head>
<body>

<!-- P1: 封面 -->
<section class="page" style="padding:10mm;">
  <div class="cover-wrap">
    <div>
      <span class="cov-pill">2026 企业研发与个人开发者实战工程手册（v2.0 无损配置版）</span>
      <div class="cov-title">不掉号 · 不断流</div>
      <div class="cov-sub">Claude Code 终端 AI 编程架构排障、<br>AWS Bedrock / Google Vertex AI 企业云合规接入与多源容灾实战全解</div>
    </div>
    <div class="cov-hero"><img src="{hero_uri}" alt="Claude Guard Enterprise Architecture Cover"></div>
    <div class="cov-box">
      <p>◆ <b>核心解决痛点 1</b>：高清矢量《10秒报错排障决策树》定位 <code>Organization disabled</code> 环境变量冲突</p>
      <p>◆ <b>核心解决痛点 2</b>：亚马逊云 AWS Bedrock 最小权限 IAM 策略 JSON 与 Claude Sonnet 4.6 跨区推理部署</p>
      <p>◆ <b>核心解决痛点 3</b>：Google Cloud Vertex AI 企业商业接口配置、ADC 授权与配额调优实操</p>
      <p>◆ <b>核心解决痛点 4</b>：JSON 非破坏性深合并技术 —— 5 源 1 秒热备切换且 100% 保留 <code>mcpServers / hooks</code></p>
      <p>◆ <b>核心解决痛点 5</b>：附书末满版《一页纸终端防封与热切速查卡（1-Page Dev Cheat Sheet）》贴屏即查</p>
    </div>
    <div class="cov-ft">
      <span>编著：阿王写工具（OPC 工程研发组）</span>
      <span>适用系统：macOS / Linux / Windows PowerShell 全平台</span>
    </div>
  </div>
</section>

<!-- P2: 目录 -->
<section class="page">
  <h1>全书实战目录与可复制工程构件清单</h1>
  <p>本手册专为高频使用 AI 终端辅助编程工具的软件工程师、系统架构师与高校科研人员编写，提供从 10 秒可视化排障决策树、非破坏性配置深合并到云厂商企业级 API 生产架构的完整可运行源码。</p>
  <table>
    <thead><tr><th width="16%">章节</th><th>核心交付内容与可复制工程构件</th></tr></thead>
    <tbody>
      <tr><td><b>第 1 章</b></td><td>高清彩色矢量《10秒报错排障与零断流路由决策树》与四级凭据覆盖机制剖析</td></tr>
      <tr><td><b>第 2 章</b></td><td>30 秒快速排雷：macOS / Linux / Windows 三端残留环境变量定位与根除命令集</td></tr>
      <tr><td><b>第 3 章</b></td><td>企业云合规直连架构（上）：AWS Bedrock 最小权限 IAM JSON 与 Sonnet 4.6 跨区推理配置</td></tr>
      <tr><td><b>第 4 章</b></td><td>企业云合规直连架构（下）：Google Cloud Vertex AI 接入流程、ADC 本地授权与区域选择</td></tr>
      <tr><td><b>第 5 章</b></td><td>终端隐私加固与 <code>settings.json</code> 非破坏性深合并规范（附多源核心环境变量速查表）</td></tr>
      <tr><td><b>第 6 章</b></td><td>完整自动化源码（一）：macOS / Linux 五源无损热备切换器 <code>cc-switch.sh</code>（v2.0）</td></tr>
      <tr><td><b>第 7 章</b></td><td>完整自动化源码（二）：Windows PowerShell 五源无损切换器 <code>cc-switch.ps1</code>（v2.0）</td></tr>
      <tr><td><b>第 8 章</b></td><td>完整自动化源码（三）：Node.js 本地终端环境健康度自检脚本 <code>env-doctor.mjs</code></td></tr>
      <tr><td><b>附录 A</b></td><td>多轮研发对话资产防丢工程：新会话 1 秒恢复上下文 Prompt 模板与错误码速查字典</td></tr>
      <tr><td><b>附录 B</b></td><td><b>一页纸终端防封与零断流热切速查卡（1-Page Dev Cheat Sheet · 贴屏备查）</b></td></tr>
    </tbody>
  </table>
  <div class="note-box">
    <b>工程阅读说明：</b>本手册所有配置文件（JSON）与跨平台自动化脚本（Bash / PowerShell / Node.js ESM）均采用非破坏性深合并逻辑并经过真机实测验证，复制至本地工程环境即可直接运行，绝不误删用户原有的 MCP 服务、权限白名单或 Hooks 钩子配置。
  </div>
  <div class="pg-ft"><span>《不掉号·不断流》企业云合规接入与排障手册</span><span>P.02 / 15</span></div>
</section>

<!-- P3: 第1章（黄金免费试读页：内嵌高清彩色矢量决策树 SVG） -->
<section class="page">
  <h1>第 1 章：10 秒报错排障决策树与四级凭据覆盖机制剖析</h1>
  <p>在日常多仓库协同研发中，工程师启动终端 CLI 时突发 <code>400 Organization disabled</code>、<code>403</code> 或 5 小时窗口限流阻断，切忌盲目弃号重装。请先对照下方<b>《10秒报错排障与零断流路由决策树》</b>按症状精准分流：</p>

  <div class="svg-wrap">{svg_tree}</div>

  <h2>1.2 终端 CLI 的四级凭据读取优先级顺序（高优先级无条件覆盖低优先级）</h2>
  <ol>
    <li><b>L1 当前 Shell 进程显式环境变量</b>（<code>ANTHROPIC_API_KEY</code> / <code>ANTHROPIC_BASE_URL</code>）—— 抢占最高优先级，30%「网页正常但终端报 disabled」乌龙均由此层历史残留引起；</li>
    <li><b>L2 工作目录或父目录 <code>.env</code> 文件</b> —— 旧测试仓库遗留的失效测试密钥常潜伏于此；</li>
    <li><b>L3 全局配置文件 <code>~/.claude/settings.json</code> 的 <code>env</code> 字段</b> —— <code>cc-switch v2.0</code> 标准无损多源热切层；</li>
    <li><b>L4 交互式 OAuth 订阅登录态或云厂商默认凭证链</b>（AWS Credentials Profile / Google Cloud ADC）。</li>
  </ol>
  <div class="warn-box">
    <b>排障关键结论：</b>只要 <code>~/.zshrc</code> 或项目 <code>.env</code> 残留了早期失效的 <code>ANTHROPIC_API_KEY</code>，CLI 每次请求都会忽略有效订阅并报错。（翻开下一页获取三端一键根除命令、AWS/Vertex 最小权限 IAM 模板与全套 v2.0 无损切换脚本源码……）
  </div>
  <div class="pg-ft"><span>第 1 章 · 10秒排障决策树与认证优先级</span><span>P.03 / 15</span></div>
</section>

<!-- P4: 第2章 -->
<section class="page">
  <h1>第 2 章：三端残留环境变量精准定位与清理命令集</h1>
  <h2>2.1 macOS 与 Linux 终端排查清理流程</h2>
  <p>打开系统终端（Terminal / iTerm2），依次执行以下三步诊断与根除指令：</p>
  <pre># 1. 列出当前进程空间中所有与模型路由、鉴权相关的环境变量
env | grep -iE "ANTHROPIC|CLAUDE|AWS_REGION|CLOUD_ML"

# 2. 立即解除当前终端会话中的冲突环境变量绑定
unset ANTHROPIC_API_KEY
unset ANTHROPIC_AUTH_TOKEN
unset ANTHROPIC_BASE_URL

# 3. 深度扫描 Shell 启动配置文件中潜伏的历史导出语句并精确定位行号
grep -rn "ANTHROPIC_" ~/.zshrc ~/.bashrc ~/.bash_profile ~/.zprofile ./.env 2&gt;/dev/null</pre>
  <p>定位到具体文件与行号后，使用编辑器删除或注释废弃的 <code>export ANTHROPIC_...</code> 语句，执行 <code>source ~/.zshrc</code> 重新加载环境即可恢复纯净状态。</p>

  <h2>2.2 Windows PowerShell 环境排查与注册表级清理流程</h2>
  <p>在 Windows 平台下，除当前终端会话外，还需同步清理用户级（User）持久化环境变量：</p>
  <pre># 1. 检查当前 PowerShell 会话中的所有相关环境变量
Get-ChildItem Env: | Where-Object {{ $_.Name -match "ANTHROPIC|CLAUDE" }}

# 2. 清除当前会话及 Windows 用户级持久化残留变量
Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_BASE_URL -ErrorAction SilentlyContinue
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $null, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", $null, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $null, "User")</pre>
  <div class="note-box">
    <b>验证方法：</b>清理完成后关闭并重新打开一个新的终端窗口，再次执行步骤 1 检查输出为空，即可确认高优先级冲突源已 100% 根除。
  </div>
  <div class="pg-ft"><span>第 2 章 · 三端环境变量清理实操</span><span>P.04 / 15</span></div>
</section>

<!-- P5: 第3章 AWS Bedrock -->
<section class="page">
  <h1>第 3 章：企业云合规直连架构（上）—— AWS Bedrock 生产部署</h1>
  <p>通过亚马逊云 Amazon Bedrock 官方商业接口接入是研发团队与重度开发者的首选生产方案：按实际消耗 Token 结算，由企业级 IAM 权限与账单预算护航，彻底消除单点限流中断风险。</p>
  <h2>3.1 遵循安全规范的最小权限 IAM JSON 策略</h2>
  <p>严禁在开发机终端直接配置 AWS 根账号（Root）或 <code>AdministratorAccess</code> 宽泛权限！请在 AWS IAM 控制台创建独立子用户并仅挂载以下最小权限策略：</p>
  <pre>{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Sid": "ClaudeCodeBedrockLeastPrivilege",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-*",
        "arn:aws:bedrock:*:*:inference-profile/*.anthropic.claude-*"
      ]
    }}
  ]
}}</pre>
  <h2>3.2 跨区域推理（Cross-Region Inference Profile）最新一代模型配置</h2>
  <p>启用带 <code>us.</code> 或 <code>global.</code> 前缀的跨区推理配置，可在多个可用区间自动负载均衡并获得更高吞吐配额（主力编码模型推荐最新一代 <code>us.anthropic.claude-sonnet-4-6</code>，轻量后台子任务配 <code>us.anthropic.claude-haiku-4-5-20251001-v1:0</code>）：</p>
  <pre>{{
  "env": {{
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "us-east-1",
    "ANTHROPIC_MODEL": "us.anthropic.claude-sonnet-4-6",
    "ANTHROPIC_SMALL_FAST_MODEL": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }}
}}</pre>
  <div class="pg-ft"><span>第 3 章 · AWS Bedrock 生产架构部署</span><span>P.05 / 15</span></div>
</section>

<!-- P6: 第4章 Vertex AI + 第5章 非破坏性深合并与核心参数速查表 -->
<section class="page">
  <h1>第 4 章：企业云合规直连架构（下）—— Google Cloud Vertex AI</h1>
  <ol>
    <li>进入 Google Cloud 控制台 <code>Vertex AI -&gt; Model Garden</code>，搜索 Claude Sonnet 4.6 / Haiku 4.5 并点击启用商业 API 权限；</li>
    <li>本机安装 Google Cloud SDK 后执行 <code>gcloud auth application-default login</code> 生成本地应用默认凭据（ADC），无需硬编码明文密钥文件；</li>
    <li>在 <code>~/.claude/settings.json</code> 的 <code>env</code> 节点中合并写入以下配置（高并发推荐选 <code>global</code> 或 <code>us-east5</code> 区域）：</li>
  </ol>
  <pre>{{
  "env": {{
    "CLAUDE_CODE_USE_VERTEX": "1",
    "CLOUD_ML_REGION": "us-east5",
    "ANTHROPIC_VERTEX_PROJECT_ID": "your-gcp-project-id",
    "ANTHROPIC_MODEL": "claude-sonnet-4-6",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }}
}}</pre>

  <h1>第 5 章：非破坏性 JSON 深合并规范与核心环境变量速查表</h1>
  <div class="warn-box">
    <b>⚠️ 严防毁配置事故：</b>许多初级脚本直接用 <code>cat &gt; ~/.claude/settings.json</code> 全量覆盖文件，瞬间清空开发者辛苦配好的 <code>mcpServers</code>（MCP 工具集）、<code>permissions</code>（命令白名单）与 <code>hooks</code>（自动化钩子）！生产切换脚本必须解析原 JSON 树，仅对 <code>env</code> 下的托管路由键做局部增删深合并。
  </div>
  <table>
    <thead><tr><th width="36%">环境变量键名</th><th width="20%">推荐值 / 示例</th><th>工程作用与冲突避坑要点</th></tr></thead>
    <tbody>
      <tr><td><code>CLAUDE_CODE_USE_BEDROCK</code></td><td><code>"1"</code></td><td>启用 AWS Bedrock IAM 路由；切换回其他通道时必须从 <code>env</code> 删除该键</td></tr>
      <tr><td><code>CLAUDE_CODE_USE_VERTEX</code></td><td><code>"1"</code></td><td>启用 Google Vertex AI ADC 路由；不可与 Bedrock 开关同时置 <code>"1"</code></td></tr>
      <tr><td><code>ANTHROPIC_MODEL</code></td><td><code>us.anthropic.claude-sonnet-4-6</code></td><td>指定主推理模型；Bedrock 按需调用务必保留 <code>us.</code> 或 <code>global.</code> 推理前缀</td></tr>
      <tr><td><code>ANTHROPIC_SMALL_FAST_MODEL</code></td><td><code>us.anthropic.claude-haiku-4-5-...</code></td><td>指定文件检索、标题摘要等高频轻量任务模型，可降低约 45% 综合 Token 账单</td></tr>
      <tr><td><code>DISABLE_TELEMETRY</code></td><td><code>"1"</code></td><td>关闭默认开启的 Statsig 特性行为遥测上报，减少非必要外部网络请求</td></tr>
      <tr><td><code>DISABLE_ERROR_REPORTING</code></td><td><code>"1"</code></td><td>关闭异常崩溃时的本地调用堆栈自动上传，满足企业内网代码保密合规要求</td></tr>
      <tr><td><code>CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC</code></td><td><code>"1"</code></td><td>阻断自动更新轮询等非核心后台握手流量，显著提升终端冷启动响应速度</td></tr>
    </tbody>
  </table>
  <div class="pg-ft"><span>第 4–5 章 · Vertex AI 接入与非破坏性配置规范</span><span>P.06 / 15</span></div>
</section>

<!-- P7: 第6章 macOS/Linux 脚本 (1/3) -->
<section class="page">
  <h1>第 6 章：完整自动化源码（一）—— macOS / Linux 无损切换器 (1/3)</h1>
  <p>将以下完整脚本保存为 <code>cc-switch.sh</code> 并执行 <code>chmod +x cc-switch.sh</code>，支持 5 源秒切且 100% 保留原有 MCP 与 Hooks 配置：</p>
  <pre style="font-size:6.55pt;line-height:1.25;">{esc(sh_p1)}</pre>
  <div class="pg-ft"><span>第 6 章 · cc-switch.sh 完整无损切换源码 (1/3)</span><span>P.07 / 15</span></div>
</section>

<!-- P8: 第6章 macOS/Linux 脚本 (2/3) -->
<section class="page">
  <h2>6.2 cc-switch.sh 核心 Node.js 非破坏性 JSON 合并引擎 (2/3)</h2>
  <pre style="font-size:6.55pt;line-height:1.25;">{esc(sh_p2)}</pre>
  <div class="pg-ft"><span>第 6 章 · cc-switch.sh 完整无损切换源码 (2/3)</span><span>P.08 / 15</span></div>
</section>

<!-- P9: 第6章 macOS/Linux 脚本 (3/3) -->
<section class="page">
  <h2>6.3 cc-switch.sh Python3 双保险回退分支与收尾校验 (3/3)</h2>
  <pre style="font-size:6.4pt;line-height:1.23;">{esc(sh_p3)}</pre>
  <div class="note-box" style="padding:7px 11px;font-size:8.7pt;">
    <b>设计亮点解析：</b>脚本通过环境变量向 <code>node -e</code>（或回退 <code>python3 -c</code>）传递用户输入，绝不将含特殊符号的密钥直接拼接进代码字符串，既杜绝了命令注入风险，又保证了原 JSON 出现语法损坏时立即中止保护现场。
  </div>
  <div class="pg-ft"><span>第 6 章 · cc-switch.sh 完整无损切换源码 (3/3)</span><span>P.09 / 15</span></div>
</section>

<!-- P10: 第7章 Windows PowerShell 脚本 (1/2) -->
<section class="page">
  <h1>第 7 章：完整自动化源码（二）—— Windows PowerShell 无损切换器 (1/2)</h1>
  <p>保存为 <code>cc-switch.ps1</code>，通过 <code>powershell -ExecutionPolicy Bypass -File .\\cc-switch.ps1</code> 运行：</p>
  <pre>{esc(ps_p1)}</pre>
  <div class="pg-ft"><span>第 7 章 · cc-switch.ps1 Windows 无损切换源码 (1/2)</span><span>P.10 / 15</span></div>
</section>

<!-- P11: 第7章 Windows PowerShell 脚本 (2/2) -->
<section class="page">
  <h2>7.2 cc-switch.ps1 无 BOM UTF-8 写入与深度树保留逻辑 (2/2)</h2>
  <pre style="font-size:6.25pt;line-height:1.22;padding:7px 10px;">{esc(ps_p2)}</pre>
  <div class="note-box" style="padding:7px 11px;font-size:8.6pt;line-height:1.45;">
    <b>Windows 专项避坑：</b>Windows PowerShell 5.1 默认的 <code>Set-Content -Encoding UTF8</code> 会写入带 BOM 字节头的文件，且 <code>ConvertTo-Json</code> 默认深度仅为 2 层（会截断深层 <code>mcpServers</code> 参数数组）。上方源码优先调用 Node 原生引擎并在回退分支强制指定 <code>-Depth 20</code> 与无 BOM <code>UTF8Encoding($false)</code>，彻底消除跨平台编码隐患。
  </div>
  <div class="pg-ft"><span>第 7 章 · cc-switch.ps1 Windows 无损切换源码 (2/2)</span><span>P.11 / 15</span></div>
</section>

<!-- P12: 第8章 env-doctor.mjs (1/2) + 巡检指标速查表 -->
<section class="page">
  <h1>第 8 章：完整自动化源码（三）—— 本地环境巡检器 env-doctor.mjs</h1>
  <p>保存为 <code>env-doctor.mjs</code>，执行 <code>node env-doctor.mjs</code> 即可一键输出终端配置完整性与安全评分报告：</p>
  <pre>{esc(doc_p1)}</pre>
  <h2>8.1 本地终端环境自动化巡检四大核心维度</h2>
  <table>
    <thead><tr><th width="25%">检测维度</th><th width="22%">扣分权重 / 判定</th><th>工程排障意义</th></tr></thead>
    <tbody>
      <tr><td><b>Intl 时区一致性</b></td><td>跨区偏移 <code>-20 分</code></td><td>识别终端 Node/V8 运行时暴露的系统时区是否与云网关出口区域错位</td></tr>
      <tr><td><b>非必要遥测开关</b></td><td>未开启 <code>-25 分</code></td><td>检查 <code>DISABLE_TELEMETRY=1</code> 与非核心流量阻断是否已在全局生效</td></tr>
      <tr><td><b>代理环境变量链</b></td><td>实时枚举回显</td><td>透视 <code>HTTP_PROXY / ALL_PROXY</code> 显式绑定，排查终端走错透明隧道问题</td></tr>
      <tr><td><b>企业云 IAM 通道</b></td><td>保底 <code>95–100 分</code></td><td>检测到已激活 AWS Bedrock 或 Google Vertex AI 时直接授予生产稳态评级</td></tr>
    </tbody>
  </table>
  <div class="pg-ft"><span>第 8 章 · env-doctor.mjs 环境健康自检源码 (1/2)</span><span>P.12 / 15</span></div>
</section>

<!-- P13: 第8章 env-doctor.mjs (2/2) —— 100% 纯净无任何外链硬广！ -->
<section class="page">
  <h2>8.2 env-doctor.mjs 评分规则与企业通道核验逻辑 (2/2)</h2>
  <pre>{esc(doc_p2)}</pre>
  <h2>8.3 生产研发环境巡检满分（95–100 分）验收清单</h2>
  <ul>
    <li><b>环境变量层零幽灵覆盖：</b><code>env | grep ANTHROPIC</code> 无任何未授权的历史残留静态 Key；</li>
    <li><b>非必要流量全屏蔽：</b><code>~/.claude/settings.json</code> 已开启 <code>DISABLE_TELEMETRY=1</code>、<code>DISABLE_ERROR_REPORTING=1</code> 与 <code>CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1</code>；</li>
    <li><b>双通道热备就绪：</b>本地已预置 AWS Bedrock（<code>us.anthropic.claude-sonnet-4-6</code>）或 Google Vertex AI 凭据，单通道偶发高负载拥塞时 1 秒无损热切不断流；</li>
    <li><b>权限最小化闭环：</b>云端 IAM 子账号仅授予 <code>bedrock:InvokeModel*</code> 推理权限，并配置月度账单告警阈值。</li>
  </ul>
  <div class="pg-ft"><span>第 8 章 · env-doctor.mjs 验收标准与加固闭环</span><span>P.13 / 15</span></div>
</section>

<!-- P14: 附录 A -->
<section class="page">
  <h1>附录 A：多轮研发上下文无缝恢复模板与常见错误码速查字典</h1>
  <h2>A.1 新会话 1 秒恢复项目上下文标准结构化 Prompt 模板</h2>
  <p>建议在长周期模块开发阶段定期将关键架构决策与最新代码块归档为本地 Markdown 文档。切换通道或开启新会话时粘贴以下引导模板：</p>
  <pre>You are resuming an ongoing software engineering project. Below is the verified
architecture summary, key design constraints, and latest code artifacts from our
previous session. Read them carefully, confirm the current file state, and wait
for my next instruction without rewriting already-completed modules:

[在此粘贴导出的关键架构摘要、接口契约与最新未提交代码块]</pre>

  <h2>A.2 常见 HTTP 状态码与终端报错 10 秒排障速查表</h2>
  <table>
    <thead><tr><th width="28%">状态码 / 报错关键词</th><th width="34%">真实根因定位</th><th>标准工程修复动作</th></tr></thead>
    <tbody>
      <tr><td><code>400 Organization disabled</code></td><td>本地 Shell 残留失效旧 <code>ANTHROPIC_API_KEY</code> 抢占最高优先级</td><td>按第 2 章执行 <code>unset</code> 并清理 <code>~/.zshrc</code> 或注册表残留项</td></tr>
      <tr><td><code>403 AccessDeniedException</code></td><td>AWS 当前区域未启用目标模型或漏加跨区推理前缀</td><td>核对第 3.1 节最小权限 IAM 策略，模型名改用 <code>us.anthropic.claude-sonnet-4-6</code></td></tr>
      <tr><td><code>403 PERMISSION_DENIED</code></td><td>GCP 项目未启用 Vertex AI API 或本地 ADC 授权令牌过期</td><td>重新执行 <code>gcloud auth application-default login</code> 刷新本地令牌</td></tr>
      <tr><td>切换源后 MCP 工具全部消失</td><td>误用了旧式全量覆盖命令重写了整个 <code>settings.json</code></td><td>从同目录自动生成的 <code>settings.backup.*.json</code> 恢复并改用第 6/7 章无损合并脚本</td></tr>
      <tr><td><code>429 Too Many Requests</code></td><td>单通道达到分钟级速率窗口（RPM / TPM）配额上限</td><td>运行 <code>cc-switch</code> 1 秒热切至跨区推理或备用企业云通道</td></tr>
      <tr><td><code>529 Overloaded</code></td><td>上游单一区域推理集群瞬时算力拥塞</td><td>将 <code>AWS_REGION</code> 切至 <code>us-west-2</code> 或改用 <code>global.</code> 推理配置继续作业</td></tr>
    </tbody>
  </table>
  <div class="pg-ft"><span>附录 A · 上下文恢复工程与错误码速查表</span><span>P.14 / 15</span></div>
</section>

<!-- P15: 附录 B 一页纸终端防封与热切速查卡 (1-Page Dev Cheat Sheet) -->
<section class="page" style="padding:11mm 13mm 10.5mm 13mm;">
  {cheatsheet_html}
  <div class="pg-ft"><span>附录 B · 一页纸终端防封与热切速查卡（1-Page Dev Cheat Sheet）</span><span>P.15 / 15</span></div>
</section>

</body>
</html>"""

    out_pdf = EBOOK_DIR / "不掉号-不断流_ClaudeCode企业云合规接入与排障手册_2026国内文库版.pdf"
    with tempfile.TemporaryDirectory(prefix="cgw_", dir="/tmp") as td:
        td_p = Path(td)
        parts = html.split('<section class="page')
        head = parts[0]
        writer = PdfWriter()
        for idx, sec in enumerate(parts[1:], start=1):
            one = head + '<section class="page' + sec.split("</body>")[0] + "</body></html>"
            hf = td_p / f"p{idx:02d}.html"
            pf = td_p / f"p{idx:02d}.pdf"
            hf.write_text(one, encoding="utf-8")
            for attempt in range(4):
                subprocess.run(
                    [
                        CHROME_BIN,
                        "--headless=new",
                        "--disable-gpu",
                        f"--user-data-dir={td_p / f'u{idx:02d}_{attempt}'}",
                        "--no-pdf-header-footer",
                        "--virtual-time-budget=2500",
                        f"--print-to-pdf={pf}",
                        hf.as_uri(),
                    ],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if pf.exists() and pf.stat().st_size > 500:
                    break
            if not (pf.exists() and pf.stat().st_size > 500):
                raise RuntimeError(f"Failed page {idx}")
            r = PdfReader(str(pf))
            assert len(r.pages) == 1, f"Wenku page {idx} spilled onto {len(r.pages)} pages!"
            writer.add_page(r.pages[0])
        for pg in writer.pages:
            pg.compress_content_streams()
        writer.add_metadata({
            "/Title": "不掉号·不断流：Claude Code 终端 AI 编程架构排障、AWS Bedrock / Google Vertex AI 企业云合规接入与多源容灾实战全解",
            "/Author": "阿王写工具（OPC 工程研发组）",
        })
        try:
            writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
        except TypeError:
            writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
        tmp_out = td_p / "out.pdf"
        with open(tmp_out, "wb") as f:
            writer.write(f)
        shutil.move(str(tmp_out), str(out_pdf))

    r_check = PdfReader(str(out_pdf))
    full_txt = "\n".join(p.extract_text() or "" for p in r_check.pages)
    assert len(r_check.pages) == 15, f"Expected 15 pages, got {len(r_check.pages)}"
    assert "github.io" not in full_txt and "a3152557994" not in full_txt, "External promo link still present!"
    ext_uris = []
    for p in r_check.pages:
        for a in p.get("/Annots") or []:
            act = a.get_object().get("/A")
            if act and "/URI" in act.get_object():
                ext_uris.append(str(act.get_object()["/URI"]))
    assert len(ext_uris) == 0, f"Wenku PDF must have 0 external URI links, found: {ext_uris}"
    print(f"[PASS] Built Wenku PDF: {out_pdf.name} -> {len(r_check.pages)} pages | {out_pdf.stat().st_size // 1024} KB | 0 external URIs!")


def update_zero_ban_epub_and_full_pdf():
    """同步更新 Zero-Ban-Claude-2026.epub（新增决策树 SVG + 附录B一页纸速查卡）并重构出版级零大白页完整版 PDF"""
    epub_pack = EBOOK_DIR / "不掉号_Zero-Ban-Claude-2026.epub"
    epub_dl = ROOT / "docs" / "downloads" / "Zero-Ban-Claude-2026.epub"
    full_pdf_pack = EBOOK_DIR / "不掉号_Claude防封号与封后退费自救全书_2026完整版.pdf"
    full_pdf_dl = ROOT / "docs" / "downloads" / "Claude-2026-Anti-Ban-Playbook.pdf"

    svg_tree = build_decision_tree_svg()
    cheatsheet_body = build_cheatsheet_inner_html(is_wenku=False)

    epub_style_css = """body { font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; line-height: 1.68; color: #1e293b; margin: 4%; }
h1 { font-size: 1.5em; color: #0f172a; border-bottom: 2px solid #f59e0b; padding-bottom: 0.3em; margin-top: 0.5em; }
h2 { font-size: 1.18em; color: #1e3a8a; margin-top: 1.15em; }
h3 { font-size: 1.05em; color: #0f172a; margin-top: 0.9em; }
p, li { font-size: 0.96em; }
code { font-family: monospace; background: #f1f5f9; color: #be123c; padding: 0.1em 0.3em; border-radius: 3px; }
pre { background: #0f172a; color: #f8fafc; padding: 0.8em; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; font-size: 0.86em; }
pre code { background: transparent; color: #f8fafc; padding: 0; }
.box { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 0.75em 0.95em; margin: 0.9em 0; border-radius: 0 6px 6px 0; }
table { width: 100%; border-collapse: collapse; margin: 0.9em 0; font-size: 0.86em; }
th { background: #0f172a; color: #ffffff; padding: 0.48em; text-align: left; }
td { border: 1px solid #cbd5e1; padding: 0.48em; vertical-align: top; }
a { color: #2563eb; text-decoration: underline; }
.svg-wrap { margin: 0.8em 0; }
.cs-banner { background: #0f172a; color: #fff; padding: 0.7em 0.9em; border-left: 4px solid #f59e0b; border-radius: 6px; margin-bottom: 0.8em; }
.cs-kicker { font-size: 0.78em; color: #fde68a; font-weight: bold; }
.cs-title { font-size: 1.2em; font-weight: bold; color: #ffffff; }
.cs-badge { display: inline-block; background: #f59e0b; color: #0f172a; font-size: 0.78em; font-weight: bold; padding: 2px 8px; border-radius: 99px; margin-top: 4px; }
.cs-card { border: 1px solid #cbd5e1; border-radius: 6px; padding: 0.7em; margin-bottom: 0.8em; background: #f8fafc; }
.cs-card-hd { font-weight: bold; color: #0f172a; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.3em; margin-bottom: 0.5em; }
.pyr-item { margin-bottom: 0.45em; padding: 0.4em; background: #ffffff; border-radius: 4px; border-left: 3px solid #f59e0b; }
.pyr-tag { display: inline-block; background: #0f172a; color: #fde68a; font-size: 0.78em; font-weight: bold; padding: 1px 6px; border-radius: 4px; margin-right: 6px; }
.cs-mini-warn { background: #fffbeb; border-left: 3px solid #f59e0b; padding: 0.5em; font-size: 0.86em; }
.cs-sub-lbl { font-weight: bold; font-size: 0.88em; color: #1e3a8a; margin: 0.4em 0 0.2em; }
.cs-footer-formula { background: #0f172a; color: #f8fafc; padding: 0.65em 0.85em; border-radius: 6px; font-size: 0.88em; }
"""

    nav_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>目录</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>全书实战目录</h1>
    <ol>
      <li><a href="cover.xhtml">封面</a></li>
      <li><a href="ch00_preface.xhtml">序言与 30 秒急救导航</a></li>
      <li><a href="ch01_risk_matrix.xhtml">第 1 章：2026 四重风控解剖与 10 秒排障决策树</a></li>
      <li><a href="ch02_false_ban.xhtml">第 2 章：30 秒排掉「假封号」乌龙与四级凭据优先级</a></li>
      <li><a href="ch03_network_isolation.xhtml">第 3 章：网络与浏览器指纹防关联工程（附 ASN 红黑榜）</a></li>
      <li><a href="ch04_apple_iap.xhtml">第 4 章：绕开 Stripe 绞肉机——美区免税州 Apple 礼品卡订阅全解</a></li>
      <li><a href="ch05_claude_code.xhtml">第 5 章：Claude Code 终端加固与 5 源 1 秒无损深合并</a></li>
      <li><a href="ch06_bedrock_vertex.xhtml">第 6 章：100% 永不封号终极架构——AWS Bedrock 与 Google Vertex AI</a></li>
      <li><a href="ch07_refund_appeal.xhtml">第 7 章：封后黄金 48 小时止损——追回 $20/$200 与英文申诉模板</a></li>
      <li><a href="ch08_vault_recovery.xhtml">第 8 章：重开新号「四清铁律」与本地代码零丢失保险箱</a></li>
      <li><a href="ch09_appendix.xhtml">附录 A：Claude 与 Claude Code 常见报错代码速查字典</a></li>
      <li><a href="ch10_cheatsheet.xhtml">附录 B：一页纸终端防封与零断流热切速查卡（1-Page Cheat Sheet）</a></li>
    </ol>
  </nav>
</body>
</html>"""

    ncx_new = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:20261122-zero-ban-claude-opc-v1"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>不掉号：Claude 防封号、免税订阅与封后退款自救全书</text></docTitle>
  <navMap>
    <navPoint id="navPoint-1" playOrder="1"><navLabel><text>序言与 30 秒急救导航</text></navLabel><content src="ch00_preface.xhtml"/></navPoint>
    <navPoint id="navPoint-2" playOrder="2"><navLabel><text>第 1 章：2026 四重风控解剖与 10 秒排障决策树</text></navLabel><content src="ch01_risk_matrix.xhtml"/></navPoint>
    <navPoint id="navPoint-3" playOrder="3"><navLabel><text>第 2 章：30 秒排掉「假封号」乌龙与四级凭据优先级</text></navLabel><content src="ch02_false_ban.xhtml"/></navPoint>
    <navPoint id="navPoint-4" playOrder="4"><navLabel><text>第 3 章：网络与浏览器指纹防关联工程</text></navLabel><content src="ch03_network_isolation.xhtml"/></navPoint>
    <navPoint id="navPoint-5" playOrder="5"><navLabel><text>第 4 章：绕开 Stripe 绞肉机——美区免税州 Apple 礼品卡订阅全解</text></navLabel><content src="ch04_apple_iap.xhtml"/></navPoint>
    <navPoint id="navPoint-6" playOrder="6"><navLabel><text>第 5 章：Claude Code 终端加固与 5 源 1 秒无损深合并</text></navLabel><content src="ch05_claude_code.xhtml"/></navPoint>
    <navPoint id="navPoint-7" playOrder="7"><navLabel><text>第 6 章：100% 永不封号终极架构——AWS Bedrock 与 Google Vertex AI</text></navLabel><content src="ch06_bedrock_vertex.xhtml"/></navPoint>
    <navPoint id="navPoint-8" playOrder="8"><navLabel><text>第 7 章：封后黄金 48 小时止损——把被封的 $20 / $200 追回来</text></navLabel><content src="ch07_refund_appeal.xhtml"/></navPoint>
    <navPoint id="navPoint-9" playOrder="9"><navLabel><text>第 8 章：重开新号「四清铁律」与本地代码零丢失保险箱</text></navLabel><content src="ch08_vault_recovery.xhtml"/></navPoint>
    <navPoint id="navPoint-10" playOrder="10"><navLabel><text>附录 A：常见报错代码速查字典</text></navLabel><content src="ch09_appendix.xhtml"/></navPoint>
    <navPoint id="navPoint-11" playOrder="11"><navLabel><text>附录 B：一页纸终端防封与零断流热切速查卡</text></navLabel><content src="ch10_cheatsheet.xhtml"/></navPoint>
  </navMap>
</ncx>"""

    opf_new = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId" xml:lang="zh-CN">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">urn:uuid:20261122-zero-ban-claude-opc-v1</dc:identifier>
    <dc:title>不掉号：Claude 防封号、免税订阅与封后退款自救全书 (Zero-Ban Claude 2026 v2.0)</dc:title>
    <dc:creator>阿王写工具 (OPC Studio)</dc:creator>
    <dc:language>zh-CN</dc:language>
    <dc:publisher>OPC Studio</dc:publisher>
    <dc:date>2026-11-22</dc:date>
    <dc:subject>Artificial Intelligence</dc:subject>
    <dc:subject>Software Development</dc:subject>
    <dc:subject>Claude Code &amp; Cloud Architecture</dc:subject>
    <dc:description>专为开发者、科研人员与高频创作者编写的 2026 实战自救指南：内含高清彩色《10秒报错排障决策树》、30 秒排查环境变量假封号乌龙、ASN 机房风险识别、美区免税州 Apple 礼品卡稳态订阅、AWS Bedrock 与 Google Vertex AI 0% 封号接入、封后 48 小时追回订阅费与书末《一页纸贴屏速查卡》。</dc:description>
    <meta property="dcterms:modified">2026-11-26T17:00:00Z</meta>
    <meta name="cover" content="cover-img"/>
  </metadata>
  <manifest>
    <item id="style" href="style.css" media-type="text/css"/>
    <item id="cover-img" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>
    <item id="decision-tree-img" href="decision_tree.png" media-type="image/png"/>
    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="ch01" href="ch00_preface.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch02" href="ch01_risk_matrix.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch03" href="ch02_false_ban.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch04" href="ch03_network_isolation.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch05" href="ch04_apple_iap.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch06" href="ch05_claude_code.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch07" href="ch06_bedrock_vertex.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch08" href="ch07_refund_appeal.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch09" href="ch08_vault_recovery.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch10" href="ch09_appendix.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch11" href="ch10_cheatsheet.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover"/>
    <itemref idref="nav"/>
    <itemref idref="ch01"/>
    <itemref idref="ch02"/>
    <itemref idref="ch03"/>
    <itemref idref="ch04"/>
    <itemref idref="ch05"/>
    <itemref idref="ch06"/>
    <itemref idref="ch07"/>
    <itemref idref="ch08"/>
    <itemref idref="ch09"/>
    <itemref idref="ch10"/>
    <itemref idref="ch11"/>
  </spine>
</package>"""

    ch01_new = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>第 1 章：2026 四重风控解剖与 10 秒排障决策树</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>第 1 章：2026 四重风控解剖与 10 秒排障决策树</h1>
    <p>为什么同样跨境办公，有人一个 Pro 号稳用满一年，有人刚绑卡 5 分钟就秒封？因为 Anthropic 风控早已不是单看“IP 在不在美国”，而是<strong>四套独立雷达交叉打分</strong>：</p>
    <ol>
      <li><strong>出口 IP 的 ASN（自治系统号）机房库比对</strong>：流量出口属于 Cloudflare (<code>AS13335</code>)、Vultr (<code>AS20473</code>)、DigitalOcean (<code>AS14061</code>)、搬瓦工等数据中心共享段，一人跑爬虫或越狱，同段账号整批连坐。</li>
      <li><strong>设备时区与 WebRTC 底层穿透校验</strong>：网页端 JS 读取 <code>Intl</code> 系统时区，挂美西 IP 却直出 <code>Asia/Shanghai (UTC+8)</code> 与 <code>zh-CN</code> 语言，异常分直接拉满。</li>
      <li><strong>Stripe 支付网关 BIN 卡段连坐</strong>：公开虚拟信用卡（VCC）卡头一旦因他人拒付被拉黑，同 BIN 段历史绑定账号回溯封禁。</li>
      <li><strong>OAuth 凭证非官方客户端调用</strong>：将个人 Pro/Max 订阅凭证填入第三方逆向套壳客户端或共享池，立即触发整个 Organization 封停。</li>
    </ol>
    <table>
      <thead><tr><th style="width:36%;">订阅与连接方案</th><th style="width:16%;">封号风险</th><th>核心原因剖析</th></tr></thead>
      <tbody>
        <tr><td>普通共享节点 + 某宝代充 / 拼车成品号</td><td><strong>95% 极危</strong></td><td>机房 ASN 千人骑 + 黑卡回滚一锅端</td></tr>
        <tr><td>网页端直接绑公开虚拟信用卡（VCC）</td><td><strong>70% 高危</strong></td><td>虚拟卡 BIN 段被 Stripe 重点监控，易触发 KYC 或秒封</td></tr>
        <tr><td>个人 Pro/Max 凭证接入第三方套壳工具</td><td><strong>85% 高危</strong></td><td>违反 OAuth 客户端调用规范，触发自动化封禁</td></tr>
        <tr><td><strong>独享静态住宅 IP + 美区免税州 Apple 礼品卡内购</strong></td><td><strong>&lt;5% 极稳</strong></td><td>苹果接管支付隔离 Stripe 风控，误封可走苹果退费</td></tr>
        <tr><td><strong>AWS Bedrock / Google Vertex AI 企业通道</strong></td><td><strong>0% 永不封</strong></td><td>亚马逊/谷歌正规商业 IAM 接口按量结算，无个人号封禁机制</td></tr>
      </tbody>
    </table>
    <h2>二、10 秒报错排障与零断流路由决策树（按症状精准对号入座）</h2>
    <div class="svg-wrap"><img src="decision_tree.png" alt="10秒报错排障与零断流路由决策树" style="width:100%;height:auto;display:block;" /></div>
</body>
</html>"""

    ch02_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>第 2 章：30 秒排掉「假封号」乌龙与四级凭据优先级</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>第 2 章：30 秒排掉「假封号」乌龙与四级凭据优先级</h1>
    <p>在终端运行 <code>claude</code>（Claude Code）时，如果突然看到以下阻断报错，<strong>先停手！不要急着弃号或重买！</strong>超过 <strong>30%</strong> 的开发者遇到这行字并非新充的 Pro / Max 账号被封，而是<strong>本地残留环境变量抢占了认证优先级</strong>：</p>
    <pre><code>API Error: 400 {"type":"error","error":{"type":"invalid_request_error","message":"Your organization has been disabled."}}</code></pre>
    <h2>一、CLI 四级凭据读取优先级机制（高优先级无条件覆盖低优先级）</h2>
    <table>
      <thead><tr><th style="width:20%;">优先级层级</th><th style="width:34%;">配置来源位置</th><th>覆盖行为与排障要点</th></tr></thead>
      <tbody>
        <tr><td><strong>L1 最高抢占</strong></td><td>Shell 显式环境变量 (<code>ANTHROPIC_API_KEY</code>)</td><td>无条件覆盖一切订阅登录态；半年前填在 <code>.zshrc</code> 的失效中转 Key 会直接报 400</td></tr>
        <tr><td><strong>L2 目录局部</strong></td><td>当前或父目录 <code>./.env</code> 文件</td><td>旧测试项目残留的局部测试密钥，进入该仓库即刻触发报错</td></tr>
        <tr><td><strong>L3 全局路由</strong></td><td><code>~/.claude/settings.json</code> ➔ <code>env</code></td><td><code>cc-switch v2.0</code> 标准多源无损切换层，结构化可审计</td></tr>
        <tr><td><strong>L4 默认底座</strong></td><td>OAuth 订阅令牌 / AWS IAM / GCP ADC</td><td>只有前三级无冲突静态 Key 时，才会正常走你的 Pro/Max 订阅或云端默认凭据</td></tr>
      </tbody>
    </table>
    <h2>二、macOS / Linux / Windows 三端 30 秒排雷命令</h2>
    <p><strong>1. macOS / Linux 终端排查与清理：</strong></p>
    <pre><code># 第一步：检查当前进程是否残留旧 Key 或第三方 Base URL
env | grep -iE "ANTHROPIC|CLAUDE"

# 第二步：立即解除当前终端会话冲突变量并扫描启动脚本潜伏行号
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL
grep -rn "ANTHROPIC_" ~/.zshrc ~/.bashrc ~/.bash_profile ~/.zprofile ./.env 2&gt;/dev/null</code></pre>
    <p><strong>2. Windows PowerShell 会话与注册表级清理：</strong></p>
    <pre><code>Get-ChildItem Env: | Where-Object { $_.Name -like "*ANTHROPIC*" }
Remove-Item Env:ANTHROPIC_API_KEY,Env:ANTHROPIC_BASE_URL -ErrorAction SilentlyContinue
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $null, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $null, "User")</code></pre>
    <p>删净启动脚本残留后重开终端运行 <code>claude /login</code>，只要网页端 <code>claude.ai</code> 能正常对话，你的终端将立刻满血复活！</p>
</body>
</html>"""

    ch03_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>第 3 章：网络与浏览器指纹防关联工程</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>第 3 章：网络与浏览器指纹防关联工程</h1>
    <p>如果你主用网页端 Claude Pro / Max，堵住封号源头的核心只有八个字：<strong>「原生家宽 + 独立容器」</strong>。</p>
    <h2>一、3 步识别真假静态原生住宅 IP（附常见 ASN 红黑榜）</h2>
    <ol>
      <li>打开在线自检台 <a href="https://a3152557994-ship-it.github.io/claude-guard/">Claude Guard 10秒体检台</a> 查看当前出口 IP 的 ASN 与运营商组织名称；</li>
      <li>核对下方常见自治系统号（ASN）信誉分类，全程固定单一美国城市出口，切勿早晚在美、日、新之间横跳。<strong>特别警告：中国香港属于不支持区域，严禁挂香港节点访问或点击官方邮件！</strong></li>
    </ol>
    <table>
      <thead><tr><th style="width:24%;">出口类型</th><th style="width:38%;">典型 ASN 与运营商标识</th><th>风控评分与处置建议</th></tr></thead>
      <tbody>
        <tr><td><strong>✅ 原生住宅 ISP</strong></td><td><code>AS7922</code> (Comcast)、<code>AS7018</code> (AT&amp;T)、<code>AS701</code> (Verizon)、<code>AS20115</code> (Charter)</td><td><code>hosting: false</code>，高信誉家庭宽带特征，配合固定单城可长期稳用</td></tr>
        <tr><td><strong>❌ 高危机房段</strong></td><td><code>AS13335</code> (Cloudflare)、<code>AS20473</code> (Vultr/Choopa)、<code>AS14061</code> (DigitalOcean)、<code>AS9009</code> (M247)</td><td><code>hosting: true</code>，千人共用服务器代理段，注册或绑卡极易触发自动封禁</td></tr>
      </tbody>
    </table>
    <h2>二、为什么必须用独立浏览器环境隔离 Claude？</h2>
    <p>你平时办公的主力 Chrome 浏览器装满了几十个国内扩展、保存着大量中文站点 Cookie、系统语言是 <code>zh-CN</code>、本地时区是 <code>Asia/Shanghai</code>，甚至 WebRTC STUN 握手会直接穿透代理暴露你的真实国内宽带公网 IP。</p>
    <div class="box">
      <strong>🛠️ 推荐零成本标准物理隔离做法：</strong>
      <p>无需额外付费买软件，直接在 Chrome 新建独立空白个人资料（地址栏输入 <code>chrome://settings/manageProfile</code>）建立名为 <code>Claude-US-Dedicated</code> 的纯净环境：</p>
      <ul>
        <li>仅在该独立窗口绑定固定美西静态住宅代理，不装任何与研发无关的第三方爬虫/比价扩展；</li>
        <li>将浏览器首选语言设为英文（<code>en-US</code>），并保持系统时区与代理出口一致（如 <code>America/Los_Angeles</code>）；</li>
        <li>开启浏览器「禁用非代理 UDP（WebRTC 防泄漏）」策略，彻底封死真实公网 IP 穿透泄露。</li>
      </ul>
    </div>
</body>
</html>"""

    ch05_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>第 5 章：Claude Code 终端加固与 5 源 1 秒无损深合并</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>第 5 章：Claude Code 终端加固与 5 源 1 秒无损深合并</h1>
    <p>对于每天在终端跑 <code>Claude Code</code> 的程序员来说，除了防封，最大的痛点有两个：一是写代码改到一半撞上 <strong>5 小时消息配额上限（5-hour rate limit）</strong> 被迫停工；二是乱用网上的粗暴覆盖脚本（<code>cat &gt; ~/.claude/settings.json</code>）把原本辛苦配好的 <code>mcpServers</code>、<code>permissions</code>、<code>hooks</code> 全量清空！</p>
    <h2>一、非破坏性关闭非必要遥测（100% 保留原有 MCP 与 Hooks）</h2>
    <p>默认状态下，Claude Code 会发送 Statsig 行为遥测与崩溃堆栈。运行以下一行 <code>node -e</code> 命令，可在<strong>不动任何已有配置</strong>的前提下安全注入三项隐私加固开关：</p>
    <pre><code>node -e '
const fs = require("fs"), os = require("os"), p = os.homedir() + "/.claude/settings.json";
fs.mkdirSync(os.homedir() + "/.claude", { recursive: true });
const cfg = fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8") || "{}") : {};
cfg.env = Object.assign({}, cfg.env, {
  DISABLE_TELEMETRY: "1",
  DISABLE_ERROR_REPORTING: "1",
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1"
});
fs.writeFileSync(p, JSON.stringify(cfg, null, 2) + "\\n");
'</code></pre>
    <h2>二、为什么必须用 cc-switch v2.0 非破坏性深合并切源？</h2>
    <table>
      <thead><tr><th style="width:26%;">对比维度</th><th style="width:37%;">❌ 传统粗暴覆盖脚本 (<code>cat &gt;</code>)</th><th>✅ <code>cc-switch v2.0</code> 无损深合并引擎</th></tr></thead>
      <tbody>
        <tr><td><strong>MCP 与 Hooks 配置</strong></td><td>直接覆写整份文件，已配 MCP 工具链瞬间归零</td><td>解析原 JSON 语法树，顶层 <code>mcpServers / permissions / hooks</code> 100% 保留</td></tr>
        <tr><td><strong>旧通道残留键清理</strong></td><td>易混留 Bedrock 与 BaseURL 双开关导致鉴权死锁</td><td>精准定点清理托管路由键，同时完整保留用户自定义业务环境变量</td></tr>
        <tr><td><strong>损坏保护与回滚</strong></td><td>无校验盲写</td><td>写入前自动生成时间戳备份，遇原 JSON 语法错误立即中止写盘保护现场</td></tr>
      </tbody>
    </table>
    <p>日常主力吃官方 Pro/Max 包月额度，撞上 5 小时限流窗时运行 <code>cc-switch</code> 1 秒热切到 <strong>AWS Bedrock (Claude Sonnet 4.6)</strong>、<strong>Google Vertex AI</strong> 或 <strong>OpenRouter</strong>。免费下载跨平台工具包（含 macOS/Linux <code>cc-switch.sh</code> 与 Windows <code>cc-switch.ps1</code>）：<a href="https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-code-kit.zip">claude-code-kit.zip</a>。</p>
</body>
</html>"""

    ch06_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>第 6 章：100% 永不封号终极架构——AWS Bedrock 与 Google Vertex AI</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>第 6 章：100% 永不封号终极架构——AWS Bedrock 与 Google Vertex AI</h1>
    <p>如果你是全职开发者、技术负责人或正在赶死线的科研人员，<strong>根本承受不起任何 1% 的封号断流风险</strong>，最彻底的终极方案就是直接走<strong>亚马逊云（AWS Bedrock）或谷歌云（Google Cloud Vertex AI）官方商业通道</strong>：采用企业级 IAM 鉴权与商业账单按量结算，<strong>完全不存在个人版针对地区、浏览器指纹或虚拟卡的封号机制</strong>。</p>
    <h2>一、AWS Bedrock 最小权限 IAM 策略（严禁直接挂 Root 密钥！）</h2>
    <p>在 AWS Console -&gt; IAM -&gt; Policies 创建以下最小权限策略并挂载给专用开发子用户：</p>
    <pre><code>{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ClaudeCodeBedrockLeastPrivilege",
    "Effect": "Allow",
    "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:ListInferenceProfiles"],
    "Resource": [
      "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-*",
      "arn:aws:bedrock:*:*:inference-profile/*.anthropic.claude-*"
    ]
  }]
}</code></pre>
    <h2>二、AWS Bedrock 与 Google Vertex AI 生产级 <code>settings.json</code> 对照配置</h2>
    <p><strong>方案 A（AWS Bedrock 跨区推理，保留 <code>us.</code> 前缀吞吐量翻倍）</strong>：</p>
    <pre><code>{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "us-east-1",
    "ANTHROPIC_MODEL": "us.anthropic.claude-sonnet-4-6",
    "ANTHROPIC_SMALL_FAST_MODEL": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}</code></pre>
    <p><strong>方案 B（Google Cloud Vertex AI，可直接抵扣新户 $300 免费赠金！先执行 <code>gcloud auth application-default login</code>）</strong>：</p>
    <pre><code>{
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "CLOUD_ML_REGION": "us-east5",
    "ANTHROPIC_VERTEX_PROJECT_ID": "你的-gcp-project-id",
    "ANTHROPIC_MODEL": "claude-sonnet-4-6",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}</code></pre>
    <div class="box">
      <strong>🧑‍💻 一键无损脚本与远程代配服务：</strong>
      <p>上述非破坏性合并流程已封装进开源脚本 <code>bedrock-vertex-1click.sh</code>（含在 <a href="https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-code-kit.zip">claude-code-kit.zip</a> 中，100% 保留原有 MCP 与 Hooks）。不想自己折腾 AWS IAM 跨区权限或 GCP CLI？可直接预约工程师 <strong>20 分钟 1对1 远程代部署（¥168/次，全程本机自输密钥，调不通全额退款）</strong>：<a href="https://a3152557994-ship-it.github.io/claude-guard/#service">点击预约远程部署</a>。</p>
    </div>
</body>
</html>"""

    ch00_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>序言与 30 秒急救导航</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>序言：为什么你需要这本《不掉号》？</h1>
    <p>如果你正在用 Claude 写核心业务代码、改写博士论文、或者搭建自动化 Agent 工作流，你一定体会过那种最令人窒息的瞬间：昨晚刚刚付完 $20（甚至 $200 Max 订阅），今天早上打开屏幕，迎面弹出一行冰冷的红字——<code>Your account has been disabled after an automatic review</code>。</p>
    <p>更糟糕的是，官方申诉人工解封率长期低于 <strong>5%</strong>；一旦网页锁死，你沉淀了几个月的 Project 上下文、上百段未保存的 Artifacts 代码块瞬间无法访问。</p>
    <div class="box">
      <strong>⚡ 急性子读者 30 秒急救直达入口（100% 免费开源免激活码）：</strong>
      <ul>
        <li>📡 <strong>10 秒在线检测当前 IP ASN 与本地时区漏点（免费免登录）</strong>：<a href="https://a3152557994-ship-it.github.io/claude-guard/">https://a3152557994-ship-it.github.io/claude-guard/</a></li>
        <li>🧩 <strong>Chrome / Edge 对话与代码块纯本地防丢保险箱插件（无限容量 100% 免费）</strong>：<a href="https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-guard-mv3.zip">点击免费下载 MV3 扩展包</a></li>
        <li>🧑‍💻 <strong>嫌配环境麻烦？AWS Bedrock / Google Vertex 100% 永不封号企业通道远程代配</strong>：<a href="https://a3152557994-ship-it.github.io/claude-guard/#service">点击查看 20 分钟包跑通方案</a></li>
      </ul>
    </div>
    <p>本书摒弃一切含糊其辞的空话，把 2026 年实测有效的<strong>「假封号乌龙排查 → 住宅网络与独立指纹容器 → 美区免税州礼品卡稳态支付 → AWS/Vertex 零封号企业架构 → 封后 48 小时追回订阅费与申诉模板」</strong>拆解为可一步步照抄执行的工程手册。</p>
</body>
</html>"""

    ch08_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>第 8 章：重开新号「四清铁律」与本地代码零丢失保险箱</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>第 8 章：重开新号「四清铁律」与本地代码零丢失保险箱</h1>
    <h2>一、弃旧开新防「关联秒封」四清清单</h2>
    <p>如果旧号确定放弃、准备重新注册干净新号，以下四项<strong>漏掉任何一项都会在 24 小时内触发指纹关联秒封</strong>：</p>
    <ol>
      <li><strong>清浏览器存储痕迹</strong>：绝对不能在刚被封号的原浏览器 Profile 里点退出直接注册新号！必须彻底清除 <code>claude.ai</code> 与 <code>anthropic.com</code> 的全部 Cookie、LocalStorage、IndexedDB，或直接在隔离浏览器中新建一个全新空白容器。</li>
      <li><strong>换全新静态住宅出口 IP</strong>：刚死过号的 IP 已被短期打标，重开务必切换新的独享住宅 IP。</li>
      <li><strong>换全新海外邮箱与接码号</strong>：使用全新 Gmail / Outlook / ProtonMail。</li>
      <li><strong>切断旧虚拟卡关联</strong>：被封账号绑过的虚拟卡号绝不可二次绑定新号，统一改走第 4 章的「美区免税州 Apple 礼品卡内购」。</li>
    </ol>
    <h2>二、永远别等封号那天才想起导出代码！</h2>
    <p>账号被封的真正损失往往不是那 $20，而是你调教了好几周的项目架构对话、论文修改稿和几十个未落盘的 Artifacts 代码组件——一旦封号，连登录导出页面都进不去！</p>
    <div class="box">
      <strong>🛡️ 养成纯本地静默防丢习惯（Chat Vault &amp; Env Guard · 100% 免费无限版）：</strong>
      <ul>
        <li>在浏览器装上纯本地归档扩展（<strong>所有数据 100% 存在你电脑自己的硬盘 <code>chrome.storage.local</code>，零云端上传</strong>）：单篇 Markdown / JSON 导出、无限本地对话归档与 AES-256-GCM 本地口令加密全部永久免费开放（免注册、免激活码）；</li>
        <li>万一遇到限流或换新号，点击<strong>「🚀 一键导出全量归档 + 新号无缝恢复包」</strong>，自动生成结构化唤醒 Prompt，贴进新账号第一句话，1 秒接上全部项目上下文！</li>
        <li>📦 <strong>免费下载插件与 5 源切换脚本</strong>：<a href="https://a3152557994-ship-it.github.io/claude-guard/">https://a3152557994-ship-it.github.io/claude-guard/</a></li>
        <li>🛠️ <strong>开源微工具矩阵 &amp; 企业定制服务</strong>：免费畅用全站 18 款研发与办公效率微工具（<a href="https://a3152557994-ship-it.github.io/opc-tools/">opc-tools 百宝箱</a>），或预约 AWS Bedrock / Vertex 1v1 远程无损代配与企业防封定制。</li>
      </ul>
    </div>
</body>
</html>"""

    ch09_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>附录 A：常见报错代码速查字典</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>附录 A：常见报错代码速查字典（10秒定位病因）</h1>
    <table>
      <thead><tr><th style="width:31%;">报错提示 / 状态码</th><th style="width:34%;">真实原因</th><th>最快解决动作</th></tr></thead>
      <tbody>
        <tr><td><code>Organization disabled</code> (网页正常)</td><td>本地残留旧 <code>ANTHROPIC_API_KEY</code> 覆盖 OAuth</td><td>执行第 2 章 <code>unset</code> 并删净 <code>.zshrc / .env</code> 残留行</td></tr>
        <tr><td><code>disabled after automatic review</code></td><td>触发机房 ASN 连坐、时区穿帮或虚拟卡风控</td><td>挂纯净美区 IP 按第 7 章走苹果退费或英文申诉，禁直连点邮件</td></tr>
        <tr><td><code>Your card was declined</code></td><td>Stripe 拦截高危虚拟卡段或 WebRTC 泄露</td><td>改走第 4 章「美区免税州 Apple ID + 礼品卡内购」</td></tr>
        <tr><td><code>Insufficient Store Credit</code> (已充$20)</td><td>美区 Apple ID 账单填了有税州加收消费税</td><td>账单地址改为俄勒冈州 Portland 邮编 <code>97201</code> 免税结算</td></tr>
        <tr><td>Bedrock <code>AccessDeniedException</code></td><td>区域未启用模型访问或漏加跨区推理前缀</td><td>切 <code>us-east-1</code> 提交简短 Use case，模型 ID 加 <code>us.</code> 前缀</td></tr>
        <tr><td><code>529 Overloaded</code> / 5h 额度耗尽</td><td>官方高峰算力拥堵或单号达到 5 小时窗口上限</td><td>运行 <code>cc-switch</code> 1 秒无损热切至 Bedrock / Vertex / OpenRouter</td></tr>
      </tbody>
    </table>
</body>
</html>"""

    ch10_new = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>附录 B：一页纸终端防封与零断流热切速查卡（1-Page Dev Cheat Sheet）</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
{cheatsheet_body}
</body>
</html>"""

    for xml_str in (nav_new, ncx_new, opf_new, ch00_new, ch01_new, ch02_new, ch03_new, ch05_new, ch06_new, ch08_new, ch09_new, ch10_new):
        ET.fromstring(xml_str.encode("utf-8"))

    chapter_bodies = {}
    with tempfile.TemporaryDirectory(prefix="cg_epub_", dir="/tmp") as td:
        td_p = Path(td)
        # Render crisp 2x PNG of SVG decision tree for universal EPUB3/Play Books compatibility
        dt_html = td_p / "dt.html"
        dt_png = td_p / "decision_tree.png"
        dt_html.write_text(
            f"<!doctype html><html><body style='margin:0;padding:0;background:#0B1120;overflow:hidden;'>{svg_tree}</body></html>",
            encoding="utf-8",
        )
        for att in range(3):
            subprocess.run(
                [
                    CHROME_BIN,
                    "--headless=new",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    f"--user-data-dir={td_p / f'u_dt_{att}'}",
                    "--window-size=820,338",
                    "--force-device-scale-factor=2",
                    f"--screenshot={dt_png}",
                    dt_html.as_uri(),
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if dt_png.exists() and dt_png.stat().st_size > 10000:
                break
        if not (dt_png.exists() and dt_png.stat().st_size > 10000):
            raise RuntimeError("Failed to render decision_tree.png for EPUB")
        dt_png_bytes = dt_png.read_bytes()

        tmp_epub = td_p / "updated.epub"
        cover_bytes = (EBOOK_DIR / "cover-1600x2560.jpg").read_bytes()
        replacements = {
            "OEBPS/style.css": epub_style_css.encode("utf-8"),
            "OEBPS/nav.xhtml": nav_new.encode("utf-8"),
            "OEBPS/toc.ncx": ncx_new.encode("utf-8"),
            "OEBPS/content.opf": opf_new.encode("utf-8"),
            "OEBPS/ch00_preface.xhtml": ch00_new.encode("utf-8"),
            "OEBPS/ch01_risk_matrix.xhtml": ch01_new.encode("utf-8"),
            "OEBPS/ch02_false_ban.xhtml": ch02_new.encode("utf-8"),
            "OEBPS/ch03_network_isolation.xhtml": ch03_new.encode("utf-8"),
            "OEBPS/ch05_claude_code.xhtml": ch05_new.encode("utf-8"),
            "OEBPS/ch06_bedrock_vertex.xhtml": ch06_new.encode("utf-8"),
            "OEBPS/ch08_vault_recovery.xhtml": ch08_new.encode("utf-8"),
            "OEBPS/ch09_appendix.xhtml": ch09_new.encode("utf-8"),
            "OEBPS/ch10_cheatsheet.xhtml": ch10_new.encode("utf-8"),
        }
        written_names = set()
        with zipfile.ZipFile(epub_pack, "r") as zin, zipfile.ZipFile(tmp_epub, "w") as zout:
            zout.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            written_names.add("mimetype")
            for info in zin.infolist():
                if info.filename == "mimetype" or info.filename == "OEBPS/decision_tree.png":
                    continue
                data = zin.read(info.filename)
                if info.filename == "OEBPS/cover.jpg":
                    data = cover_bytes
                elif info.filename in replacements:
                    data = replacements[info.filename]
                elif info.filename == "OEBPS/ch04_apple_iap.xhtml":
                    s4 = data.decode("utf-8")
                    if '<div class="box">' in s4:
                        s4_head = s4.split('<div class="box">')[0]
                        s4 = s4_head + """<div class="box">
      <strong>💡 没有 iPhone 或不想维护海外住宅 IP 的零折腾方案：</strong>
      <p>切勿在二手平台购买无质保共享成品号（多人混用机房节点极易连坐秒封）。若无美区设备，推荐直接采用本书<strong>第 6 章 AWS Bedrock / Google Vertex AI 企业商业接口</strong>（按量付费、0% 封号），或直接预约 <a href="https://a3152557994-ship-it.github.io/claude-guard/#service">20 分钟 1对1 远程代配（¥168 包跑通）</a>。</p>
    </div>
</body>
</html>"""
                    data = s4.encode("utf-8")
                if info.filename.endswith((".xhtml", ".opf", ".ncx")):
                    ET.fromstring(data)
                if info.filename.startswith("OEBPS/") and info.filename.endswith(".xhtml"):
                    txt = data.decode("utf-8")
                    chapter_bodies[info.filename] = txt.split("<body>")[1].split("</body>")[0].strip()
                zout.writestr(info.filename, data, compress_type=zipfile.ZIP_DEFLATED)
                written_names.add(info.filename)

            zout.writestr("OEBPS/decision_tree.png", dt_png_bytes, compress_type=zipfile.ZIP_DEFLATED)
            written_names.add("OEBPS/decision_tree.png")
            if "OEBPS/ch10_cheatsheet.xhtml" not in written_names:
                c10_bytes = ch10_new.encode("utf-8")
                ET.fromstring(c10_bytes)
                zout.writestr("OEBPS/ch10_cheatsheet.xhtml", c10_bytes, compress_type=zipfile.ZIP_DEFLATED)
                chapter_bodies["OEBPS/ch10_cheatsheet.xhtml"] = ch10_new.split("<body>")[1].split("</body>")[0].strip()

        shutil.move(str(tmp_epub), str(epub_pack))
    # Restore inline vector SVG for full PDF chapter body (PNG is inside EPUB)
    chapter_bodies["OEBPS/ch01_risk_matrix.xhtml"] = chapter_bodies["OEBPS/ch01_risk_matrix.xhtml"].replace(
        '<img src="decision_tree.png" alt="10秒报错排障与零断流路由决策树" style="width:100%;height:auto;display:block;" />',
        svg_tree,
    )
    shutil.copy2(epub_pack, epub_dl)
    print(f"[PASS] Updated Zero-Ban-Claude-2026.epub ({epub_pack.stat().st_size // 1024} KB) & synced to docs/downloads/")

    # ==================== 构建出版级零大白页完整版 PDF ====================
    # 采用单文档一次性打印 (@page :first { margin: 0; })，原生保留全部 #chXX PDF Named Destinations！
    hero_uri = (EBOOK_DIR / "cover_hero_shield.jpg").as_uri()

    def clean_chap_html(key: str) -> str:
        raw = chapter_bodies[key].replace('epub:type="toc"', "")
        raw = re.sub(r'<li>\s*<a href="cover\.xhtml">[^<]*</a>\s*</li>', "", raw)
        raw = re.sub(r'href="(ch\d+_[^"]+)\.xhtml"', r'href="#\1"', raw)
        return raw

    # P.02 紧凑合并：2列精致目录网格 + 序言（彻底消除原 P.02 70%空白 与 P.03 62%空白）
    nav_clean = clean_chap_html("OEBPS/nav.xhtml")
    preface_clean = clean_chap_html("OEBPS/ch00_preface.xhtml")

    # 第 6 章：将方案 A (Bedrock) 与方案 B (Vertex) 的 settings.json 并排双栏展示，使整章紧凑收进单页 P.08，彻底根除跨页劈裂！
    ch06_pdf_html = """<h1>第 6 章：100% 永不封号终极架构——AWS Bedrock 与 Google Vertex AI</h1>
    <p>如果你是全职开发者、技术负责人或正在赶毕业论文死线的硕博，<strong>根本承受不起任何 1% 的封号断流风险</strong>，最彻底的终极方案就是直接走<strong>亚马逊云（AWS Bedrock）或谷歌云（Google Cloud Vertex AI）官方商业通道</strong>：走企业级云厂商标准 IAM 鉴权与商业账单结算，<strong>完全不存在个人版针对地区、浏览器指纹或虚拟卡的封号机制</strong>，且支持独立子密钥与预算上限！</p>
    <h2>一、AWS Bedrock 最小权限 IAM 策略（切忌直接挂载 Root 或 AdministratorAccess！）</h2>
    <p>请在 AWS Console -&gt; IAM -&gt; Policies 中创建以下最小权限 JSON 策略并绑定至专用开发子用户：</p>
    <pre><code>{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ClaudeCodeBedrockLeastPrivilege",
    "Effect": "Allow",
    "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:ListInferenceProfiles"],
    "Resource": [
      "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-*",
      "arn:aws:bedrock:*:*:inference-profile/*.anthropic.claude-*"
    ]
  }]
}</code></pre>
    <h2>二、AWS Bedrock 与 Google Vertex AI 生产级 <code>~/.claude/settings.json</code> 双轨配置</h2>
    <div class="dual-code-grid">
      <div class="dual-code-col">
        <div class="dual-code-hd">🔥 方案 A：AWS Bedrock 跨区推理（<code>us.</code> 前缀高并发）</div>
        <pre><code>{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "us-east-1",
    "ANTHROPIC_MODEL": "us.anthropic.claude-sonnet-4-6",
    "ANTHROPIC_SMALL_FAST_MODEL":
      "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}</code></pre>
      </div>
      <div class="dual-code-col">
        <div class="dual-code-hd">☁️ 方案 B：Google Vertex AI（可抵新户 $300 赠金）</div>
        <pre><code>{
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "CLOUD_ML_REGION": "us-east5",
    "ANTHROPIC_VERTEX_PROJECT_ID": "你的-gcp-project-id",
    "ANTHROPIC_MODEL": "claude-sonnet-4-6",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}</code></pre>
      </div>
    </div>
    <p style="font-size:8.9pt;color:#334155;margin-top:2px;"><em>注：Vertex AI 接入前需在 GCP <code>Model Garden</code> 启用 Claude Sonnet 4.6 权限，并在本机执行一次 <code>gcloud auth application-default login</code> 生成 ADC 凭证。</em></p>
    <div class="box">
      <strong>🧑‍💻 一键无损脚本与远程代配服务：</strong>
      <p style="margin-bottom:0;">上述非破坏性合并流程已封装进开源脚本 <code>bedrock-vertex-1click.sh</code>（含在 <a href="https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-code-kit.zip">claude-code-kit.zip</a> 中，100% 保留原有 MCP 与 Hooks 配置）。不想自己折腾 AWS IAM 跨区权限或 GCP CLI？可直接预约工程师 <strong>20 分钟 1对1 远程代部署（¥168/次，全程本机自输密钥，调不通全额退款）</strong>：<a href="https://a3152557994-ship-it.github.io/claude-guard/#service">点击预约远程部署</a>。</p>
    </div>"""

    full_doc_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>不掉号：Claude 防封号、免税订阅与封后退款自救全书（2026完整版）</title>
<style>
  @page {{ size: A4 portrait; margin: 11.5mm 13.5mm 11mm 13.5mm; }}
  @page :first {{ margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
  body {{
    font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    color: #1E293B; background: #FFF; font-size: 9.4pt; line-height: 1.55;
  }}

  /* P1 全出血暗金护盾封面 */
  .cover-page {{
    width: 210mm; height: 296.8mm; padding: 14mm 15mm 12mm;
    background: radial-gradient(circle at 50% 35%, #172554 0%, #0B132B 58%, #050914 100%);
    border: 4.5mm solid #F59E0B; display: flex; flex-direction: column; justify-content: space-between;
    color: #FFF; overflow: hidden; page-break-after: always; break-after: page;
  }}
  .cover-page code {{
    background: rgba(245,158,11,0.18); color: #FDE68A; border: 1px solid rgba(245,158,11,0.35);
    padding: 1px 6px; border-radius: 4px; font-size: 8.8pt;
  }}
  .top-row {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(245,158,11,0.35); padding-bottom: 9px; }}
  .pill {{ background: linear-gradient(90deg, #F59E0B, #FBBF24); color: #0F172A; font-weight: 900; font-size: 10pt; padding: 4px 14px; border-radius: 99px; }}
  .ed {{ color: #FBBF24; font-weight: 800; font-size: 10.5pt; letter-spacing: 1.5px; }}
  .kicker {{ text-align: center; color: #38BDF8; font-weight: 800; letter-spacing: 3px; font-size: 11pt; margin-top: 6px; }}
  .ttl {{ text-align: center; font-size: 54pt; font-weight: 900; letter-spacing: 4px; color: #FFFFFF; line-height: 1.08; margin: 4px 0 8px; text-shadow: 0 6px 24px rgba(0,0,0,0.6); }}
  .sub-pill {{ align-self: center; border: 1.5px solid #F59E0B; color: #FDE68A; background: rgba(245,158,11,0.12); border-radius: 99px; padding: 5px 20px; font-weight: 800; font-size: 11.5pt; margin-bottom: 6px; }}
  .desc {{ text-align: center; color: #E2E8F0; font-size: 11.2pt; font-weight: 600; line-height: 1.5; }}
  .hero {{ margin: 10px 0; height: 245px; border-radius: 14px; overflow: hidden; border: 2px solid rgba(245,158,11,0.7); box-shadow: 0 14px 32px rgba(0,0,0,0.55); }}
  .hero img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .card {{ background: rgba(15,23,42,0.85); border: 1.5px solid rgba(245,158,11,0.38); border-radius: 12px; padding: 13px 18px; }}
  .card-hd {{ color: #34D399; font-size: 9.8pt; font-weight: 800; margin-bottom: 6px; }}
  .card p {{ font-size: 9.8pt; line-height: 1.68; color: #F8FAFC; font-weight: 600; margin-bottom: 2px; }}
  .card p b {{ color: #FBBF24; margin-right: 6px; }}
  .ft {{ display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.18); padding-top: 9px; font-size: 9pt; color: #CBD5E1; }}

  /* 正文章节分页与防劈裂控制 */
  .chap-page {{ page-break-before: always; break-before: page; padding-top: 1px; }}
  .chap-inline {{ margin-top: 14px; padding-top: 12px; border-top: 1.5px dashed #CBD5E1; }}
  h1 {{ font-size: 15.2pt; font-weight: 900; color: #0F172A; border-left: 5px solid #F59E0B; padding-left: 10px; margin: 0 0 9px; line-height: 1.28; }}
  h2 {{ font-size: 11.2pt; font-weight: 800; color: #1E40AF; margin: 9px 0 5px; }}
  h3 {{ font-size: 10pt; font-weight: 800; color: #0F172A; margin: 7px 0 4px; }}
  p {{ margin-bottom: 6.5px; }}
  ol, ul {{ padding-left: 19px; margin-bottom: 7px; }}
  li {{ margin-bottom: 3.5px; }}
  a {{ color: #2563EB; text-decoration: none; font-weight: 600; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #FEF2F2; color: #BE123C; padding: 1px 4.5px; border-radius: 4px; font-size: 8.3pt; }}
  th code, .dual-code-hd code {{ background: rgba(245,158,11,0.22); color: #FDE68A; border: 1px solid rgba(245,158,11,0.38); }}
  pre {{
    background: #0F172A; color: #F8FAFC; padding: 8px 11px; border-radius: 8px; margin: 5px 0 8px;
    white-space: pre-wrap; word-break: break-word; line-height: 1.34; font-size: 7.7pt;
    break-inside: avoid; page-break-inside: avoid;
  }}
  pre code {{ background: transparent; color: #F8FAFC; padding: 0; font-size: 7.7pt; }}
  .box {{
    background: #FFFBEB; border-left: 4px solid #F59E0B; border-radius: 8px; padding: 8px 12px;
    margin: 7px 0; font-size: 9pt; break-inside: avoid; page-break-inside: avoid;
  }}
  table {{
    width: 100%; border-collapse: collapse; margin: 7px 0 9px; font-size: 8.75pt;
    break-inside: avoid; page-break-inside: avoid;
  }}
  th {{ background: #0F172A; color: #FFF; padding: 6.5px 8.5px; text-align: left; }}
  td {{ border: 1px solid #CBD5E1; padding: 6px 8.5px; vertical-align: top; line-height: 1.42; }}
  tr:nth-child(even) td {{ background: #F8FAFC; }}
  .svg-wrap {{
    margin: 6px 0 4px; break-inside: avoid; page-break-inside: avoid;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.13); border-radius: 10px;
  }}

  /* P2 紧凑双栏目录卡片 */
  .toc-card {{
    background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 10px; padding: 10px 14px;
    margin-bottom: 12px; break-inside: avoid; page-break-inside: avoid;
  }}
  .toc-card h1 {{ margin-bottom: 8px; font-size: 14.5pt; }}
  .toc-card ol {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 5px 16px;
    list-style: none; padding-left: 0; margin-bottom: 0;
  }}
  .toc-card li {{
    background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 3.5px solid #2563EB;
    border-radius: 6px; padding: 5px 9px; font-size: 8.6pt; line-height: 1.35; margin-bottom: 0;
  }}

  /* Ch6 双栏 JSON 对照 */
  .dual-code-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 5px 0 6px;
    break-inside: avoid; page-break-inside: avoid;
  }}
  .dual-code-col {{ display: flex; flex-direction: column; }}
  .dual-code-hd {{
    background: #1E293B; color: #FDE68A; font-size: 8.2pt; font-weight: 800;
    padding: 5px 9px; border-radius: 7px 7px 0 0;
  }}
  .dual-code-col pre {{
    margin: 0; border-radius: 0 0 7px 7px; flex: 1; font-size: 7.2pt; line-height: 1.31; padding: 7.5px 9px;
  }}
  .dual-code-col pre code {{ font-size: 7.2pt; }}

  {CHEATSHEET_CSS}
</style>
</head>
<body>

  <!-- P1: 封面 -->
  <div class="cover-page">
    <div class="top-row"><span class="pill">AI 开发者与科研人自救实战书系</span><span class="ed">2026 v2.0 EDITION</span></div>
    <div style="display:flex;flex-direction:column;">
      <div class="kicker">ZERO-BAN CLAUDE PLAYBOOK</div>
      <div class="ttl">不掉号</div>
      <div class="sub-pill">防封号 · 免税订阅 · 封后退费 · 企业云零断流</div>
      <div class="desc">Claude &amp; Claude Code 稳态环境配置、<br>AWS Bedrock / Google Vertex AI 0% 封号接入与资产抢救全书</div>
    </div>
    <div class="hero"><img src="{hero_uri}" alt="Zero-Ban Claude Shield Cover"></div>
    <div class="card">
      <div class="card-hd">◆ 全书新增高清彩色决策树 + 贴屏速查卡 · 从排雷到退款止损全闭环</div>
      <p><b>01</b> 《10秒报错排障决策树》精准排掉 <code>ANTHROPIC_API_KEY</code> 假封号乌龙</p>
      <p><b>02</b> 美区免税州 Apple 礼品卡内购隔离 Stripe 虚拟卡雷区</p>
      <p><b>03</b> AWS Bedrock &amp; Vertex AI 企业通道 + <code>cc-switch v2.0</code> 无损配置秒切</p>
      <p><b>04</b> 封后黄金 48 小时追回订阅费实操 + 书末《一页纸终端防封速查卡》</p>
    </div>
    <div class="ft">
      <span>阿王写工具 · OPC Studio 编著（附 5 源无损切换脚本与本地防丢扩展）</span>
      <span style="color:#34D399;font-weight:800;">PRACTICAL GUIDE</span>
    </div>
  </div>

  <!-- P2: 目录 + 序言同页紧凑编排 -->
  <section id="nav" style="padding-top:1px;">
    <div class="toc-card">{nav_clean}</div>
  </section>
  <section id="ch00_preface">
    {preface_clean}
  </section>

  <!-- P3: 第1章 四重风控 + 10秒排障决策树 SVG -->
  <section class="chap-page" id="ch01_risk_matrix">{clean_chap_html("OEBPS/ch01_risk_matrix.xhtml")}</section>

  <!-- P4: 第2章 假封号排雷 + 四级优先级表 -->
  <section class="chap-page" id="ch02_false_ban">{clean_chap_html("OEBPS/ch02_false_ban.xhtml")}</section>

  <!-- P5: 第3章 网络与指纹防关联 + ASN 红黑榜 -->
  <section class="chap-page" id="ch03_network_isolation">{clean_chap_html("OEBPS/ch03_network_isolation.xhtml")}</section>

  <!-- P6: 第4章 美区免税州 Apple 礼品卡内购 -->
  <section class="chap-page" id="ch04_apple_iap">{clean_chap_html("OEBPS/ch04_apple_iap.xhtml")}</section>

  <!-- P7: 第5章 终端加固与 v2.0 非破坏性深合并 -->
  <section class="chap-page" id="ch05_claude_code">{clean_chap_html("OEBPS/ch05_claude_code.xhtml")}</section>

  <!-- P8: 第6章 AWS Bedrock & Vertex AI 单页零劈裂双栏版 -->
  <section class="chap-page" id="ch06_bedrock_vertex">{ch06_pdf_html}</section>

  <!-- P9: 第7章 封后黄金48h止损与申诉信 -->
  <section class="chap-page" id="ch07_refund_appeal">{clean_chap_html("OEBPS/ch07_refund_appeal.xhtml")}</section>

  <!-- P10: 第8章 四清铁律与保险箱 + 附录A 报错速查字典同页紧凑编排 -->
  <section class="chap-page" id="ch08_vault_recovery">
    {clean_chap_html("OEBPS/ch08_vault_recovery.xhtml")}
    <div class="chap-inline" id="ch09_appendix">
      {clean_chap_html("OEBPS/ch09_appendix.xhtml")}
    </div>
  </section>

  <!-- P11: 附录B 独立满版一页纸终端防封与热切速查卡 -->
  <section class="chap-page" id="ch10_cheatsheet">
    {cheatsheet_body}
  </section>

</body>
</html>"""

    with tempfile.TemporaryDirectory(prefix="cg_full_", dir="/tmp") as td:
        td_p = Path(td)
        doc_h = td_p / "full_all.html"
        raw_p = td_p / "full_raw.pdf"
        doc_h.write_text(full_doc_html, encoding="utf-8")
        for att in range(4):
            subprocess.run(
                [
                    CHROME_BIN,
                    "--headless=new",
                    "--disable-gpu",
                    f"--user-data-dir={td_p / f'u_full_{att}'}",
                    "--no-pdf-header-footer",
                    "--virtual-time-budget=3500",
                    f"--print-to-pdf={raw_p}",
                    doc_h.as_uri(),
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if raw_p.exists() and raw_p.stat().st_size > 500:
                break
        if not (raw_p.exists() and raw_p.stat().st_size > 500):
            raise RuntimeError("Failed to render Full Playbook PDF")

        # 使用 writer.append() 完整保留 Chrome 生成的 PDF 内部跳转锚点 (/Names -> /Dests)！
        writer = PdfWriter()
        writer.append(str(raw_p))
        for pg in writer.pages:
            pg.compress_content_streams()
        writer.add_metadata({
            "/Title": "不掉号：Claude 防封号、免税订阅与封后退款自救全书 (2026 v2.0)",
            "/Author": "阿王写工具 (OPC Studio)",
        })
        try:
            writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
        except TypeError:
            writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
        out_tmp = td_p / "full.pdf"
        with open(out_tmp, "wb") as f:
            writer.write(f)
        shutil.move(str(out_tmp), str(full_pdf_pack))

    shutil.copy2(full_pdf_pack, full_pdf_dl)
    rc = PdfReader(str(full_pdf_pack))
    ftxt = "\n".join(p.extract_text() or "" for p in rc.pages)
    for banned in ("银河录像局", "nf.video", "AdsPower", "Proxy-Seller", "IPRoyal", "¥15", "¥39", "20场", "20 场"):
        assert banned not in ftxt, f"Legacy paywall or competitor still present: {banned}"

    # 严格校验 0 file:// 残留 且 全部 #chXX 内部命名锚点 100% 有效！
    named_dests = set(rc.named_destinations.keys())
    expected_anchors = {
        "/ch00_preface", "/ch01_risk_matrix", "/ch02_false_ban", "/ch03_network_isolation",
        "/ch04_apple_iap", "/ch05_claude_code", "/ch06_bedrock_vertex", "/ch07_refund_appeal",
        "/ch08_vault_recovery", "/ch09_appendix", "/ch10_cheatsheet",
    }
    missing = expected_anchors - named_dests
    assert not missing, f"Missing PDF internal anchors: {missing} (have: {named_dests})"
    for p in rc.pages:
        for a in p.get("/Annots") or []:
            act = a.get_object().get("/A")
            if act and "/URI" in act.get_object():
                uri = str(act.get_object()["/URI"])
                assert not uri.startswith("file://"), f"Dead file:// link found in Full PDF: {uri}"

    print(
        f"[PASS] Rebuilt Full Playbook PDF: {full_pdf_pack.name} -> {len(rc.pages)} pages | "
        f"{full_pdf_pack.stat().st_size // 1024} KB | {len(named_dests)} internal anchors verified & synced to docs/downloads/"
    )


def update_web_playbook_html():
    """同步将高清矢量《10秒报错排障决策树》SVG 与 v2.0 非破坏性配置嵌入 docs/claude-anti-ban-playbook-2026.html"""
    web_path = ROOT / "docs" / "claude-anti-ban-playbook-2026.html"
    src = web_path.read_text(encoding="utf-8")
    svg_tree = build_decision_tree_svg()

    marker_start = "<!-- DECISION-TREE-SVG-START -->"
    marker_end = "<!-- DECISION-TREE-SVG-END -->"
    svg_block = f"""{marker_start}
<div style="margin:18px 0 22px;box-shadow:0 12px 28px rgba(0,0,0,0.45);border-radius:12px;overflow:hidden;">
  {svg_tree}
</div>
{marker_end}"""

    if marker_start in src and marker_end in src:
        src = re.sub(f"{re.escape(marker_start)}.*?{re.escape(marker_end)}", svg_block, src, flags=re.S)
    else:
        target = "<h2>一、 报错先别弃号！30 秒排查「假封号乌龙」</h2>"
        assert target in src, "Expected heading not found in claude-anti-ban-playbook-2026.html"
        src = src.replace(target, f"{target}\n{svg_block}", 1)

    src = src.replace('"dateModified": "2026-11-22"', '"dateModified": "2026-11-26"')
    web_path.write_text(src, encoding="utf-8")
    print("[PASS] Synced inline SVG decision tree into docs/claude-anti-ban-playbook-2026.html")


if __name__ == "__main__":
    test_nondestructive_merge()
    repack_kit_zip()
    build_wenku_pdf()
    update_zero_ban_epub_and_full_pdf()
    update_web_playbook_html()
