---
layout: page
title: "AI 围棋竞技场 · 双 AI 对弈"
permalink: /docs/go-arena/
---

[← 返回文档中心](/docs/) · 来源：本地项目（暂未单独开源） · 同步于 2026-09-25

一个跑在本机浏览器里的双 AI 围棋对弈 Web 应用。黑白双方各配一个模型接口，自动落子对局，无需手动操作。

## 功能

- **双 AI 自动对弈**：黑白双方可分别选择不同的 OpenAI 兼容接口与模型（如 DeepSeek、智谱 GLM 等），各自独立配置温度、最大输出等参数
- **流式输出**：服务端代理转发上游 SSE 流；上游不支持 `response_format` 时自动降级重试，兼容性更好
- **对局观感**：可设置贴目、最大手数、落子延迟、棋盘自动缩放、手数显示
- **本地运行**：仅依赖 Python 标准库，服务只监听 `127.0.0.1`，API Key 保存在本机 `config.json`，不经过第三方服务器

## 运行

```bash
./run.sh        # 启动并自动打开浏览器（默认 http://127.0.0.1:8787/）
./stop.sh       # 停止
```

首次运行请在页面右上角「设置」中填写双方的 API 地址、Key 与模型名称。

## 目录结构

```
new/
├── server.py        # Python 标准库 HTTP 服务：静态文件 + /api/chat 代理
├── run.sh / stop.sh # 启动、停止脚本
├── icon.svg         # 桌面图标
├── config.json      # 对局与模型配置（含 API Key，请勿提交/分享）
└── static/          # 前端（原生 JS/CSS，无框架）
    ├── index.html
    ├── app.js       # 对局逻辑与设置面板
    ├── engine.js    # 棋盘与规则
    ├── view.js      # 渲染
    └── style.css
```

## 安全提示

`config.json` 中保存着真实的 API Key，已被排除在文档同步之外，请勿将其上传到任何公开仓库或分享给他人。若不慎泄露，请立即到对应平台吊销并重新生成。
