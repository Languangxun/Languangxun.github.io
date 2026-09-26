---
layout: default
title: 首页
---

{% include hero.html %}

<section class="section" id="projects">
  <div class="section-head reveal">
    <h2>项目</h2>
    <span class="section-note">SELECTED WORKS</span>
  </div>

  <div class="project-grid">
    <article class="project-card reveal">
      <header class="card-top"><h3>ai-quant</h3><span class="tag">量化</span></header>
      <p>OrangePi 上的 AI 量化研究与模拟交易系统：CLI 选股 + LLM 组合决策 + A 股账本 + 全缓存回测。</p>
      <div class="card-links"><a href="https://github.com/Languangxun/ai-quant">源码</a><a href="/docs/ai-quant/">文档</a></div>
    </article>

    <article class="project-card reveal">
      <header class="card-top"><h3>stock-analyzer</h3><span class="tag">v6.1.5</span></header>
      <p>基于历史形态相似度匹配 + 多维融合 + 三档组合策略的 A 股短线统计研究工具。</p>
      <div class="card-links"><a href="https://github.com/Languangxun/stock-analyzer">源码</a><a href="/docs/stock-analyzer/">文档</a><a href="/docs/stock-analyzer-architecture/">架构</a></div>
    </article>

    <article class="project-card reveal">
      <header class="card-top"><h3>stock-pi-mobile</h3><span class="tag">嵌入式</span></header>
      <p>2.4 寸触摸屏随身盯盘终端：自选 / 荐股 / AI 问答 / WiFi 设置，复用 stock-analyzer 后端。</p>
      <div class="card-links"><a href="/docs/stock-pi-mobile/">文档</a></div>
    </article>

    <article class="project-card reveal">
      <header class="card-top"><h3>OneOS</h3><span class="tag">Rust · mkosi</span></header>
      <p>可启动的模拟操作系统（教学 / 实验用途）：复用 Debian 内核，用户态自研，mkosi 构建 UEFI 镜像。</p>
      <div class="card-links"><a href="https://github.com/Languangxun/oneos">源码</a><a href="/docs/oneos/">文档</a><a href="/docs/oneos-architecture/">架构</a><a href="/docs/oneos-boot-animation/">开机动画</a></div>
    </article>

    <article class="project-card reveal">
      <header class="card-top"><h3>AI 围棋竞技场</h3><span class="tag">Web</span></header>
      <p>本地 Web 应用：黑白两个 AI（OpenAI 兼容接口）自动对弈，可选贴目、落子延迟与手数显示。</p>
      <div class="card-links"><a href="/docs/go-arena/">文档</a></div>
    </article>
  </div>
</section>
