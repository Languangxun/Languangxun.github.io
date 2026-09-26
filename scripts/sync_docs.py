#!/usr/bin/env python3
"""一键同步本地项目文档与 stock-analyzer 回测报告，提交并推送。

- 项目文档：把本地项目 README/ARCHITECTURE 等镜像到 docs/（保留 front matter，
  自动脱敏：家目录路径、内网 IP、密码/密钥；相对图片复制到 assets/img/）
- 回测报告：读取 stock-analyzer GUI 最新导出 JSON，生成
  docs/stock-analyzer-backtest.md 与 assets/img/stock-analyzer-backtest-*.svg
- 最后 git add/commit/push（无变化则跳过）

用法：
  python3 scripts/sync_docs.py --dry-run   # 只预览，不改文件不提交
  python3 scripts/sync_docs.py             # 同步并推送
  python3 scripts/sync_docs.py --no-push   # 同步并本地提交，不推送
  python3 scripts/sync_docs.py --no-sources  # 只更新回测报告
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
DESKTOP = HOME / "桌面"
SITE = Path(__file__).resolve().parents[1]
DOCS = SITE / "docs"
ASSETS = SITE / "assets" / "img"
ANALYZER = DESKTOP / "stock_predict"
GUI_BACKTESTS = ANALYZER / "research" / "gui_backtests"

TODAY = dt.date.today().isoformat()
BACKTEST_PAGE = "stock-analyzer-backtest.md"
BACKTEST_PERMALINK = "/docs/stock-analyzer-backtest/"

SOURCES = [
    {
        "src": ANALYZER / "README.md",
        "dst": "stock-analyzer.md",
        "project": "stock-analyzer",
        "title": "stock-analyzer · A 股形态分析",
        "permalink": "/docs/stock-analyzer/",
        "origin": "[Languangxun/stock-analyzer](https://github.com/Languangxun/stock-analyzer)",
    },
    {
        "src": ANALYZER / "ARCHITECTURE.md",
        "dst": "stock-analyzer-architecture.md",
        "project": "stock-analyzer",
        "title": "stock-analyzer · 架构设计",
        "permalink": "/docs/stock-analyzer-architecture/",
        "origin": "[Languangxun/stock-analyzer](https://github.com/Languangxun/stock-analyzer)",
    },
    {
        "src": ANALYZER / "PLUGIN_API.md",
        "dst": "stock-analyzer-plugin-api.md",
        "project": "stock-analyzer",
        "title": "stock-analyzer · 插件 API",
        "permalink": "/docs/stock-analyzer-plugin-api/",
        "origin": "[Languangxun/stock-analyzer](https://github.com/Languangxun/stock-analyzer)",
    },
    {
        "src": DESKTOP / "ai-quant" / "README.md",
        "dst": "ai-quant.md",
        "project": "ai-quant",
        "title": "ai-quant · 量化研究与模拟交易",
        "permalink": "/docs/ai-quant/",
        "origin": "[Languangxun/ai-quant](https://github.com/Languangxun/ai-quant)",
    },
    {
        "src": DESKTOP / "oneos" / "README.md",
        "dst": "oneos.md",
        "project": "oneos",
        "title": "OneOS · 模拟操作系统",
        "permalink": "/docs/oneos/",
        "origin": "[Languangxun/oneos](https://github.com/Languangxun/oneos)",
    },
    {
        "src": DESKTOP / "oneos" / "docs" / "ARCHITECTURE.md",
        "dst": "oneos-architecture.md",
        "project": "oneos",
        "title": "OneOS · 架构设计",
        "permalink": "/docs/oneos-architecture/",
        "origin": "[Languangxun/oneos](https://github.com/Languangxun/oneos)",
    },
    {
        "src": DESKTOP / "oneos" / "docs" / "ROADMAP.md",
        "dst": "oneos-roadmap.md",
        "project": "oneos",
        "title": "OneOS · 路线图",
        "permalink": "/docs/oneos-roadmap/",
        "origin": "[Languangxun/oneos](https://github.com/Languangxun/oneos)",
    },
    {
        "src": DESKTOP / "oneos" / "docs" / "BOOT-ANIMATION.md",
        "dst": "oneos-boot-animation.md",
        "project": "oneos",
        "title": "OneOS · 开机动画",
        "permalink": "/docs/oneos-boot-animation/",
        "origin": "[Languangxun/oneos](https://github.com/Languangxun/oneos)",
    },
    {
        "src": DESKTOP / "stock_pi_mobile" / "README.md",
        "dst": "stock-pi-mobile.md",
        "project": "stock-pi-mobile",
        "title": "stock-pi-mobile · 触摸屏盯盘终端",
        "permalink": "/docs/stock-pi-mobile/",
        "origin": "本地项目（暂未单独开源）",
    },
]

FRONT_MATTER_RE = re.compile(r"\A---\n.*?\n---\n?", re.S)
H1_RE = re.compile(r"\A#\s+[^\n]*\n+")
BACKLINK_RE = re.compile(r"\A\[← 返回文档中心\][^\n]*\n+")
IMAGE_RE = re.compile(r"(!\[[^\]]*\]\()([^)\s]+)(\))")


def log(msg: str) -> None:
    print(msg, flush=True)


def split_front_matter(text: str) -> tuple[str, str]:
    m = FRONT_MATTER_RE.match(text)
    if m:
        return m.group(0), text[m.end():]
    return "", text


def make_front_matter(title: str, permalink: str) -> str:
    return f'---\nlayout: page\ntitle: "{title}"\npermalink: {permalink}\n---\n'


def backlink(origin: str) -> str:
    return f"[← 返回文档中心](/docs/) · 来源：{origin} · 同步于 {TODAY}\n"


def strip_backlink(body: str) -> str:
    return BACKLINK_RE.sub("", body.lstrip("\n"), count=1).strip("\n")


def sanitize(text: str) -> str:
    text = text.replace(str(DESKTOP) + "/", "~/").replace(str(HOME) + "/", "~/")
    text = re.sub(r"(?<![\w.])/home/[A-Za-z0-9_.\-]+/", "~/", text)
    text = re.sub(
        r"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))(?:\.\d{1,3}){2,3}\b",
        "<内网IP>",
        text,
    )
    text = re.sub(
        r"(?im)^([ \t]*(?:password|passwd|token|api[_-]?key|secret)[ \t]*[:=])[ \t]*\S+.*$",
        r"\1 ***",
        text,
    )
    text = re.sub(
        r"\b(?:sk|gho|ghp|ghu|ghs|ghr)_[A-Za-z0-9_\-]{16,}\b", "***", text
    )
    return text


def rewrite_images(text: str, src_file: Path, project: str, dry: bool) -> str:
    def repl(m: re.Match) -> str:
        url = m.group(2)
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url) or url.startswith(("/", "#")):
            return m.group(0)
        for base in (src_file.parent, src_file.parent.parent):
            cand = (base / url).resolve()
            if cand.is_file():
                target = ASSETS / f"{project}-{cand.name}"
                if not dry:
                    ASSETS.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(cand, target)
                return f"{m.group(1)}/assets/img/{target.name}{m.group(3)}"
        return m.group(0)

    return IMAGE_RE.sub(repl, text)


def build_source_doc(entry: dict, old_text: str, dry: bool) -> str | None:
    src: Path = entry["src"]
    if not src.is_file():
        log(f"  ! 跳过（源文件不存在）：{src}")
        return None
    raw = src.read_text(encoding="utf-8")
    body = H1_RE.sub("", raw, count=1)
    body = sanitize(body)
    body = rewrite_images(body, src, entry["project"], dry)
    front, old_body = split_front_matter(old_text)
    if not front:
        front = make_front_matter(entry["title"], entry["permalink"])
    if strip_backlink(old_body) == body.strip("\n"):
        return old_text
    return f"{front}\n{backlink(entry['origin'])}\n{body.strip()}\n"


def fmt_pct(v: float | None, digits: int = 1) -> str:
    if v is None:
        return "—"
    return f"{v * 100:+.{digits}f}%"


def fmt_num(v: float | None, digits: int = 2) -> str:
    if v is None:
        return "—"
    return f"{v:.{digits}f}"


def metrics_rows(seg: dict) -> list[tuple[str, str]]:
    return [
        ("交易次数", f"{seg['trades']}（已平仓 {seg['closed']}）"),
        ("胜率", f"{seg['winrate'] * 100:.1f}%（{seg['wins']}/{seg['closed']}）"),
        ("区间收益", fmt_pct(seg["total"])),
        ("年化收益", fmt_pct(seg["ann"])),
        ("最大回撤", fmt_pct(seg["mdd"])),
        ("盈亏比", fmt_num(seg["profit_loss"])),
        ("均盈 / 均亏", f"{fmt_pct(seg['avg_win'])} / {fmt_pct(seg['avg_loss'])}"),
        ("未平仓浮盈", fmt_pct(seg.get("floating"))),
    ]


def fwd_cell(fwd: dict, side: str, horizon: str) -> str:
    n, mean, up = fwd[side][horizon]
    return f"{fmt_pct(mean, 2)} · 上涨 {up * 100:.0f}%（n={n}）"


def build_backtest_svg(data: dict) -> str:
    dates: list[str] = data["curve_dates"]
    curve: list[float] = data["curve"]
    drawdown: list[float] = data["drawdown"]
    split_i: int = data.get("split_i", len(curve) // 2)
    n = len(curve)
    if n < 2:
        raise ValueError("净值曲线数据不足")

    width, height = 860, 470
    left, right, top = 58, 14, 16
    eq_top, eq_bottom = top + 14, 316
    dd_top, dd_bottom = 356, 424
    plot_w = width - left - right

    def x(i: int) -> float:
        return left + plot_w * i / (n - 1)

    lo, hi = min(curve), max(curve)
    pad = (hi - lo) * 0.08 or 0.05
    lo, hi = lo - pad, hi + pad

    def y(v: float) -> float:
        return eq_bottom - (v - lo) / (hi - lo) * (eq_bottom - eq_top)

    eq_pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(curve))

    dd_lo = min(drawdown + [0.0])
    dd_hi = 0.0
    dd_pad = (dd_hi - dd_lo) * 0.08 or 0.02
    dd_lo -= dd_pad

    def ydd(v: float) -> float:
        return dd_bottom - (v - dd_lo) / (dd_hi - dd_lo) * (dd_bottom - dd_top)

    dd_pts = " ".join(f"{x(i):.1f},{ydd(v):.1f}" for i, v in enumerate(drawdown))
    dd_area = f"{left},{ydd(0):.1f} {dd_pts} {x(n - 1):.1f},{ydd(0):.1f}"

    split_x = x(min(split_i, n - 1))
    mid = dates[split_i] if split_i < n else dates[-1]
    grid = "rgba(255,255,255,0.08)"
    axis = "rgba(255,255,255,0.22)"
    muted = "#8e8e93"
    text = "#a1a1a6"

    lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" '
            f'aria-label="净值与回撤曲线" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Noto Sans SC,sans-serif">'
        ),
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#0b0b0c"/>',
        f'<rect x="{split_x:.1f}" y="{eq_top}" width="{x(n - 1) - split_x:.1f}" '
        f'height="{dd_bottom - eq_top}" fill="rgba(255,255,255,0.035)"/>',
        f'<text x="{left}" y="{top}" fill="{text}" font-size="13">净值曲线（初始=1.00）</text>',
        f'<text x="{left}" y="{dd_top - 12}" fill="{text}" font-size="13">回撤</text>',
    ]

    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        v = lo + (hi - lo) * frac
        yy = y(v)
        lines.append(
            f'<line x1="{left}" y1="{yy:.1f}" x2="{x(n - 1):.1f}" y2="{yy:.1f}" stroke="{grid}" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{left - 8}" y="{yy + 4:.1f}" fill="{muted}" font-size="11" text-anchor="end">'
            f"{(v - 1) * 100:+.0f}%</text>"
        )

    for frac in (0.0, 0.5, 1.0):
        v = dd_lo + (dd_hi - dd_lo) * frac
        yy = ydd(v)
        lines.append(
            f'<line x1="{left}" y1="{yy:.1f}" x2="{x(n - 1):.1f}" y2="{yy:.1f}" stroke="{grid}" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{left - 8}" y="{yy + 4:.1f}" fill="{muted}" font-size="11" text-anchor="end">'
            f"{v * 100:.0f}%</text>"
        )

    lines += [
        f'<path d="M {dd_area}" fill="rgba(255,69,58,0.28)" stroke="none"/>',
        f'<polyline points="{dd_pts}" fill="none" stroke="#ff453a" stroke-width="1.2"/>',
        f'<line x1="{left}" y1="{eq_bottom}" x2="{x(n - 1):.1f}" y2="{eq_bottom}" stroke="{axis}" stroke-width="1"/>',
        f'<polyline points="{eq_pts}" fill="none" stroke="#2997ff" stroke-width="1.8"/>',
        f'<line x1="{split_x:.1f}" y1="{eq_top}" x2="{split_x:.1f}" y2="{dd_bottom}" stroke="rgba(255,255,255,0.45)" stroke-width="1" stroke-dasharray="4 4"/>',
        f'<text x="{left}" y="{eq_top + 14}" fill="#d3d3d3" font-size="11">训练（前 75%）</text>',
        f'<text x="{split_x + 6:.1f}" y="{eq_top + 14}" fill="#d3d3d3" font-size="11">验证（后 25%，仅检验）</text>',
        f'<text x="{left}" y="{height - 8}" fill="{muted}" font-size="11">{html.escape(dates[0])}</text>',
        f'<text x="{split_x:.1f}" y="{height - 8}" fill="{muted}" font-size="11" text-anchor="middle">{html.escape(mid)}</text>',
        f'<text x="{x(n - 1):.1f}" y="{height - 8}" fill="{muted}" font-size="11" text-anchor="end">{html.escape(dates[-1])}</text>',
        "</svg>",
    ]
    return "\n".join(lines) + "\n"


def backtest_detail_name(code: str) -> str:
    return f"stock-analyzer-backtest-{code}.md"


def backtest_detail_permalink(code: str) -> str:
    return f"/docs/stock-analyzer-backtest-{code}/"


def build_backtest_page(data: dict, svg_name: str) -> str:
    code = data["code"]
    name = data.get("name", "")
    strat = data.get("strategy", {})
    params = strat.get("params", {})
    param_txt = ", ".join(f"`{k}={v}`" for k, v in params.items())
    rng = data.get("range", ["", ""])
    exec_txt = (
        "T 日收盘信号 → T+1 收盘成交"
        if data.get("exec") == "close"
        else str(data.get("exec"))
    )
    version = data.get("version", "")

    full, train, val = data["full"], data["train"], data["val"]
    rows = metrics_rows(full), metrics_rows(train), metrics_rows(val)
    labels = ["全期", "训练集（前75%）", "验证集（后25%）"]
    table = ["| 指标 | " + " | ".join(labels) + " |", "|---|---|---|---|"]
    for i in range(len(rows[0])):
        cells = " | ".join(r[i][1] for r in rows)
        table.append(f"| {rows[0][i][0]} | {cells} |")

    ic1, ic5 = data.get("ic1", [None, 0]), data.get("ic5", [None, 0])
    fwd = data.get("fwd", {})
    fwd_table = ["| 信号 | T+1 | T+5 |", "|---|---|---|"]
    for side, label in (("BUY", "买入信号后"), ("SELL", "卖出信号后")):
        if side in fwd:
            fwd_table.append(
                f"| {label} | {fwd_cell(fwd, side, '1')} | {fwd_cell(fwd, side, '5')} |"
            )

    return f"""{make_front_matter(f"stock-analyzer · 回测报告 {code}", backtest_detail_permalink(code))}
[← 返回文档中心](/docs/) · [stock-analyzer 文档](/docs/stock-analyzer/) · [全部回测报告](/docs/stock-analyzer-backtest/) · 同步于 {TODAY}

`{code}` {name} · 策略 **{strat.get("label", "—")}**（`{strat.get("algo", "—")}` · {strat.get("mode", "—")}） · stock-analyzer v{version} · 导出时间 {data.get("ts", "")}

> 回测区间 {rng[0]} ~ {rng[1]}；成交口径：{exec_txt}，ATR 止损 + 移动止盈，无手续费。
> 训练/验证按时间前 75% / 后 25% 切分，**验证集不参与选型、仅供指标检验**。
> 参数：{param_txt or "—"}。

![stock-analyzer 单股回测净值与回撤（{code}）](/assets/img/{svg_name})

## 指标

{chr(10).join(table)}

## 信号质量

| 指标 | 数值 |
|---|---|
| IC(T+1) | {fmt_num(ic1[0], 3)}（n={ic1[1]}） |
| IC(T+5) | {fmt_num(ic5[0], 3)}（n={ic5[1]}） |

{chr(10).join(fwd_table)}

> 本页由 `scripts/sync_docs.py` 自动生成：读取 `research/gui_backtests/` 中该股最新一次
> GUI「导出回测」JSON（数据源与本机 stock-analyzer 一致）。
> 所有输出仅为历史数据的技术统计与研究用途，不构成任何投资建议。
"""


def build_backtest_index(exports: dict[str, dict]) -> str:
    rows = [
        "| 股票 | 策略 | 导出时间 | 全期收益 | 年化 | 胜率 | 最大回撤 | 报告 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for code in sorted(exports):
        data = exports[code]
        full = data.get("full", {})
        strat = data.get("strategy", {})
        rows.append(
            "| {code} {name} | {label} | {ts} | {total} | {ann} | {win} | {mdd} | "
            "[查看](/docs/stock-analyzer-backtest-{code}/) |".format(
                code=code,
                name=data.get("name", ""),
                label=strat.get("label", "—"),
                ts=data.get("ts", "—"),
                total=fmt_pct(full.get("total")),
                ann=fmt_pct(full.get("ann")),
                win=f"{full.get('winrate', 0) * 100:.1f}%" if full else "—",
                mdd=fmt_pct(full.get("mdd")),
            )
        )
    return f"""{make_front_matter("stock-analyzer · 回测报告", BACKTEST_PERMALINK)}
[← 返回文档中心](/docs/) · [stock-analyzer 文档](/docs/stock-analyzer/) · 同步于 {TODAY}

stock-analyzer GUI「导出回测」产物汇总（留档于本机 `research/gui_backtests/`），
每只股票展示最新一次导出；点击「查看」进入单股详情（指标 + 净值/回撤曲线）。

{chr(10).join(rows)}

> 本页由 `scripts/sync_docs.py` 自动生成。验证集不参与选型、仅供指标检验，
> 所有输出仅为历史数据的技术统计与研究用途，不构成任何投资建议。
"""


def load_latest_exports() -> dict[str, tuple[tuple[str, float], Path, dict]]:
    exports: dict[str, tuple[tuple[str, float], Path, dict]] = {}
    for path in GUI_BACKTESTS.glob("gui_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        code = data.get("code")
        if not code:
            continue
        key = (str(data.get("ts", "")), path.stat().st_mtime)
        if code not in exports or key > exports[code][0]:
            exports[code] = (key, path, data)
    return exports


def update_derived_pages(dry: bool) -> list[Path]:
    changed: list[Path] = []
    exports = load_latest_exports()
    if not exports:
        log(f"  ! 未找到回测导出：{GUI_BACKTESTS}/gui_*.json")
    written: dict[Path, str] = {}
    for code in sorted(exports):
        _, src_json, data = exports[code]
        try:
            svg_name = f"stock-analyzer-backtest-{code}.svg"
            page = build_backtest_page(data, svg_name)
            svg = build_backtest_svg(data)
        except (ValueError, KeyError, TypeError) as exc:
            log(f"  ! 回测导出解析失败（{src_json.name}）：{exc}")
            continue
        target = DOCS / backtest_detail_name(code)
        old = target.read_text(encoding="utf-8") if target.is_file() else ""
        if old and strip_backlink(split_front_matter(old)[1]) == strip_backlink(
            split_front_matter(page)[1]
        ):
            log(f"  = {src_json.name}（{code}）无变化")
            continue
        written[target] = page
        written[ASSETS / svg_name] = svg
        changed.append(target)
        log(f"  + {src_json.name} → docs/{target.name} + assets/img/{svg_name}")

    index = DOCS / BACKTEST_PAGE
    index_page = build_backtest_index(
        {code: data for code, (_, _, data) in exports.items()}
    )
    old = index.read_text(encoding="utf-8") if index.is_file() else ""
    if not old or strip_backlink(split_front_matter(old)[1]) != strip_backlink(
        split_front_matter(index_page)[1]
    ):
        written[index] = index_page
        changed.append(index)
        log(f"  ~ 更新 docs/{BACKTEST_PAGE}（回测报告索引）")

    if not dry:
        ASSETS.mkdir(parents=True, exist_ok=True)
        for path, content in written.items():
            path.write_text(content, encoding="utf-8")

    index = DOCS / "index.md"
    text = index.read_text(encoding="utf-8")
    new = re.sub(r"最近一次同步：\d{4}-\d{2}-\d{2}", f"最近一次同步：{TODAY}", text)
    if "stock-analyzer-backtest" not in new:
        new = new.replace(
            "[插件 API](/docs/stock-analyzer-plugin-api/) |",
            "[插件 API](/docs/stock-analyzer-plugin-api/) · [单股回测报告](/docs/stock-analyzer-backtest/) |",
        )
    if new != text:
        changed.append(index)
        if not dry:
            index.write_text(new, encoding="utf-8")
        log(f"  ~ 更新 docs/index.md")

    home = SITE / "index.md"
    text = home.read_text(encoding="utf-8")
    if "stock-analyzer-backtest" not in text:
        new = text.replace(
            '<a href="/docs/stock-analyzer-architecture/">架构</a>',
            '<a href="/docs/stock-analyzer-architecture/">架构</a>'
            '<a href="/docs/stock-analyzer-backtest/">回测</a>',
        )
        if new != text:
            changed.append(home)
            if not dry:
                home.write_text(new, encoding="utf-8")
            log("  ~ 更新首页 index.md 入口")
    return changed


def git(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        ["git", "-C", str(SITE), *args], capture_output=True, text=True
    )
    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(
            proc.returncode, proc.args, proc.stdout, proc.stderr
        )
    return proc


def commit_and_push(push: bool) -> None:
    status = git(["status", "--porcelain"]).stdout.strip()
    if not status:
        log("无文件变化，跳过提交。")
        return
    log("\n待提交：\n" + status)
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    if push:
        pull = git(["pull", "--rebase", "--autostash"], check=False)
        if pull.returncode != 0:
            log("! git pull --rebase 失败，已取消（请手动处理后重试）")
            log(pull.stderr.strip())
            return
    git(["add", "-A"])
    msg = f"自动同步文档：项目 README + stock-analyzer 回测报告（{TODAY}）"
    commit = git(["commit", "-m", msg], check=False)
    if commit.returncode != 0:
        log("! 提交失败：\n" + (commit.stderr or commit.stdout).strip())
        sys.exit(1)
    log(f"已提交：{msg}")
    if not push:
        log("已跳过推送（--no-push）。")
        return
    result = git(["push", "origin", branch], check=False)
    if result.returncode != 0:
        log("! 推送失败：请检查网络/凭证后重试（本地提交已保留）")
        log((result.stderr or result.stdout).strip())
        sys.exit(1)
    log(f"已推送到 origin/{branch}。")


def main() -> None:
    parser = argparse.ArgumentParser(description="同步文档与回测报告并推送")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不写文件不提交")
    parser.add_argument("--no-push", action="store_true", help="只本地提交，不推送")
    parser.add_argument("--no-sources", action="store_true", help="只更新回测报告")
    args = parser.parse_args()

    log(f"站点：{SITE}")
    log(f"日期：{TODAY}")
    if not args.no_sources:
        log("\n[1/2] 同步项目文档")
        for entry in SOURCES:
            dst = DOCS / entry["dst"]
            old = dst.read_text(encoding="utf-8") if dst.is_file() else ""
            new = build_source_doc(entry, old, args.dry_run)
            if new is None:
                continue
            if new == old:
                log(f"  = {entry['dst']}")
                continue
            if not args.dry_run:
                dst.write_text(new, encoding="utf-8")
            log(f"  + {entry['src'].name} → docs/{entry['dst']}")
    log("\n[2/2] 生成回测报告")
    update_derived_pages(args.dry_run)
    if args.dry_run:
        log("\n[dry-run] 未写入文件、未提交、未推送。")
        return
    commit_and_push(push=not args.no_push)


if __name__ == "__main__":
    main()
