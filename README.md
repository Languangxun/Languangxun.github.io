# 獨白 · Languangxun.github.io

个人主页与项目文档站（GitHub Pages + Jekyll 自定义主题）。

- 站点地址：https://languangxun.github.io
- 首页：`index.md`，首屏为 `_includes/hero.html`（头像 + SVG 书写动画 + 签名）
- 布局：`_layouts/default.html`、`_layouts/page.html`
- 样式：`assets/css/style.css`；脚本：`assets/js/main.js`
- 头像：`assets/img/avatar.png`
- 首屏「Monologue」书写动画：`_includes/monologue-ink.svg`，由 [InkTrail](https://github.com/GXeLla/InkTrail)（MIT）的 Apple-like 预设（Caveat 字体）离线生成，自包含 CSS 动画
- 版式参考 [iamreiyn/apple-website-clone](https://github.com/iamreiyn/apple-website-clone)（MIT）的 apple.com 布局，配色改为深色
- 项目文档：`docs/`（Markdown，带 front matter）
- 联系方式：Telegram `@Monologue_101`、QQ `2180287399`

新增文档：把 Markdown 放入 `docs/`，在开头加上 `layout: page`、`title`、`permalink` 三个字段，提交推送到 `main` 分支后 GitHub Pages 自动构建。

注意：本项目是文档站，不要提交 API Key、密码、内网地址等敏感信息。
