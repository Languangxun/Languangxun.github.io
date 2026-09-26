# 獨白 · Languangxun.github.io

个人主页与项目文档站（GitHub Pages + Jekyll 自定义主题）。

- 站点地址：https://languangxun.github.io
- 首页：`index.md`，首屏为 `_includes/hero.html`（头像 + SVG 书写动画 + 签名）
- 布局：`_layouts/default.html`、`_layouts/page.html`
- 样式：`assets/css/style.css`；脚本：`assets/js/main.js`
- 头像：`assets/img/avatar.png`
- 首屏「Monologue」书写动画：`_includes/monologue-ink.svg`，由 [InkTrail](https://github.com/GXeLla/InkTrail)（MIT）的 Apple-like 预设（Caveat 字体）离线生成，自包含 CSS 动画
- 版式参考 [iamreiyn/apple-website-clone](https://github.com/iamreiyn/apple-website-clone)（MIT）的 apple.com 布局，配色改为深色
- 项目文档：`docs/`（Markdown，带 front matter，内容同步自本地项目目录并已脱敏）
  - ai-quant：`docs/ai-quant.md`
  - stock-analyzer：`docs/stock-analyzer.md`、`stock-analyzer-architecture.md`、`stock-analyzer-plugin-api.md`
  - stock-analyzer 回测报告：`docs/stock-analyzer-backtest.md`（索引）+ 每只股票 `docs/stock-analyzer-backtest-<code>.md`
  - stock-pi-mobile：`docs/stock-pi-mobile.md`
  - OneOS：`docs/oneos.md`、`oneos-architecture.md`、`oneos-roadmap.md`、`oneos-boot-animation.md`
  - AI 围棋竞技场：`docs/go-arena.md`
  - 文档中心：`docs/index.md`；多篇文档的配图放在 `assets/img/`
- 联系方式：Telegram `@Monologue_101`、QQ `2180287399`

新增文档：把 Markdown 放入 `docs/`，在开头加上 `layout: page`、`title`、`permalink` 三个字段，提交推送到 `main` 分支后 GitHub Pages 自动构建。

## 一键同步文档（`scripts/sync_docs.py`）

从本地项目目录同步文档到本站并推送，桌面快捷方式「更新文档并推送」即调用它：

```sh
python3 scripts/sync_docs.py --dry-run     # 只预览，不写文件不提交
python3 scripts/sync_docs.py               # 同步 + 提交 + 推送
python3 scripts/sync_docs.py --no-push     # 同步 + 本地提交，不推送
python3 scripts/sync_docs.py --no-sources  # 只更新 stock-analyzer 回测报告
```

- 文档镜像：`SOURCES` 表把各项目 README/ARCHITECTURE 等映射到 `docs/`，保留目标文件的
  front matter，自动脱敏（家目录路径、内网 IP、密码/密钥）并把相对图片复制到 `assets/img/`
- 回测报告：读取 `stock-analyzer/research/gui_backtests/gui_*.json`（每只股票最新一次
  GUI「导出回测」），生成指标/信号质量页面与净值+回撤 SVG，并刷新 `docs/stock-analyzer-backtest.md` 索引
- 内容无变化时保留原「同步于」日期，不会产生空提交

注意：本项目是文档站，不要提交 API Key、密码、内网地址等敏感信息。
