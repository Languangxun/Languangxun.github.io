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
      <div class="card-links"><a href="https://github.com/Languangxun/ai-quant">源码</a><a href="/docs/ai-quant/">文档</a><a href="https://orangepizero2w-1.tail6a6cc8.ts.net/quant/">在线演示</a></div>
    </article>

    <article class="project-card reveal">
      <header class="card-top"><h3>stock-analyzer</h3><span class="tag">v6.1.5</span></header>
      <p>基于历史形态相似度匹配 + 多维融合 + 三档组合策略的 A 股短线统计研究工具。</p>
      <div class="card-links"><a href="https://github.com/Languangxun/stock-analyzer">源码</a><a href="/docs/stock-analyzer/">文档</a><a href="/docs/stock-analyzer-architecture/">架构</a><a href="/docs/stock-analyzer-backtest/">回测</a></div>
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
      <header class="card-top"><h3>market-sniper</h3><span class="tag">超短线</span></header>
      <p>港 / 美 / 加密超短线研究与实时交易框架：多市场 K 线、实时引擎、仓位语义信号、港股 LightGBM 买卖点。</p>
      <div class="card-links"><a href="https://github.com/Languangxun/market-sniper">源码</a><a href="/docs/market-sniper/">文档</a></div>
    </article>

    <article class="project-card reveal">
      <header class="card-top"><h3>sm701</h3><span class="tag">机器学习</span></header>
      <p>A 股 T+1 日频上涨概率预测：LightGBM 横截面选股 + TCN 时序形态 + 多周期 + 基本面/资金/事件因子。</p>
      <div class="card-links"><a href="https://github.com/Languangxun/sm701">源码</a><a href="/docs/sm701/">文档</a></div>
    </article>

    <article class="project-card reveal">
      <header class="card-top"><h3>sm702</h3><span class="tag">风控</span></header>
      <p>个股顶部识别与止损模型：LightGBM 学习个股自身顶部特征，输出今日是否需要止损，walk-forward 回测。</p>
      <div class="card-links"><a href="https://github.com/Languangxun/sm702">源码</a><a href="/docs/sm702/">文档</a></div>
    </article>

    <article class="project-card reveal">
      <header class="card-top"><h3>stock-strategy-studio</h3><span class="tag">回测</span></header>
      <p>面向 A 股的本地策略研究与回测工具：自定义策略编辑器、AKShare 行情、Rust 加速、全市场逐股回测。</p>
      <div class="card-links"><a href="https://github.com/Languangxun/stock-strategy-studio">源码</a><a href="/docs/stock-strategy-studio/">文档</a></div>
    </article>

  </div>
</section>
