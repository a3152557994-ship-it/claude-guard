# -*- coding: utf-8 -*-
"""
Generate & unify Xianyu 1080x1080 product showcase images for claude-guard:
1. Update release/xianyu-03-plugin.png:
   - Fix conflicting old ¥49 remote setup price -> unify with site-wide ¥9.9 / ¥39 (¥15 single) / ¥168 tiers.
2. Generate release/xianyu-04-interior-showcase.png (and sync to release/cashflow-service-pack/xianyu-04-interior-showcase.png):
   - Rasterize genuine newly built PDF pages (P.03 Color SVG Decision Tree & P.15 1-Page Dev Cheat Sheet) via macOS PDFKit
   - Macro-showcase the real PDF interior pages + non-destructive JSON merge comparison + unified pricing bar.
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
    width: 1080px; height: 1080px; padding: 54px 62px 52px;
    display: flex; flex-direction: column; justify-content: space-between;
    background: radial-gradient(circle at 85% 12%, rgba(16,185,129,0.10) 0%, rgba(6,10,18,0) 48%), #060A12;
  }
  .hdr-title { font-size: 41px; font-weight: 800; color: #22C55E; letter-spacing: 0.3px; line-height: 1.2; white-space: nowrap; }
  .hdr-sub { font-size: 23.5px; color: #94A3B8; margin-top: 12px; font-weight: 500; white-space: nowrap; }

  .vault-card {
    background: #0D1526; border: 2px solid #38BDF8; border-radius: 22px;
    padding: 36px 42px; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
  }
  .vault-hd { font-size: 32px; font-weight: 800; color: #FFFFFF; margin-bottom: 24px; white-space: nowrap; }
  .vault-list { list-style: none; display: flex; flex-direction: column; gap: 18px; }
  .vault-list li { font-size: 23px; color: #CBD5E1; line-height: 1.45; white-space: nowrap; }
  .vault-list li b { color: #F1F5F9; }
  .vault-pro {
    margin-top: 24px; padding-top: 20px; border-top: 1px solid rgba(56, 189, 248, 0.24);
    font-size: 23.5px; font-weight: 800; color: #FBBF24; white-space: nowrap;
  }

  .tier-card {
    background: #0D1422; border: 2px solid #F59E0B; border-radius: 22px;
    padding: 34px 42px; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
  }
  .tier-hd { font-size: 30px; font-weight: 800; color: #F59E0B; margin-bottom: 22px; white-space: nowrap; }
  .tier-rows { display: flex; flex-direction: column; gap: 17px; }
  .tier-row { font-size: 21px; color: #E2E8F0; line-height: 1.42; display: flex; align-items: center; gap: 12px; white-space: nowrap; }
  .price-pill {
    display: inline-block; font-weight: 900; padding: 3px 10px; border-radius: 7px; font-size: 20px; flex-shrink: 0; min-width: 172px; text-align: center;
  }
  .p-amber { background: rgba(245,158,11,0.18); color: #FCD34D; border: 1px solid rgba(245,158,11,0.45); }
  .p-blue { background: rgba(56,189,248,0.16); color: #7DD3FC; border: 1px solid rgba(56,189,248,0.45); }
  .p-green { background: rgba(16,185,129,0.18); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.45); }
  .tier-note { font-size: 20.5px; color: #94A3B8; margin-top: 4px; white-space: nowrap; }
</style>
</head>
<body>
  <div class="canvas">
    <div>
      <div class="hdr-title">配套 Chrome/Edge 本地自动防丢插件 (MV3)</div>
      <div class="hdr-sub">等账号被封再装导出插件已经进不去网页了！平时自动落盘本地硬盘才稳</div>
    </div>

    <div class="vault-card">
      <div class="vault-hd">Claude Guard 浏览器防丢保险箱 (100% 本地零云端上传)</div>
      <ul class="vault-list">
        <li>· <b>实时环境预警灯</b>：检测到 Asia/Shanghai 时区暴露或机房 ASN 立即提醒</li>
        <li>· <b>免费导出权益</b>：单篇对话 + 代码块一键导出 Markdown，20 场内保险箱免费</li>
        <li>· <b>AES 本地防丢库</b>：边聊边存本地硬盘，换号一键生成「1 秒恢复上下文包」</li>
      </ul>
      <div class="vault-pro">★ 离线永久买断：¥15 单品激活码 ｜ ¥39 全站工具通票 (Ed25519 秒解锁)</div>
    </div>

    <div class="tier-card">
      <div class="tier-hd">全站统一梯度清单与售前说明（拍前必看 · 零套路）</div>
      <div class="tier-rows">
        <div class="tier-row">
          <span class="price-pill p-amber">1. ¥9.9 自救包</span>
          <span>自动发 2026 双版排障 PDF + <b>cc-switch v2.0 无损脚本</b> + 体检器</span>
        </div>
        <div class="tier-row">
          <span class="price-pill p-blue">2. ¥39 全站通票</span>
          <span>离线永久解锁无限容量保险箱 + OPC 全站 16 款效率工具 (单品 ¥15)</span>
        </div>
        <div class="tier-row">
          <span class="price-pill p-green">3. ¥168 远程代配</span>
          <span>工程师 1对1 部署 <b>AWS Bedrock / Vertex 企业云零封号通道</b> (不通全退)</span>
        </div>
        <div class="tier-note">4. 合规边界：纯本地开源研发辅助脚本与正规云 IAM 架构指导，不含违规账号或节点</div>
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
    display: inline-block; border: 1.5px solid #F59E0B; background: rgba(245,158,11,0.12);
    color: #FCD34D; font-size: 20px; font-weight: 800; padding: 6px 20px; border-radius: 99px;
  }}
  .ver-tag {{
    background: #1E293B; border: 1px solid #334155; color: #38BDF8;
    font-size: 18px; font-weight: 800; padding: 6px 16px; border-radius: 99px;
  }}
  .main-title {{ font-size: 38px; font-weight: 900; color: #FFFFFF; margin-top: 10px; letter-spacing: 0.3px; white-space: nowrap; }}
  .main-title span {{ color: #FBBF24; }}
  .sub-title {{ font-size: 21px; color: #94A3B8; margin-top: 6px; font-weight: 600; white-space: nowrap; }}

  /* 中部双内页高清微距实拍窗 */
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
  .shot-lbl {{ font-size: 18px; font-weight: 800; color: #FDE68A; white-space: nowrap; }}
  .shot-card.right .shot-lbl {{ color: #7DD3FC; }}
  .shot-tag {{
    font-size: 13.5px; font-weight: 800; padding: 3px 9px; border-radius: 6px; white-space: nowrap; flex-shrink: 0;
    background: rgba(16,185,129,0.2); color: #6EE7B7; border: 1px solid rgba(16,185,129,0.4);
  }}
  .paper-viewport {{
    width: 100%; height: 500px; border-radius: 10px; overflow: hidden;
    background: #FFFFFF; border: 1px solid #334155; position: relative;
  }}
  /* 微距聚焦 PDF 核心图表版面，字迹清晰锐利 */
  .paper-viewport img.p3 {{
    width: 108%; margin-left: -4%; margin-top: -18px; display: block;
  }}
  .paper-viewport img.p15 {{
    width: 104%; margin-left: -2%; margin-top: -12px; display: block;
  }}
  .shot-caption {{
    margin-top: 9px; font-size: 16.5px; color: #CBD5E1; line-height: 1.38; font-weight: 600; white-space: nowrap;
  }}

  /* 下部非破坏性脚本硬核对比卡 */
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

  /* 底部统一定价横幅 */
  .bottom-strip {{
    background: linear-gradient(90deg, #0F172A 0%, #172554 50%, #0F172A 100%);
    border: 1.5px solid #F59E0B; border-radius: 14px; padding: 14px 22px;
    display: flex; justify-content: space-between; align-items: center;
    font-size: 20px; font-weight: 800; color: #F8FAFC;
  }}
  .bottom-strip span.hl-amber {{ color: #FBBF24; }}
  .bottom-strip span.hl-blue {{ color: #7DD3FC; }}
  .bottom-strip span.hl-green {{ color: #6EE7B7; }}
  .sep {{ color: #475569; }}
</style>
</head>
<body>
  <div class="canvas">
    <div>
      <div class="top-bar">
        <span class="kicker-pill">🔥 拒绝廉价拼凑 AI 水文 · 掘金销冠级精排版内页实拍</span>
        <span class="ver-tag">2026 v2.0 工程实测版</span>
      </div>
      <div class="main-title">内页微距实拍：<span>彩色排障决策树 + 一页纸贴屏速查卡</span></div>
      <div class="sub-title">买即发：双版本高清矢量 PDF + 标准 EPUB + v2.0 五源无损切换源码包</div>
    </div>

    <div class="pages-grid">
      <div class="shot-card">
        <div class="shot-bar">
          <span class="shot-lbl">📊 P.03 实拍 · 10秒报错排障决策树</span>
          <span class="shot-tag">高清矢量无损放大</span>
        </div>
        <div class="paper-viewport">
          <img class="p3" src="{p3_uri}" alt="PDF Page 3 Decision Tree Real Render" />
        </div>
        <div class="shot-caption">三大分支秒判「30%环境变量假封号 / ASN风控止损 / 企业云零断流」</div>
      </div>

      <div class="shot-card right">
        <div class="shot-bar">
          <span class="shot-lbl">🗂️ 书末实拍 · 一页纸贴屏速查卡</span>
          <span class="shot-tag">双栏高密壁纸</span>
        </div>
        <div class="paper-viewport">
          <img class="p15" src="{p15_uri}" alt="PDF Page 15 1-Page Dev Cheat Sheet Real Render" />
        </div>
        <div class="shot-caption">四级凭据金字塔 + 五源参数速查表 + 四清铁律 + 体检命令</div>
      </div>
    </div>

    <div class="diff-box">
      <div class="diff-bad">
        <div class="diff-hd">❌ 闲鱼几块钱旧脚本 (cat &gt; settings.json)</div>
        <div class="diff-txt">粗暴全量覆盖配置文件，切一次源直接把辛苦配好的 <code>mcpServers</code> 与 <code>hooks</code> 清空归零！</div>
      </div>
      <div class="diff-good">
        <div class="diff-hd">✅ 本套 cc-switch v2.0 非破坏性深合并</div>
        <div class="diff-txt">Node/Python 双引擎解析 JSON 语法树，仅更新 <code>env</code> 路由键，<b>100% 无损保留原有 MCP 与钩子</b>！</div>
      </div>
    </div>

    <div class="bottom-strip">
      <span class="hl-amber">¥9.9 手册+无损脚本包</span>
      <span class="sep">｜</span>
      <span class="hl-blue">¥39 在线全站通票</span>
      <span class="sep">｜</span>
      <span class="hl-green">¥168 企业云 Bedrock/Vertex 1对1代部署</span>
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

        # 1. Rebuild release/xianyu-03-plugin.png (unified pricing, 0 ¥49 conflict)
        xy03_out = RELEASE_DIR / "xianyu-03-plugin.png"
        render_html_to_1080_png(build_xianyu_03_html(), xy03_out, td_p, "xy03")
        print(f"[PASS] Updated {xy03_out} ({xy03_out.stat().st_size // 1024} KB)")

        # 2. Build release/xianyu-04-interior-showcase.png & sync to cashflow-service-pack/
        xy04_out = RELEASE_DIR / "xianyu-04-interior-showcase.png"
        xy04_service_out = SERVICE_PACK_DIR / "xianyu-04-interior-showcase.png"
        render_html_to_1080_png(
            build_xianyu_04_showcase_html(p3_png.as_uri(), p15_png.as_uri()),
            xy04_out,
            td_p,
            "xy04",
        )
        shutil.copy2(xy04_out, xy04_service_out)
        print(f"[PASS] Built {xy04_out} ({xy04_out.stat().st_size // 1024} KB) & synced to {xy04_service_out}")


if __name__ == "__main__":
    main()
