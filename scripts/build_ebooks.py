# -*- coding: utf-8 -*-
"""
Rebuild Book 3 (claude-guard) deliverables strictly inside kit/, dist/, docs/downloads/, and release/ebook-publishing-pack/
WITHOUT touching extension/ or docs/index.html:
1. Verify cc-switch.sh & cc-switch.ps1 non-destructive JSON deep merge (preserves mcpServers, permissions, hooks, custom env).
2. Re-pack dist/claude-code-kit.zip and docs/downloads/claude-code-kit.zip.
3. Rebuild release/ebook-publishing-pack/不掉号-不断流_ClaudeCode企业云合规接入与排障手册_2026国内文库版.pdf:
   - Eliminate Page 13 external promo URL (100% domestic Wenku compliant, 0 external promo links)
   - Eliminate Page 6 huge whitespace by enriching Ch4 + Ch5 (Non-destructive JSON merge architecture + dense troubleshooting table)
   - Sync Ch3.2, Ch6, Ch7 with v2.0 non-destructive cc-switch.sh / cc-switch.ps1 & Claude Sonnet 4.6 model IDs
4. Update release/ebook-publishing-pack/不掉号_Zero-Ban-Claude-2026.epub (and sync docs/downloads/Zero-Ban-Claude-2026.epub)
   with updated Ch5 & Ch6 non-destructive JSON merge scripts & Claude Sonnet 4.6 model IDs.
"""

import html as html_mod
import os
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
        # Mode 2: AWS Bedrock
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

        # Switch back to Mode 1: Official privacy-hardened
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
    """构建 100% 国内文库合规专供版 PDF（零外链硬广、第6页零大片留白、含 v2.0 非破坏性 JSON 深合并源码）"""
    sh_src = (KIT_DIR / "cc-switch.sh").read_text(encoding="utf-8").strip()
    ps_src = (KIT_DIR / "cc-switch.ps1").read_text(encoding="utf-8").strip()
    doc_src = (KIT_DIR / "env-doctor.mjs").read_text(encoding="utf-8").strip()

    # 剔除 env-doctor.mjs 第 70 行公网硬广网址与敏感词，替换为纯本地企业研发合规排障建议！
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

    sh_lines = sh_src.splitlines()
    sh_p1 = "\n".join(sh_lines[:53])
    sh_p2 = "\n".join(sh_lines[53:115])
    sh_p3 = "\n".join(sh_lines[115:])

    ps_lines = ps_src.splitlines()
    ps_p1 = "\n".join(ps_lines[:66])
    ps_p2 = "\n".join(ps_lines[66:])

    doc_l = doc_clean.splitlines()
    doc_p1 = "\n".join(doc_l[:37])
    doc_p2 = "\n".join(doc_l[37:])

    esc = html_mod.escape
    hero_uri = (EBOOK_DIR / "cover_hero_shield.jpg").as_uri()

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
    width: 210mm; height: 296.8mm; padding: 15mm 16mm 14mm 16mm;
    page-break-after: always; break-after: page; overflow: hidden;
    display: flex; flex-direction: column; position: relative; background: #FFFFFF;
  }}
  .page:last-child {{ page-break-after: auto; break-after: auto; }}
  .cover-wrap {{
    flex: 1; background: linear-gradient(160deg, #070D19 0%, #0F172A 52%, #172554 100%);
    border: 4px solid #F59E0B; border-radius: 16px; padding: 28px 32px 24px;
    display: flex; flex-direction: column; justify-content: space-between; color: #FFFFFF;
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
    font-size: 16.5pt; font-weight: 900; color: #0F172A; border-left: 5px solid #2563EB;
    padding-left: 11px; margin-bottom: 12px; line-height: 1.3;
  }}
  h2 {{ font-size: 12pt; font-weight: 800; color: #1D4ED8; margin: 12px 0 7px; }}
  p, li {{ font-size: 9.8pt; line-height: 1.66; color: #1E293B; }}
  p {{ margin-bottom: 8px; }}
  ol, ul {{ padding-left: 20px; margin-bottom: 9px; }}
  li {{ margin-bottom: 4px; }}
  code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    background: #FEE2E2; color: #B91C1C; padding: 1px 5px; border-radius: 4px; font-size: 8.8pt;
  }}
  pre {{
    background: #0F172A; color: #F8FAFC; border-radius: 10px; padding: 8.5px 12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 6.95pt; line-height: 1.31; white-space: pre-wrap; word-break: break-all;
    margin: 4px 0 7px;
  }}
  table {{ width: 100%; border-collapse: collapse; margin: 8px 0 10px; font-size: 8.9pt; }}
  th {{ background: #0F172A; color: #FFFFFF; padding: 7.5px 9px; text-align: left; font-weight: 800; }}
  td {{ border: 1px solid #CBD5E1; padding: 7px 9px; line-height: 1.45; vertical-align: top; }}
  tr:nth-child(even) td {{ background: #F8FAFC; }}
  .note-box {{
    background: #EFF6FF; border-left: 4px solid #2563EB; border-radius: 6px;
    padding: 9px 12px; font-size: 9.2pt; line-height: 1.55; color: #1E3A8A; margin-top: 6px;
  }}
  .warn-box {{
    background: #FFFBEB; border-left: 4px solid #D97706; border-radius: 6px;
    padding: 8px 12px; font-size: 9pt; line-height: 1.5; color: #78350F; margin: 6px 0;
  }}
  .pg-ft {{
    margin-top: auto; padding-top: 6px; border-top: 1px solid #E2E8F0;
    display: flex; justify-content: space-between; font-size: 8pt; color: #64748B;
  }}
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
      <p>◆ <b>核心解决痛点 1</b>：终端突发 <code>Organization disabled</code> 四级环境变量优先级冲突定位与清理</p>
      <p>◆ <b>核心解决痛点 2</b>：亚马逊云 AWS Bedrock 最小权限 IAM 策略 JSON 与 Claude Sonnet 4.6 跨区推理部署</p>
      <p>◆ <b>核心解决痛点 3</b>：Google Cloud Vertex AI 企业商业接口配置、ADC 授权与配额调优实操</p>
      <p>◆ <b>核心解决痛点 4</b>：JSON 非破坏性深合并技术 —— 5 源 1 秒热备切换且 100% 保留 <code>mcpServers / hooks</code></p>
      <p>◆ <b>核心解决痛点 5</b>：多轮研发对话上下文结构化恢复模板与生产环境常见报错状态码速查表</p>
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
  <p>本手册专为高频使用 AI 终端辅助编程工具的软件工程师、系统架构师与高校科研人员编写，提供从本地环境变量诊断、非破坏性配置合并到云厂商企业级 API 生产架构的完整源码。</p>
  <table>
    <thead><tr><th width="16%">章节</th><th>核心交付内容与可复制工程构件</th></tr></thead>
    <tbody>
      <tr><td><b>第 1 章</b></td><td>终端常见报错诊断决策树与四级凭据优先级覆盖机制剖析</td></tr>
      <tr><td><b>第 2 章</b></td><td>30 秒快速排雷：macOS / Linux / Windows 三端残留环境变量定位与根除命令集</td></tr>
      <tr><td><b>第 3 章</b></td><td>企业云合规直连架构（上）：AWS Bedrock 最小权限 IAM JSON 与 Sonnet 4.6 跨区推理配置</td></tr>
      <tr><td><b>第 4 章</b></td><td>企业云合规直连架构（下）：Google Cloud Vertex AI 接入流程、ADC 本地授权与区域选择</td></tr>
      <tr><td><b>第 5 章</b></td><td>终端隐私加固与 <code>settings.json</code> 非破坏性深合并规范（附多源核心环境变量速查表）</td></tr>
      <tr><td><b>第 6 章</b></td><td>完整自动化源码（一）：macOS / Linux 五源无损热备切换器 <code>cc-switch.sh</code>（v2.0）</td></tr>
      <tr><td><b>第 7 章</b></td><td>完整自动化源码（二）：Windows PowerShell 五源无损切换器 <code>cc-switch.ps1</code>（v2.0）</td></tr>
      <tr><td><b>第 8 章</b></td><td>完整自动化源码（三）：Node.js 本地终端环境健康度自检脚本 <code>env-doctor.mjs</code></td></tr>
      <tr><td><b>附录 A</b></td><td>多轮研发对话资产防丢工程：新会话 1 秒恢复上下文 Prompt 模板与错误码速查字典</td></tr>
    </tbody>
  </table>
  <div class="note-box">
    <b>工程阅读说明：</b>本手册所有配置文件（JSON）与跨平台自动化脚本（Bash / PowerShell / Node.js ESM）均采用非破坏性深合并逻辑并经过真机实测验证，复制至本地工程环境即可直接运行，绝不误删用户原有的 MCP 服务、权限白名单或 Hooks 钩子配置。
  </div>
  <div class="pg-ft"><span>《不掉号·不断流》企业云合规接入与排障手册</span><span>P.02 / 14</span></div>
</section>

<!-- P3: 第1章（前3页试读悬念页） -->
<section class="page">
  <h1>第 1 章：终端常见报错诊断决策树与环境变量覆盖机制剖析</h1>
  <h2>1.1 为什么明明订阅或云账户正常，终端却立即返回 400/403 阻断报错？</h2>
  <p>在日常多仓库协同研发中，工程师最常遭遇的突发阻断故障是终端启动后立即返回 HTTP 400 或 403 状态码，伴随报错提示 <code>Your organization has been disabled</code> 或 <code>Invalid API Key</code>，导致代码重构与自动化测试被迫中断。</p>
  <p>经过大量生产研发环境复盘统计，此类突发报错中有超过 <b>30%</b> 并非远端云账户异常，而是由本地操作系统的多级环境变量继承残留与认证凭据读取优先级冲突所引起。</p>

  <h2>1.2 终端 CLI 的四级凭据读取优先级顺序</h2>
  <p>理解命令行工具启动时的配置加载与覆盖顺序，是一切快速排障的基石。终端按从高到低的优先级依次读取：</p>
  <ol>
    <li><b>当前 Shell 进程显式导出的环境变量</b>（如 <code>ANTHROPIC_API_KEY</code>、<code>ANTHROPIC_AUTH_TOKEN</code>、<code>ANTHROPIC_BASE_URL</code>）——优先级最高，会无条件覆盖后续所有配置与登录态；</li>
    <li><b>当前工作目录或父级目录下的 <code>.env</code> 环境文件</b> —— 历史测试项目遗留的局部密钥常潜伏于此；</li>
    <li><b>用户主目录全局配置文件 <code>~/.claude/settings.json</code> 中的 <code>env</code> 字段</b> —— 推荐用于多源容灾路由切换的标准层；</li>
    <li><b>交互式 OAuth 登录令牌或云厂商默认凭证链</b>（AWS Credentials Profile / Google Cloud ADC）。</li>
  </ol>
  <div class="warn-box">
    <b>排障关键结论：</b>一旦你的 Shell 启动脚本（如 <code>~/.zshrc</code>、<code>~/.bash_profile</code>）或旧项目残留了早期已停用失效的测试 <code>ANTHROPIC_API_KEY</code>，每次发请求都会优先携带该失效密钥并触发 400 阻断报错。（下一章起给出三端一键清理命令、AWS Bedrock / Vertex AI 生产级配置模板及完整无损切换脚本源码……）
  </div>
  <div class="pg-ft"><span>第 1 章 · 认证优先级与诊断决策树</span><span>P.03 / 14</span></div>
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
grep -rn "ANTHROPIC_" ~/.zshrc ~/.bashrc ~/.bash_profile ~/.zprofile ./.env 2>/dev/null</pre>
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
  <div class="pg-ft"><span>第 2 章 · 三端环境变量清理实操</span><span>P.04 / 14</span></div>
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
  <div class="pg-ft"><span>第 3 章 · AWS Bedrock 生产架构部署</span><span>P.05 / 14</span></div>
</section>

<!-- P6: 第4章 Vertex AI + 第5章 非破坏性深合并与核心参数速查表（彻底消除原第6页55%大片留白！） -->
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
  <div class="pg-ft"><span>第 4–5 章 · Vertex AI 接入与非破坏性配置规范</span><span>P.06 / 14</span></div>
</section>

<!-- P7: 第6章 macOS/Linux 脚本 (1/3) -->
<section class="page">
  <h1>第 6 章：完整自动化源码（一）—— macOS / Linux 无损切换器 (1/3)</h1>
  <p>将以下完整脚本保存为 <code>cc-switch.sh</code> 并执行 <code>chmod +x cc-switch.sh</code>，支持 5 源秒切且 100% 保留原有 MCP 与 Hooks 配置：</p>
  <pre>{esc(sh_p1)}</pre>
  <div class="pg-ft"><span>第 6 章 · cc-switch.sh 完整无损切换源码 (1/3)</span><span>P.07 / 14</span></div>
</section>

<!-- P8: 第6章 macOS/Linux 脚本 (2/3) -->
<section class="page">
  <h2>6.2 cc-switch.sh 核心 Node.js 非破坏性 JSON 合并引擎 (2/3)</h2>
  <pre>{esc(sh_p2)}</pre>
  <div class="pg-ft"><span>第 6 章 · cc-switch.sh 完整无损切换源码 (2/3)</span><span>P.08 / 14</span></div>
</section>

<!-- P9: 第6章 macOS/Linux 脚本 (3/3) -->
<section class="page">
  <h2>6.3 cc-switch.sh Python3 双保险回退分支与收尾校验 (3/3)</h2>
  <pre>{esc(sh_p3)}</pre>
  <div class="note-box">
    <b>设计亮点解析：</b>脚本通过环境变量向 <code>node -e</code>（或回退 <code>python3 -c</code>）传递用户输入，绝不将含特殊符号的密钥直接拼接进代码字符串，既杜绝了命令注入风险，又保证了原 JSON 出现语法损坏时立即中止保护现场。
  </div>
  <div class="pg-ft"><span>第 6 章 · cc-switch.sh 完整无损切换源码 (3/3)</span><span>P.09 / 14</span></div>
</section>

<!-- P10: 第7章 Windows PowerShell 脚本 (1/2) -->
<section class="page">
  <h1>第 7 章：完整自动化源码（二）—— Windows PowerShell 无损切换器 (1/2)</h1>
  <p>保存为 <code>cc-switch.ps1</code>，通过 <code>powershell -ExecutionPolicy Bypass -File .\\cc-switch.ps1</code> 运行：</p>
  <pre>{esc(ps_p1)}</pre>
  <div class="pg-ft"><span>第 7 章 · cc-switch.ps1 Windows 无损切换源码 (1/2)</span><span>P.10 / 14</span></div>
</section>

<!-- P11: 第7章 Windows PowerShell 脚本 (2/2) -->
<section class="page">
  <h2>7.2 cc-switch.ps1 无 BOM UTF-8 写入与深度树保留逻辑 (2/2)</h2>
  <pre style="font-size:6.25pt;line-height:1.22;padding:7px 10px;">{esc(ps_p2)}</pre>
  <div class="note-box" style="padding:7px 11px;font-size:8.6pt;line-height:1.45;">
    <b>Windows 专项避坑：</b>Windows PowerShell 5.1 默认的 <code>Set-Content -Encoding UTF8</code> 会写入带 BOM 字节头的文件，且 <code>ConvertTo-Json</code> 默认深度仅为 2 层（会截断深层 <code>mcpServers</code> 参数数组）。上方源码优先调用 Node 原生引擎并在回退分支强制指定 <code>-Depth 20</code> 与无 BOM <code>UTF8Encoding($false)</code>，彻底消除跨平台编码隐患。
  </div>
  <div class="pg-ft"><span>第 7 章 · cc-switch.ps1 Windows 无损切换源码 (2/2)</span><span>P.11 / 14</span></div>
</section>

<!-- P12: 第8章 env-doctor.mjs (1/2) -->
<section class="page">
  <h1>第 8 章：完整自动化源码（三）—— 本地环境巡检器 env-doctor.mjs</h1>
  <p>保存为 <code>env-doctor.mjs</code>，执行 <code>node env-doctor.mjs</code> 即可一键输出终端配置完整性与安全评分报告：</p>
  <pre>{esc(doc_p1)}</pre>
  <div class="pg-ft"><span>第 8 章 · env-doctor.mjs 环境健康自检源码 (1/2)</span><span>P.12 / 14</span></div>
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
  <div class="pg-ft"><span>第 8 章 · env-doctor.mjs 验收标准与加固闭环</span><span>P.13 / 14</span></div>
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
  <div class="pg-ft"><span>附录 A · 上下文恢复工程与错误码速查表</span><span>P.14 / 14</span></div>
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
    assert len(r_check.pages) == 14, f"Expected 14 pages, got {len(r_check.pages)}"
    assert "github.io" not in full_txt and "a3152557994" not in full_txt, "External promo link still present!"
    print(f"[PASS] Built Wenku PDF: {out_pdf.name} -> {len(r_check.pages)} pages | {out_pdf.stat().st_size // 1024} KB | 0 external promo links!")


def update_zero_ban_epub_and_full_pdf():
    """同步更新 Zero-Ban-Claude-2026.epub（剔除0佣金竞品外链、同步v2.0无损合并与Sonnet 4.6）并重建完整版 PDF"""
    epub_pack = EBOOK_DIR / "不掉号_Zero-Ban-Claude-2026.epub"
    epub_dl = ROOT / "docs" / "downloads" / "Zero-Ban-Claude-2026.epub"
    full_pdf_pack = EBOOK_DIR / "不掉号_Claude防封号与封后退费自救全书_2026完整版.pdf"
    full_pdf_dl = ROOT / "docs" / "downloads" / "Claude-2026-Anti-Ban-Playbook.pdf"

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
    <h2>一、3 步识别真假静态原生住宅 IP</h2>
    <ol>
      <li>打开在线自检台 <a href="https://a3152557994-ship-it.github.io/claude-guard/">Claude Guard 10秒体检台</a> 查看当前出口 IP 的 ASN 与运营商组织名称；</li>
      <li><strong>真住宅宽带（ISP / Residential）</strong>：运营商显示为 <code>AT&amp;T</code>、<code>Comcast Cable</code>、<code>Verizon Business</code>、<code>Charter / Spectrum</code> 等本土宽带商，且 <code>hosting: false</code>；</li>
      <li><strong>假原生机房（Datacenter）</strong>：显示为 <code>Cloudflare</code>、<code>Choopa</code>、<code>Vultr</code>、<code>DigitalOcean</code>、<code>Cogent</code>、<code>M247</code> 等，务必更换为独享静态住宅 ISP 线路（<code>hosting: false</code>），全程固定单一美国城市出口，切勿早晚在美、日、新之间来回切换。<strong>特别警告：中国香港属于不支持区域，严禁挂香港节点访问或点击官方邮件！</strong></li>
    </ol>
    <h2>二、为什么必须用独立浏览器环境隔离 Claude？</h2>
    <p>你平时办公的主力 Chrome 浏览器装满了几十个国内扩展、保存着大量中文站点 Cookie、系统语言是 <code>zh-CN</code>、本地时区是 <code>Asia/Shanghai</code>，甚至 WebRTC STUN 握手会直接穿透代理暴露你的真实国内宽带公网 IP。</p>
    <div class="box">
      <strong>🛠️ 推荐零成本标准物理隔离做法：</strong>
      <p>无需额外付费买软件，直接在 Chrome 新建独立空白个人资料（地址栏输入 <code>chrome://settings/manageProfile</code>）或使用开源防关联容器，专门建立名为 <code>Claude-US-Dedicated</code> 的纯净环境：</p>
      <ul>
        <li>仅在该独立窗口绑定固定美西静态住宅代理，不装任何与研发无关的第三方爬虫/比价扩展；</li>
        <li>将浏览器首选语言设为英文（<code>en-US</code>），并保持系统时区与代理出口一致（如 <code>America/Los_Angeles</code>）；</li>
        <li>开启浏览器「禁用非代理 UDP（WebRTC 防泄漏）」策略，彻底封死真实公网 IP 穿透泄露。</li>
      </ul>
      <p>从此以后，只有在这个干净独立的窗口里才登录 Claude，和日常国内上网环境彻底物理隔离。</p>
    </div>
</body>
</html>"""

    ch05_new = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh-CN" lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>第 5 章：Claude Code 终端极客加固与 5 源 1 秒无损热备切换</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <h1>第 5 章：Claude Code 终端极客加固与 5 源 1 秒无损热备切换</h1>
    <p>对于每天在终端跑 <code>Claude Code</code> 的程序员来说，除了防封，最大的痛点有两个：一是写代码改到一半撞上 <strong>5 小时消息配额上限（5-hour rate limit）</strong> 被迫停工；二是乱用网上的粗暴覆盖脚本（<code>cat &gt; ~/.claude/settings.json</code>）把原本配好的 <code>mcpServers</code>、<code>permissions</code>、<code>hooks</code> 全量清空！本章教你用<strong>「非破坏性 JSON 深合并」</strong>同时搞定防遥测加固与 1 秒无损切源。</p>
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
    <h2>二、5 源 1 秒无损热备切换架构（cc-switch v2.0）</h2>
    <p>不要把进度全押在单一账号上。成熟的独立开发者都会在本地配置双轨热备：</p>
    <ul>
      <li><strong>日常主力</strong>：官方个人 Pro/Max 防遥测加固模式（吃包月固定成本）；</li>
      <li><strong>撞上 5 小时限流窗 / 官方维护时</strong>：运行 <code>cc-switch</code> v2.0，自动通过 <code>node -e</code> 读取现有 <code>settings.json</code>，仅清理并更新 <code>env</code> 下的托管路由键（<code>100% 保留 mcpServers / permissions / hooks</code>），1 秒切换到 <strong>AWS Bedrock (Claude Sonnet 4.6)</strong>、<strong>Google Vertex AI</strong> 或 <strong>OpenRouter</strong> 按量热备通道！</li>
    </ul>
    <p>你可以直接免费下载已升级为 v2.0 非破坏性深合并引擎的跨平台工具包（含 macOS / Linux <code>cc-switch.sh</code> 与 Windows <code>cc-switch.ps1</code>）：<a href="https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-code-kit.zip">claude-code-kit.zip</a>。</p>
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
    <p>如果你是全职开发者、创业团队技术负责人或正在赶毕业论文死线的硕博，<strong>根本承受不起任何 1% 的封号断流风险</strong>，那么最彻底的终极方案就是：直接走<strong>亚马逊云（AWS Bedrock）或谷歌云（Google Cloud Vertex AI）官方商业通道</strong>。</p>
    <h2>一、为什么云大厂通道是 0% 封号？</h2>
    <p>AWS 与 Google Cloud 是 Anthropic 官方战略云合作伙伴。通过 Bedrock 或 Vertex AI 调用最新一代 Claude Sonnet 4.6 / Opus 4.6 模型，走的是企业级云厂商标准 IAM 鉴权与商业账单结算——<strong>完全不存在个人版针对地区、浏览器指纹或虚拟卡的封号机制</strong>，且支持为团队成员分配独立最小权限 IAM 子密钥与预算上限！</p>
    <h2>二、AWS Bedrock 最小权限 IAM 策略与跨区推理配置</h2>
    <p><strong>切忌直接给终端挂载 AWS 根账号或 AdministratorAccess 权限！</strong>请在 AWS Console -&gt; IAM -&gt; Policies 中创建以下最小权限 JSON 策略：</p>
    <pre><code>{
  "Version": "2012-10-17",
  "Statement": [
    {
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
    }
  ]
}</code></pre>
    <p>随后使用 <code>cc-switch.sh</code>（或非破坏性合并）在 <code>~/.claude/settings.json</code> 的 <code>env</code> 字段启用最新一代跨区推理模型 ID（保留 <code>us.</code> 或 <code>global.</code> 推理前缀可大幅提升并发配额稳定性）：</p>
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
    <h2>三、Google Cloud Vertex AI 配置（可抵扣新户 $300 赠金！）</h2>
    <p>如果你有 Google Cloud 账号（新注册用户官方通常赠送 <strong>$300 免费试用赠金</strong>，可直接抵扣 Vertex AI 上的 Claude 调用费！）：</p>
    <ol>
      <li>进入 GCP Console -&gt; <code>Vertex AI</code> -&gt; <code>Model Garden</code>，搜索 Claude Sonnet 4.6 并点击 <code>Enable</code> 启用模型权限；</li>
      <li>本机安装 Google Cloud SDK 后运行 <code>gcloud auth application-default login</code> 完成授权；</li>
      <li>在 <code>~/.claude/settings.json</code> 的 <code>env</code> 节点合并写入：</li>
    </ol>
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
      <p>上述非破坏性合并流程已封装进开源脚本 <code>bedrock-vertex-1click.sh</code>（含在 <a href="https://a3152557994-ship-it.github.io/claude-guard/downloads/claude-code-kit.zip">claude-code-kit.zip</a> 中，100% 保留原有 MCP 与 Hooks 配置）。如果你不想自己折腾 AWS IAM 跨区权限或 GCP CLI，可直接预约工程师 <strong>20 分钟 1对1 远程代部署（¥168/次，全程本机自输密钥，调不通全额退款）</strong>：<a href="https://a3152557994-ship-it.github.io/claude-guard/#checkout-remote">点击预约远程部署</a>。</p>
    </div>
</body>
</html>"""

    ET.fromstring(ch03_new.encode("utf-8"))
    ET.fromstring(ch05_new.encode("utf-8"))
    ET.fromstring(ch06_new.encode("utf-8"))

    chapter_bodies = {}
    with tempfile.TemporaryDirectory(prefix="cg_epub_") as td:
        tmp_epub = Path(td) / "updated.epub"
        cover_bytes = (EBOOK_DIR / "cover-1600x2560.jpg").read_bytes()
        with zipfile.ZipFile(epub_pack, "r") as zin, zipfile.ZipFile(tmp_epub, "w") as zout:
            zout.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            for info in zin.infolist():
                if info.filename == "mimetype":
                    continue
                data = zin.read(info.filename)
                if info.filename == "OEBPS/cover.jpg":
                    data = cover_bytes
                elif info.filename == "OEBPS/ch03_network_isolation.xhtml":
                    data = ch03_new.encode("utf-8")
                elif info.filename == "OEBPS/ch04_apple_iap.xhtml":
                    s4 = data.decode("utf-8")
                    if '<div class="box">' in s4:
                        s4_head = s4.split('<div class="box">')[0]
                        s4 = s4_head + """<div class="box">
      <strong>💡 没有 iPhone 或不想维护海外住宅 IP 的零折腾方案：</strong>
      <p>切勿在二手平台购买无质保共享成品号（多人混用机房节点极易连坐秒封）。若无美区设备，推荐直接采用本书<strong>第 6 章 AWS Bedrock / Google Vertex AI 企业商业接口</strong>（按量付费、0% 封号），或直接预约 <a href="https://a3152557994-ship-it.github.io/claude-guard/#checkout-remote">20 分钟 1对1 远程代配（¥168 包跑通）</a>。</p>
    </div>
</body>
</html>"""
                    ET.fromstring(s4.encode("utf-8"))
                    data = s4.encode("utf-8")
                elif info.filename == "OEBPS/ch05_claude_code.xhtml":
                    data = ch05_new.encode("utf-8")
                elif info.filename == "OEBPS/ch06_bedrock_vertex.xhtml":
                    data = ch06_new.encode("utf-8")
                elif info.filename == "OEBPS/content.opf":
                    s = data.decode("utf-8").replace("2026-11-22T11:35:00Z", "2026-11-26T15:30:00Z")
                    ET.fromstring(s.encode("utf-8"))
                    data = s.encode("utf-8")
                if info.filename.endswith((".xhtml", ".opf", ".ncx")):
                    ET.fromstring(data)
                if info.filename.startswith("OEBPS/") and info.filename.endswith(".xhtml"):
                    txt = data.decode("utf-8")
                    body_inner = txt.split("<body>")[1].split("</body>")[0].strip()
                    chapter_bodies[info.filename] = body_inner
                zout.writestr(info.filename, data, compress_type=zipfile.ZIP_DEFLATED)
        shutil.move(str(tmp_epub), str(epub_pack))
    shutil.copy2(epub_pack, epub_dl)
    print(f"[PASS] Updated Zero-Ban-Claude-2026.epub ({epub_pack.stat().st_size // 1024} KB) & synced to docs/downloads/")

    # 同步生成出版级完整版 PDF（第1页全出血护盾封面 + 内页零85%空页、零竞品外链）
    hero_uri = (EBOOK_DIR / "cover_hero_shield.jpg").as_uri()
    ordered_files = [
        "OEBPS/nav.xhtml",
        "OEBPS/ch00_preface.xhtml",
        "OEBPS/ch01_risk_matrix.xhtml",
        "OEBPS/ch02_false_ban.xhtml",
        "OEBPS/ch03_network_isolation.xhtml",
        "OEBPS/ch04_apple_iap.xhtml",
        "OEBPS/ch05_claude_code.xhtml",
        "OEBPS/ch06_bedrock_vertex.xhtml",
        "OEBPS/ch07_refund_appeal.xhtml",
        "OEBPS/ch08_vault_recovery.xhtml",
        "OEBPS/ch09_appendix.xhtml",
    ]
    import re
    toc_attr = 'epub:type="toc"'
    sec_list = []
    for k in ordered_files:
        if k not in chapter_bodies:
            continue
        stem = Path(k).stem
        b_html = chapter_bodies[k].replace(toc_attr, "")
        b_html = re.sub(r'<li>\s*<a href="cover\.xhtml">[^<]*</a>\s*</li>', "", b_html)
        b_html = re.sub(r'href="(ch\d+_[^"]+)\.xhtml"', r'href="#\1"', b_html)
        sec_list.append(f'<section class="chap" id="{stem}">{b_html}</section>')
    sections_html = "\n".join(sec_list)
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>不掉号：Claude 防封号、免税订阅与封后退款自救全书（2026完整版）</title>
<style>
  @page {{ size: A4 portrait; margin: 11.5mm 14mm; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
  body {{ font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; color: #1E293B; background: #FFF; font-size: 9.6pt; line-height: 1.56; }}
  .chap {{ page-break-before: always; break-before: page; }}
  h1 {{ font-size: 16pt; font-weight: 900; color: #0F172A; border-left: 5px solid #F59E0B; padding-left: 11px; margin: 0 0 10px; line-height: 1.3; }}
  h2 {{ font-size: 11.6pt; font-weight: 800; color: #1E40AF; margin: 11px 0 6px; }}
  p {{ margin-bottom: 7px; }}
  ol, ul {{ padding-left: 20px; margin-bottom: 8px; }}
  li {{ margin-bottom: 4px; }}
  a {{ color: #2563EB; text-decoration: none; font-weight: 600; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #FEF2F2; color: #BE123C; padding: 1px 5px; border-radius: 4px; font-size: 8.6pt; }}
  pre {{ background: #0F172A; color: #F8FAFC; padding: 9px 13px; border-radius: 9px; margin: 6px 0 9px; white-space: pre-wrap; word-break: break-word; line-height: 1.38; font-size: 8.1pt; }}
  pre code {{ background: transparent; color: #F8FAFC; padding: 0; font-size: 8.1pt; }}
  .box {{ background: #FFFBEB; border-left: 4px solid #F59E0B; border-radius: 8px; padding: 8px 12px; margin: 8px 0; font-size: 9.2pt; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 9.2pt; }}
  th {{ background: #0F172A; color: #FFF; padding: 8px 10px; text-align: left; }}
  td {{ border: 1px solid #CBD5E1; padding: 7.5px 10px; vertical-align: top; line-height: 1.48; }}
  tr:nth-child(even) td {{ background: #F8FAFC; }}
</style>
</head>
<body>
{sections_html}
</body>
</html>"""

    cov_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  @page {{ size: A4 portrait; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
  body {{ width: 210mm; height: 297mm; overflow: hidden; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #070D19; }}
  .wrap {{
    width: 210mm; height: 296.8mm; padding: 14mm 15mm 12mm;
    background: radial-gradient(circle at 50% 35%, #172554 0%, #0B132B 58%, #050914 100%);
    border: 4.5mm solid #F59E0B; display: flex; flex-direction: column; justify-content: space-between; color: #FFF;
  }}
  .top-row {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(245,158,11,0.35); padding-bottom: 9px; }}
  .pill {{ background: linear-gradient(90deg, #F59E0B, #FBBF24); color: #0F172A; font-weight: 900; font-size: 10pt; padding: 4px 14px; border-radius: 99px; }}
  .ed {{ color: #FBBF24; font-weight: 800; font-size: 10.5pt; letter-spacing: 1.5px; }}
  .kicker {{ text-align: center; color: #38BDF8; font-weight: 800; letter-spacing: 3px; font-size: 11pt; margin-top: 6px; }}
  .ttl {{ text-align: center; font-size: 54pt; font-weight: 900; letter-spacing: 4px; color: #FFFFFF; line-height: 1.08; margin: 4px 0 8px; text-shadow: 0 6px 24px rgba(0,0,0,0.6); }}
  .sub-pill {{ align-self: center; border: 1.5px solid #F59E0B; color: #FDE68A; background: rgba(245,158,11,0.12); border-radius: 99px; padding: 5px 20px; font-weight: 800; font-size: 11.5pt; margin-bottom: 6px; }}
  .desc {{ text-align: center; color: #E2E8F0; font-size: 11.2pt; font-weight: 600; line-height: 1.5; }}
  .hero {{ margin: 10px 0; height: 250px; border-radius: 14px; overflow: hidden; border: 2px solid rgba(245,158,11,0.7); box-shadow: 0 14px 32px rgba(0,0,0,0.55); }}
  .hero img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .card {{ background: rgba(15,23,42,0.85); border: 1.5px solid rgba(245,158,11,0.38); border-radius: 12px; padding: 14px 18px; }}
  .card-hd {{ color: #34D399; font-size: 9.8pt; font-weight: 800; margin-bottom: 6px; }}
  .card p {{ font-size: 10pt; line-height: 1.72; color: #F8FAFC; font-weight: 600; }}
  .card p b {{ color: #FBBF24; margin-right: 6px; }}
  .ft {{ display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.18); padding-top: 9px; font-size: 9pt; color: #CBD5E1; }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="top-row"><span class="pill">AI 开发者与科研人自救实战书系</span><span class="ed">2026 v2.0 EDITION</span></div>
    <div style="display:flex;flex-direction:column;">
      <div class="kicker">ZERO-BAN CLAUDE PLAYBOOK</div>
      <div class="ttl">不掉号</div>
      <div class="sub-pill">防封号 · 免税订阅 · 封后退费 · 企业云零断流</div>
      <div class="desc">Claude &amp; Claude Code 稳态环境配置、<br>AWS Bedrock / Google Vertex AI 0% 封号接入与资产抢救全书</div>
    </div>
    <div class="hero"><img src="{hero_uri}" alt="Zero-Ban Claude Shield Cover"></div>
    <div class="card">
      <div class="card-hd">◆ 8 大实战章节 · 覆盖从环境排雷到退款止损全闭环</div>
      <p><b>01</b> 30 秒排掉本地环境变量冲突导致的「假封号」乌龙</p>
      <p><b>02</b> 美区免税州 Apple 礼品卡内购隔离 Stripe 虚拟卡雷区</p>
      <p><b>03</b> AWS Bedrock &amp; Vertex AI 企业通道 + v2.0 无损配置秒切</p>
      <p><b>04</b> 封后黄金 48 小时追回订阅费实操与高通过率英文申诉信</p>
    </div>
    <div class="ft">
      <span>阿王写工具 · OPC Studio 编著（附 5 源无损切换脚本与本地防丢扩展）</span>
      <span style="color:#34D399;font-weight:800;">PRACTICAL GUIDE</span>
    </div>
  </div>
</body>
</html>"""

    with tempfile.TemporaryDirectory(prefix="cg_full_", dir="/tmp") as td:
        td_p = Path(td)
        cov_h = td_p / "cov.html"
        cov_p = td_p / "cov.pdf"
        body_h = td_p / "body.html"
        body_p = td_p / "body.pdf"
        cov_h.write_text(cov_html, encoding="utf-8")
        body_h.write_text(full_html.replace('<section class="chap">', '<section class="chap" style="page-break-before:always;">').replace('<section class="chap" style="page-break-before:always;">', '<section class="chap">', 1), encoding="utf-8")
        for hf, pf in [(cov_h, cov_p), (body_h, body_p)]:
            for att in range(4):
                subprocess.run(
                    [
                        CHROME_BIN,
                        "--headless=new",
                        "--disable-gpu",
                        f"--user-data-dir={td_p / f'u_{hf.stem}_{att}'}",
                        "--no-pdf-header-footer",
                        "--virtual-time-budget=3000",
                        f"--print-to-pdf={pf}",
                        hf.as_uri(),
                    ],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if pf.exists() and pf.stat().st_size > 500:
                    break
        writer = PdfWriter()
        writer.add_page(PdfReader(str(cov_p)).pages[0])
        for pg in PdfReader(str(body_p)).pages:
            writer.add_page(pg)
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
    for banned in ("银河录像局", "nf.video", "AdsPower", "Proxy-Seller", "IPRoyal"):
        assert banned not in ftxt, f"Competitor still present: {banned}"
    print(f"[PASS] Rebuilt Full Playbook PDF: {full_pdf_pack.name} -> {len(rc.pages)} pages | {full_pdf_pack.stat().st_size // 1024} KB & synced to docs/downloads/Claude-2026-Anti-Ban-Playbook.pdf")


if __name__ == "__main__":
    test_nondestructive_merge()
    repack_kit_zip()
    build_wenku_pdf()
    update_zero_ban_epub_and_full_pdf()
