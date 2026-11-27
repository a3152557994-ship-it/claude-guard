# -*- coding: utf-8 -*-
"""
Generate & unify Xianyu 1080x1080 product showcase images for claude-guard (Zero-Paywall Edition):
- Theme: 「全套 2026 防封全书 + 出口体检插件 + 零断流脚本 0 元免费送（不卖激活码不拦人）｜另承接 AWS Bedrock / Vertex 1v1 远程无损代配与团队防封定制」
- Generates:
  1. release/xianyu-01-cover.png (+ release/xianyu-01.png & media/20261118-claude-guard/xianyu-01-cover.png)
  2. release/xianyu-02-terminal.png (+ release/xianyu-02.png & media/20261118-claude-guard/xianyu-02-terminal.png)
  3. release/xianyu-03-plugin.png (+ release/xianyu-03.png & media/20261118-claude-guard/xianyu-03-plugin.png)
  4. release/xianyu-04-interior-showcase.png (+ release/xianyu-04.png & release/cashflow-service-pack/xianyu-04-interior-showcase.png)
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

ROOT = Path("/Users/wang/OPC/projects/claude-guard")
RELEASE_DIR = ROOT / "release"
SERVICE_PACK_DIR = RELEASE_DIR / "cashflow-service-pack"
EBOOK_DIR = RELEASE_DIR / "ebook-publishing-pack"
MEDIA_SYNC_DIR = Path("/Users/wang/OPC/media/20261118-claude-guard")
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


SWIFT_PDF_RENDER = """
import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 5 else { exit(1) }
let pdfPath = args[1]
let pageIndex = Int(args[2])! - 1
let outPath = args[3]
let targetWidth = CGFloat(Double(args[4])!)

guard let doc = PDFDocument(url: URL(fileURLWithPath: pdfPath)),
      let page = doc.page(at: pageIndex) else {
    fputs("Failed to open PDF or page\\n", stderr)
    exit(2)
}

let bounds = page.bounds(for: .mediaBox)
let scale = targetWidth / bounds.width
let targetHeight = ceil(bounds.height * scale)
let imgSize = NSSize(width: targetWidth, height: targetHeight)

guard let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: Int(targetWidth),
    pixelsHigh: Int(targetHeight),
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: .deviceRGB,
    bytesPerRow: 0,
    bitsPerPixel: 0
) else { exit(3) }

NSGraphicsContext.saveGraphicsState()
if let ctx = NSGraphicsContext(bitmapImageRep: rep) {
    NSGraphicsContext.current = ctx
    let cg = ctx.cgContext
    cg.setFillColor(NSColor.white.cgColor)
    cg.fill(CGRect(origin: .zero, size: imgSize))
    cg.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: cg)
}
NSGraphicsContext.restoreGraphicsState()

guard let pngData = rep.representation(using: .png, properties: [:]) else { exit(4) }
try pngData.write(to: URL(fileURLWithPath: outPath))
"""


def render_html_to_1080_png(html_content: str, out_png: Path, td_p: Path, tag: str):
    hf = td_p / f"{tag}.html"
    raw_png = td_p / f"{tag}_raw.png"
    hf.write_text(html_content, encoding="utf-8")
    for attempt in range(4):
        subprocess.run(
            [
                CHROME_BIN,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--user-data-dir={td_p / f'u_{tag}_{attempt}'}",
                "--window-size=1080,1080",
                "--force-device-scale-factor=2",
                "--virtual-time-budget=2500",
                f"--screenshot={raw_png}",
                hf.as_uri(),
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if raw_png.exists() and raw_png.stat().st_size > 5000:
            break
    if not (raw_png.exists() and raw_png.stat().st_size > 5000):
        raise RuntimeError(f"Failed to screenshot {tag}")

    with Image.open(raw_png) as im:
        rgb = im.convert("RGB")
        if rgb.size != (1080, 1080):
            rgb = rgb.resize((1080, 1080), Image.Resampling.LANCZOS)
        rgb.save(out_png, format="PNG", optimize=True)


def build_xianyu_01_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: 1080px; height: 1080px; overflow: hidden;
    background: #060A14; color: #F8FAFC;
    font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  }
  .canvas {
    width: 1080px; height: 1080px; padding: 50px 58px 48px;
    display: flex; flex-direction: column; justify-content: space-between;
    background:
      radial-gradient(circle at 82% 14%, rgba(16,185,129,0.16) 0%, transparent 45%),
      radial-gradient(circle at 18% 85%, rgba(245,158,11,0.13) 0%, transparent 48%),
      #060A14;
  }
  .pill {
    display: inline-block; border: 2px solid #10B981; background: rgba(16,185,129,0.14);
    color: #6EE7B7; font-size: 22px; font-weight: 800; padding: 8px 24px; border-radius: 99px;
  }
  .h1 { font-size: 56px; font-weight: 900; line-height: 1.18; margin-top: 18px; color: #FFFFFF; }
  .h1 span { color: #FBBF24; }
  .sub { font-size: 25px; color: #94A3B8; margin-top: 12px; font-weight: 600; }
  .items { display: flex; flex-direction: column; gap: 18px; }
  .item {
    background: #0D1528; border: 1.8px solid #233256; border-radius: 20px;
    padding: 24px 28px; display: flex; align-items: center; gap: 22px;
  }
  .num {
    width: 68px; height: 68px; border-radius: 16px; display: flex; align-items: center;
    justify-content: center; font-size: 28px; font-weight: 900; flex-shrink: 0;
  }
  .n1 { background: rgba(56,189,248,0.2); color: #38BDF8; border: 1.5px solid rgba(56,189,248,0.5); }
  .n2 { background: rgba(245,158,11,0.2); color: #FBBF24; border: 1.5px solid rgba(245,158,11,0.5); }
  .n3 { background: rgba(16,185,129,0.2); color: #34D399; border: 1.5px solid rgba(16,185,129,0.5); }
  .it-title { font-size: 27px; font-weight: 800; color: #F8FAFC; margin-bottom: 6px; }
  .it-desc { font-size: 21px; color: #94A3B8; line-height: 1.38; }
  .footer-bar {
    background: linear-gradient(90deg, #064E3B 0%, #0F172A 55%, #172554 100%);
    border: 2px solid #10B981; border-radius: 18px; padding: 20px 26px;
  }
  .fb-top { font-size: 24px; font-weight: 900; color: #6EE7B7; margin-bottom: 6px; }
  .fb-bot { font-size: 21px; font-weight: 700; color: #FDE68A; }
</style>
</head>
<body>
  <div class="canvas">
    <div>
      <span class="pill">🎉 2026 开源防封百宝箱 · 0 元免费送（不卖激活码不拦人）</span>
      <div class="h1">全套防封全书 + 体检插件<br/><span>+ 零断流脚本 ¥0 免码全送</span></div>
      <div class="sub">拒绝把人拒之门外的收费锁！工具全免费，另承接企业云 1v1 远程代配</div>
    </div>

    <div class="items">
      <div class="item">
        <div class="num n1">01</div>
        <div>
          <div class="it-title">2026 防封与退款自救全书（15页矢量 PDF + EPUB 免费送）</div>
          <div class="it-desc">含 10 秒排障彩色决策树、美区免税州订阅避坑与封后退费申诉模板</div>
        </div>
      </div>
      <div class="item">
        <div class="num n2">02</div>
        <div>
          <div class="it-title">出口 ASN 体检插件 + 无限容量防丢保险箱（MV3 免码全开）</div>
          <div class="it-desc">实时揪出机房 IP / 东八区时区穿帮，无限本地备份 + AES-256 口令加密</div>
        </div>
      </div>
      <div class="item">
        <div class="num n3">03</div>
        <div>
          <div class="it-title">cc-switch v2.0 五源 1 秒无损热切脚本（Mac/Win/Linux）</div>
          <div class="it-desc">一键开启防遥测，无损保留原有 MCP/Hooks，秒切 Bedrock / Vertex</div>
        </div>
      </div>
    </div>

    <div class="footer-bar">
      <div class="fb-top">✅ 全套软件 / 插件 / 脚本 / 电子书：私信或自助 0 元免费领（绝不卖激活码）</div>
      <div class="fb-bot">🛠️ 嫌配置麻烦？另承接 AWS Bedrock / Vertex 1v1 远程无损代配与团队防封定制</div>
    </div>
  </div>
</body>
</html>"""


def build_xianyu_02_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: 1080px; height: 1080px; overflow: hidden;
    background: #060A12; color: #F8FAFC;
    font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  }
  .canvas {
    width: 1080px; height: 1080px; padding: 48px 56px 46px;
    display: flex; flex-direction: column; justify-content: space-between;
  }
  .hdr-title { font-size: 40px; font-weight: 900; color: #FBBF24; }
  .hdr-sub { font-size: 23px; color: #94A3B8; margin-top: 10px; font-weight: 600; }
  .term-box {
    background: #0B101B; border: 2px solid #233256; border-radius: 20px; padding: 28px 34px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  }
  .dots { display: flex; gap: 10px; align-items: center; margin-bottom: 18px; }
  .dot { width: 15px; height: 15px; border-radius: 50%; display: inline-block; }
  .t-line { font-size: 21px; line-height: 1.68; color: #E2E8F0; }
  .c-amber { color: #FBBF24; font-weight: 700; }
  .c-rose { color: #FB7185; font-weight: 700; }
  .c-green { color: #34D399; font-weight: 700; }
  .switch-box {
    background: #0B1424; border: 2px solid #10B981; border-radius: 20px; padding: 28px 34px;
  }
  .sw-hd { font-size: 27px; font-weight: 800; color: #34D399; margin-bottom: 16px; }
  .sw-line { font-size: 21.5px; line-height: 1.66; color: #E2E8F0; }
  .bottom-note {
    background: #111C33; border: 1.5px solid #38BDF8; border-radius: 16px; padding: 16px 20px;
    font-size: 19.5px; font-weight: 800; color: #BAE6FD; text-align: center; white-space: nowrap;
  }
</style>
</head>
<body>
  <div class="canvas">
    <div>
      <div class="hdr-title">终端实机运行实拍（脚本 0 元开源免码直用）</div>
      <div class="hdr-sub">上：env-doctor.mjs 10秒漏点扫描 ｜ 下：cc-switch v2.0 五源无损热切</div>
    </div>

    <div class="term-box">
      <div class="dots">
        <span class="dot" style="background:#F43F5E;"></span>
        <span class="dot" style="background:#F59E0B;"></span>
        <span class="dot" style="background:#10B981;"></span>
        <span style="color:#94A3B8;font-size:19px;margin-left:8px;">zsh — node kit/env-doctor.mjs</span>
      </div>
      <div class="t-line c-amber">Claude Guard — 本地终端防封环境自检报告 (CLI Doctor)</div>
      <div class="t-line">· 操作系统平台 : darwin (arm64) ｜ 系统时区 : Asia/Shanghai (UTC+8)</div>
      <div class="t-line">· 配置文件路径 : ~/.claude/settings.json</div>
      <div class="t-line c-amber">[风险 -20] 系统时区暴露东八区，挂欧美机房节点易触发跨洲异常标记</div>
      <div class="t-line c-rose">[风险 -25] 未开启 DISABLE_TELEMETRY=1 与非必要流量屏蔽！</div>
      <div class="t-line c-green">终端环境初始评分: 55 / 100  --&gt;  一键加固后评分: 95 / 100</div>
    </div>

    <div class="switch-box">
      <div class="sw-hd">~/.claude/settings.json 非破坏性深合并 · 5 源 1 秒热备切换：</div>
      <div class="sw-line">[1] 官方账号 · 隐私防遥测加固 (DISABLE_TELEMETRY=1)</div>
      <div class="sw-line">[2] AWS Bedrock · 企业级零封号直连 (CLAUDE_CODE_USE_BEDROCK=1)</div>
      <div class="sw-line">[3] Google Cloud Vertex AI · 零封号商业通道 (可抵扣 GCP $300 赠金)</div>
      <div class="sw-line">[4] OpenRouter 聚合网关 · 5小时限流无缝顶上不断活</div>
      <div class="sw-line">[5] 国产高性价比兼容源 · 离线兜底模式 (100% 保留原有 mcpServers/hooks)</div>
    </div>

    <div class="bottom-note">
      🎁 全书+插件+脚本 0元免费送（不拦人） ｜ 🛠️ 承接 AWS Bedrock / Vertex 1v1远程无损代配
    </div>
  </div>
</body>
</html>"""


def build_xianyu_03_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: 1080px; height: 1080px; overflow: hidden;
    background: #060A12; color: #F8FAFC;
    font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  }
  .canvas {
    width: 1080px; height: 1080px; padding: 52px 58px 50px;
    display: flex; flex-direction: column; justify-content: space-between;
    background: radial-gradient(circle at 85% 12%, rgba(16,185,129,0.12) 0%, rgba(6,10,18,0) 48%), #060A12;
  }
  .hdr-title { font-size: 40px; font-weight: 800; color: #22C55E; line-height: 1.2; white-space: nowrap; }
  .hdr-sub { font-size: 23px; color: #94A3B8; margin-top: 12px; font-weight: 500; white-space: nowrap; }

  .vault-card {
    background: #0D1526; border: 2px solid #38BDF8; border-radius: 22px;
    padding: 34px 38px; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
  }
  .vault-hd { font-size: 31px; font-weight: 800; color: #FFFFFF; margin-bottom: 22px; white-space: nowrap; }
  .vault-list { list-style: none; display: flex; flex-direction: column; gap: 16px; }
  .vault-list li { font-size: 22px; color: #CBD5E1; line-height: 1.45; white-space: nowrap; }
  .vault-list li b { color: #F1F5F9; }
  .vault-free {
    margin-top: 22px; padding-top: 18px; border-top: 1px solid rgba(56, 189, 248, 0.24);
    font-size: 22.5px; font-weight: 800; color: #34D399; white-space: nowrap;
  }

  .tier-card {
    background: #0D1422; border: 2px solid #F59E0B; border-radius: 22px;
    padding: 32px 38px; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
  }
  .tier-hd { font-size: 29px; font-weight: 800; color: #F59E0B; margin-bottom: 20px; white-space: nowrap; }
  .tier-rows { display: flex; flex-direction: column; gap: 16px; }
  .tier-row { font-size: 19.5px; color: #E2E8F0; line-height: 1.42; display: flex; align-items: center; gap: 12px; white-space: nowrap; }
  .price-pill {
    display: inline-block; font-weight: 900; padding: 4px 10px; border-radius: 8px; font-size: 18.5px; flex-shrink: 0; min-width: 176px; text-align: center;
  }
  .p-green { background: rgba(16,185,129,0.18); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.45); }
  .p-amber { background: rgba(245,158,11,0.18); color: #FCD34D; border: 1px solid rgba(245,158,11,0.45); }
  .p-blue { background: rgba(56,189,248,0.16); color: #7DD3FC; border: 1px solid rgba(56,189,248,0.45); }
  .tier-note { font-size: 19px; color: #94A3B8; margin-top: 4px; white-space: nowrap; }
</style>
</head>
<body>
  <div class="canvas">
    <div>
      <div class="hdr-title">配套 Chrome/Edge 无限容量防丢插件 (0元免码)</div>
      <div class="hdr-sub">等账号被封再装导出插件已经进不去网页了！平时自动落盘本地硬盘才稳</div>
    </div>

    <div class="vault-card">
      <div class="vault-hd">Claude Guard 浏览器防丢保险箱 (100% 本地零云端上传)</div>
      <ul class="vault-list">
        <li>· <b>实时出口预警灯</b>：检测到机房共享 ASN 或东八区时区暴露立即亮灯提醒</li>
        <li>· <b>无限容量全免费</b>：取消 20 场容量锁，对话 + Artifacts 代码块无限本地归档</li>
        <li>· <b>AES-256 口令加密</b>：免费支持自定义口令加密备份与「新号 1 秒恢复上下文包」</li>
      </ul>
      <div class="vault-free">★ 零门槛承诺：全套插件 · 脚本 · 15页防封全书 0 元免费送（不卖激活码不拦人）</div>
    </div>

    <div class="tier-card">
      <div class="tier-hd">免费领工具 &amp; 工程师人工技术服务说明（公开透明 · 零套路）</div>
      <div class="tier-rows">
        <div class="tier-row">
          <span class="price-pill p-green">1. 工具全套 0 元送</span>
          <span>0 元免费送 2026 防封全书 PDF/EPUB + <b>无限版备份插件</b> + 5源切换脚本</span>
        </div>
        <div class="tier-row">
          <span class="price-pill p-amber">2. 1v1 远程无损代配</span>
          <span>工程师远程 20 分钟配通 <b>AWS Bedrock / Vertex 零封号通道</b>（不通全退）</span>
        </div>
        <div class="tier-row">
          <span class="price-pill p-blue">3. 团队防封架构定制</span>
          <span>企业多席位最小权限 IAM 策略、多源容灾路由与算力预算熔断定制部署</span>
        </div>
        <div class="tier-note">合规边界：纯本地开源研发辅助工具与正规云厂商 IAM 架构调试，不含任何违规账号或节点</div>
      </div>
    </div>
  </div>
</body>
</html>"""


def build_xianyu_04_showcase_html(p3_uri: str, p15_uri: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 1080px; height: 1080px; overflow: hidden;
    background: #060B16; color: #F8FAFC;
    font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  }}
  .canvas {{
    width: 1080px; height: 1080px; padding: 38px 46px 36px;
    display: flex; flex-direction: column; justify-content: space-between;
    background:
      radial-gradient(circle at 18% 18%, rgba(245,158,11,0.13) 0%, transparent 45%),
      radial-gradient(circle at 85% 32%, rgba(56,189,248,0.12) 0%, transparent 46%),
      #060B16;
  }}
  .top-bar {{ display: flex; justify-content: space-between; align-items: center; }}
  .kicker-pill {{
    display: inline-block; border: 1.5px solid #10B981; background: rgba(16,185,129,0.14);
    color: #6EE7B7; font-size: 20px; font-weight: 800; padding: 6px 20px; border-radius: 99px;
  }}
  .ver-tag {{
    background: #1E293B; border: 1px solid #334155; color: #38BDF8;
    font-size: 18px; font-weight: 800; padding: 6px 16px; border-radius: 99px;
  }}
  .main-title {{ font-size: 38px; font-weight: 900; color: #FFFFFF; margin-top: 10px; letter-spacing: 0.3px; }}
  .main-title span {{ color: #FBBF24; }}
  .sub-title {{ font-size: 21px; color: #94A3B8; margin-top: 6px; font-weight: 600; }}

  .pages-grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin: 12px 0;
  }}
  .shot-card {{
    background: linear-gradient(180deg, #111C33 0%, #0B1324 100%);
    border: 2px solid rgba(245, 158, 11, 0.55); border-radius: 18px;
    padding: 13px 14px 12px; display: flex; flex-direction: column;
    box-shadow: 0 20px 44px rgba(0, 0, 0, 0.6);
  }}
  .shot-card.right {{ border-color: rgba(56, 189, 248, 0.6); }}
  .shot-bar {{
    display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 10px;
  }}
  .shot-lbl {{ font-size: 18px; font-weight: 800; color: #FDE68A; }}
  .shot-card.right .shot-lbl {{ color: #7DD3FC; }}
  .shot-tag {{
    font-size: 13.5px; font-weight: 800; padding: 3px 9px; border-radius: 6px; flex-shrink: 0;
    background: rgba(16,185,129,0.2); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.4);
  }}
  .paper-viewport {{
    width: 100%; height: 492px; border-radius: 10px; overflow: hidden;
    background: #FFFFFF; border: 1px solid #334155; position: relative;
  }}
  .paper-viewport img.p3 {{
    width: 108%; margin-left: -4%; margin-top: -18px; display: block;
  }}
  .paper-viewport img.p15 {{
    width: 104%; margin-left: -2%; margin-top: -12px; display: block;
  }}
  .shot-caption {{
    margin-top: 9px; font-size: 15.2px; color: #CBD5E1; line-height: 1.38; font-weight: 600; white-space: nowrap;
  }}

  .diff-box {{
    background: #0D1628; border: 1.5px solid #334155; border-radius: 16px;
    padding: 16px 22px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  }}
  .diff-bad {{
    background: rgba(244, 63, 94, 0.10); border-left: 4px solid #F43F5E;
    padding: 10px 14px; border-radius: 8px;
  }}
  .diff-good {{
    background: rgba(16, 185, 129, 0.12); border-left: 4px solid #10B981;
    padding: 10px 14px; border-radius: 8px;
  }}
  .diff-hd {{ font-size: 20px; font-weight: 900; margin-bottom: 5px; }}
  .diff-bad .diff-hd {{ color: #FDA4AF; }}
  .diff-good .diff-hd {{ color: #6EE7B7; }}
  .diff-txt {{ font-size: 17.5px; color: #E2E8F0; line-height: 1.4; }}
  code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    background: rgba(15,23,42,0.75); color: #FDE68A; padding: 1px 6px; border-radius: 5px; font-size: 16.5px;
  }}

  .bottom-strip {{
    background: linear-gradient(90deg, #064E3B 0%, #172554 55%, #0F172A 100%);
    border: 1.8px solid #10B981; border-radius: 14px; padding: 14px 20px;
    display: flex; justify-content: space-between; align-items: center;
    font-size: 19px; font-weight: 800; color: #F8FAFC;
  }}
  .bottom-strip span.hl-green {{ color: #6EE7B7; }}
  .bottom-strip span.hl-amber {{ color: #FBBF24; }}
  .sep {{ color: #475569; }}
</style>
</head>
<body>
  <div class="canvas">
    <div>
      <div class="top-bar">
        <span class="kicker-pill">🎁 15页精排版全书 + 插件 + 脚本 0元免费送（不卖激活码）</span>
        <span class="ver-tag">2026 v2.0 工程实测版</span>
      </div>
      <div class="main-title">内页微距实拍：<span>彩色排障决策树 + 一页纸贴屏速查卡</span></div>
      <div class="sub-title">全套 PDF / EPUB / 体检插件 / 五源无损脚本零门槛免费领 · 另承接企业云远程代配</div>
    </div>

    <div class="pages-grid">
      <div class="shot-card">
        <div class="shot-bar">
          <span class="shot-lbl">📊 P.03 实拍 · 10秒报错排障决策树</span>
          <span class="shot-tag">0元免费送完整版</span>
        </div>
        <div class="paper-viewport">
          <img class="p3" src="{p3_uri}" alt="PDF Page 3 Decision Tree Real Render" />
        </div>
        <div class="shot-caption">三大分支秒判「30%环境变量假封号 / ASN风控止损 / 企业云零断流」</div>
      </div>

      <div class="shot-card right">
        <div class="shot-bar">
          <span class="shot-lbl">🗂️ 书末实拍 · 一页纸贴屏速查卡</span>
          <span class="shot-tag">双栏高清矢量</span>
        </div>
        <div class="paper-viewport">
          <img class="p15" src="{p15_uri}" alt="PDF Page 15 1-Page Dev Cheat Sheet Real Render" />
        </div>
        <div class="shot-caption">四级凭据金字塔 + 五源参数速查表 + 四清铁律 + 体检命令</div>
      </div>
    </div>

    <div class="diff-box">
      <div class="diff-bad">
        <div class="diff-hd">❌ 普通覆盖脚本 (cat &gt; settings.json)</div>
        <div class="diff-txt">粗暴全量覆盖配置文件，切一次源直接把辛苦配好的 <code>mcpServers</code> 与 <code>hooks</code> 清空归零！</div>
      </div>
      <div class="diff-good">
        <div class="diff-hd">✅ 本套 cc-switch v2.0 非破坏性深合并</div>
        <div class="diff-txt">解析 JSON 语法树仅更新 <code>env</code> 路由键，<b>100% 无损保留原有 MCP 与钩子</b>！</div>
      </div>
    </div>

    <div class="bottom-strip">
      <span class="hl-green">🎁 全书+插件+脚本 0元免费送（不拦人）</span>
      <span class="sep">｜</span>
      <span class="hl-amber">🛠️ 另承接 AWS Bedrock / Vertex 1v1远程无损代配与团队定制</span>
    </div>
  </div>
</body>
</html>"""


def main():
    wenku_pdf = EBOOK_DIR / "不掉号-不断流_ClaudeCode企业云合规接入与排障手册_2026国内文库版.pdf"
    if not wenku_pdf.exists():
        raise FileNotFoundError(f"Run build_ebooks.py first; missing {wenku_pdf}")

    with tempfile.TemporaryDirectory(prefix="cg_xy_", dir="/tmp") as td:
        td_p = Path(td)
        swift_file = td_p / "render_pdf.swift"
        swift_file.write_text(SWIFT_PDF_RENDER, encoding="utf-8")

        p3_png = td_p / "pdf_p03.png"
        p15_png = td_p / "pdf_p15.png"
        subprocess.run(["swift", str(swift_file), str(wenku_pdf), "3", str(p3_png), "1240"], check=True)
        subprocess.run(["swift", str(swift_file), str(wenku_pdf), "15", str(p15_png), "1240"], check=True)

        targets = [
            ("xy01", build_xianyu_01_html(), "xianyu-01-cover.png"),
            ("xy02", build_xianyu_02_html(), "xianyu-02-terminal.png"),
            ("xy03", build_xianyu_03_html(), "xianyu-03-plugin.png"),
            ("xy04", build_xianyu_04_showcase_html(p3_png.as_uri(), p15_png.as_uri()), "xianyu-04-interior-showcase.png"),
        ]

        for idx, (tag, html_str, fname) in enumerate(targets, 1):
            out_main = RELEASE_DIR / fname
            render_html_to_1080_png(html_str, out_main, td_p, tag)
            print(f"[PASS] Built {out_main} ({out_main.stat().st_size // 1024} KB)")

            # Sync to media/20261118-claude-guard/ if directory & matching file exist
            if MEDIA_SYNC_DIR.exists() and (MEDIA_SYNC_DIR / fname).exists():
                shutil.copy2(out_main, MEDIA_SYNC_DIR / fname)
                print(f"  -> Synced {MEDIA_SYNC_DIR / fname}")

        shutil.copy2(RELEASE_DIR / "xianyu-04-interior-showcase.png", SERVICE_PACK_DIR / "xianyu-04-interior-showcase.png")
        print(f"  -> Synced {SERVICE_PACK_DIR / 'xianyu-04-interior-showcase.png'}")


if __name__ == "__main__":
    main()
