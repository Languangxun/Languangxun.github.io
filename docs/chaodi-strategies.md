---
layout: page
title: "chaodi 策略选股（18 策略）"
permalink: /docs/chaodi-strategies/
---

[← 返回文档中心](/docs/) · 来源：本地项目（暂未单独开源） · 同步于 2026-09-25

内置 **18 个短线选股策略**，用 **通达信语义**（MA/EMA/MACD/BOLL/KDJ/RSI/ATR…）
在本地重算指标与信号，数据直接复用 `stock_predict/stock_cache.db`
（约 5500 只 A 股日K，后复权 + adjust 转乘法前复权）。

> 仅统计参考，不构成投资建议。

---

## 一、目录结构

```
chaodi_strategies/
├── et_engine/
│   ├── data.py          本地 SQLite 读取、代码转换（sh600000 ↔ 600000.SH）、复权
│   ├── indicators.py    TDX 语义指标引擎（numpy + scipy 加速）
│   ├── signals.py       signal_* 信号（金叉/突破/新高低/涨停/连板/炸板…）
│   ├── strategies.py    18 个策略的 filter / scoring / 退出规则
│   ├── universe.py      股票池元数据（名称/市值/行业）与 basic_filter
│   └── scan.py          扫描引擎（全市场跑一个策略 + 横截面评分）
├── scan.py              CLI 入口
├── gui.py               Tkinter GUI（chaodi 暗色风格，K线 + 信号标记）
├── web/                 云端网站（登录/扫描/K线/导出/定时任务）
├── deploy/              systemd 服务 + 安装/推送脚本
├── tools/               精简行情库生成
└── tests/               冒烟测试
```

## 二、快速开始

```bash
# 依赖（stock_predict/.venv 已含 numpy/scipy）
/home/lan/桌面/stock_predict/.venv/bin/python3 scan.py --list      # 列出 18 策略
/home/lan/桌面/stock_predict/.venv/bin/python3 scan.py trend_breakout
/home/lan/桌面/stock_predict/.venv/bin/python3 scan.py --all --top 10
/home/lan/桌面/stock_predict/.venv/bin/python3 scan.py boll_breakout \
    --as-of 2026-09-16 --params vol_ratio_min=2.0 --csv picks.csv
/home/lan/桌面/stock_predict/.venv/bin/python3 gui.py              # 图形界面
```

环境变量 `STOCK_DB` 可指定 `stock_cache.db` 路径（默认取同级 `stock_predict/`）。
数据过期时先用 `stock_gui.py`（或 GUI 内「刷新代码表」补名称/市值）更新行情。

## 三、18 个策略

| id | 名称 | 规则摘要 |
|---|---|---|
| boll_breakout | 布林突破 | 突破布林上轨 + 量比≥1.5 |
| broken_board_recovery | 断板反包 | 涨停 + 量比≥1.5 + 涨幅>3% |
| bullish_alignment | 均线多头 | MA5>MA10>MA20>MA60 + 20日动量>0 |
| consecutive_limit_ups | 连板股 | 当日涨停且连板≥2 |
| high_turnover_surge | 高换手拉升 | 换手>5% 且涨幅>3% |
| limit_up_momentum | 连板接力 | 连板≥1 且涨幅>5% |
| low_volatility_leader | 低波动龙头 | 20日动量>0 + 年化波动<30% + MA20上方 |
| ma_golden_cross | MA 金叉 | MA5上穿MA20 + 量比≥1.2 + MA60上方 |
| macd_golden | MACD 金叉放量 | MACD金叉 + 量比≥1.5 |
| n_day_low_reversal | 新低反转 | 60日新低 + 收阳 + 量比≥1.5 |
| near_limit_up | 逼近涨停 | 涨幅>7% 且距涨停<3% |
| oversold_bounce | 超跌反弹 | RSI14<30 + 收阳 + 量比≥1.2 |
| oversold_reversal | 超跌反转 | RSI14<30 + 涨幅>1% + 站上MA5 |
| pullback_ma20_bounce | 均线回踩反弹 | 价格贴近MA20(±2%) + MA5>MA20>MA60 + 上涨 |
| pullback_to_support | 缩量回踩 | 贴近MA20 + 缩量(量比<0.8) + MA60上方 + 20日动量>0 |
| strong_open | 强势高开 | 高开>3% + 收阳 + 涨幅>3% |
| trend_breakout | 趋势突破 | MA60上方 + 60日新高 + 量比≥2 |
| volume_price_surge | 量价齐升 | 突破MA20 + 量比≥2 + 收阳 |

评分口径与服务端一致（已对拍）：
`score = 100 × Σ w_f × (x_f - min_f)/(max_f - min_f)`，min/max 取自通过过滤后的候选池。

## 四、口径验证

指标与信号在开发期与云端服务端做过逐列对拍（现已移除基准数据，仅保留结论）：

| 类别 | 结论 |
|---|---|
| MA/EMA/成交量均线/BOLL/动量/涨跌幅/振幅/波动率/WR | 中位相对误差 ~1e-8（float32 舍入级） |
| KDJ/RSI/ATR（Wilder） | 公式一致 |
| 入场/出场信号（金叉/突破/新高低/放量/涨停/连板/炸板） | 近端 120 根匹配率 ≥ 99% |
| 18 策略选股 + 评分 | 同池内完全一致 |

本地行情与服务端行情商在个别交易日/除权日会有差异，属数据源差异，不影响引擎本身。

## 五、数据口径说明

- **价格**：库内为后复权，按 `adjust.k` 缩放为乘法前复权（最新价≈真实价），
  与服务端 `close` 同口径；分红除权日与服务端复权因子可能有细微差异。
- **成交额**：本地无 amount 字段，用 `volume×100×close` 近似（误差 <1%）。
- **换手率/市值**：由「刷新代码表」从腾讯行情批量写入 `stocks`（名称/总市值）并
  在 `stock_cache.db` 新建 `et_shares` 表（由市值/现价反推总股本），
  换手率 = `成交量×100/总股本×100`，与服务端口径一致。
- **市值过滤**：`stocks.mktcap` 缺失时会被市值条件排除，建议先刷新代码表。
- **成交量单位**：腾讯日K对科创板(688/689)返回「股」，其余板块返回「手」；
  引擎在读取时统一折算为手（否则科创板换手率/成交额会放大 100 倍）。
- **停牌老股**：扫描默认跳过「最后K线早于库内最新交易日 3 天以上」的代码
  （避免退市/长期停牌股混入结果）；指定 `--as-of` 时以该日为准。
- **涨停判定**：按板块/ST 的涨跌幅限制 + 价格四舍五入。注意：本地库走腾讯
  **后复权(hfq)**，实测腾讯 hfq 在个别分红除权日与其自家 qfq/东财原始行情不一致
  （如 000055 于 2026-09-16 应为 +10.09% 涨停，腾讯 hfq 只给出 +7.7%），
  会漏判该日涨停/连板。东财原始行情（push2his fqt=0）可复核；
  如需修正可对相关个股重新拉取或用东财源回填。

## 六、云端网站（Orange Pi / Tailscale）

`web/` 是零依赖（仅需 numpy，scipy 可选）的网页版，可在 Orange Pi 上 7×24 运行，
Tailscale 内网访问，账号密码登录：

```bash
# 本机预览
python web/set_password.py admin --password 你的密码
python web/server.py                      # http://127.0.0.1:8720/
```

**已部署实例（Orange Pi Zero 2W）**

| 项 | 值 |
|---|---|
| **公网（Tailscale Funnel）** | `<Tailscale-Funnel-地址>` |
| 局域网 | `http://<Pi-局域网IP>:8720/` |
| Tailscale 内网 | `http://<Tailscale-IP>:8720/` |
| 账号 | `admin` / 见 `web/auth.json` 设置时的输出（改密码见下） |
| 服务 | `systemctl status chaodi-web`（开机自启，`journalctl -u chaodi-web -f`） |
| 数据 | `~/chaodi_strategies/data/stock_cache.db`（精简库，约 386MB） |
| 性能 | 全市场单策略约 45 秒（多进程 4 核；单进程约 100 秒） |
| 定时 | 每日 15:10 自动扫全部策略、15:40 增量更新行情 |
| 穿透配置 | `sudo tailscale funnel --bg --https=8443 http://127.0.0.1:8720`（443 留给「股票形态预测」服务，互不影响）；关闭：`tailscale funnel --https=8443 off` |

```bash
# 从本机重新推送（生成精简库 → rsync → 远端安装）
bash deploy/push_to_pi.sh orangepi@<Pi-局域网IP>            # 全量
bash deploy/push_to_pi.sh orangepi@<Pi-局域网IP> --skip-db  # 只更新代码
# 改密码（在 Pi 上执行）
ssh orangepi@<Pi-局域网IP>
cd ~/chaodi_strategies && .venv/bin/python web/set_password.py admin
```

网站功能：

| 能力 | 说明 |
|---|---|
| 登录/注册 | 多用户（SQLite `web/users.db`）；开放注册可开关，支持授权码开通订阅 |
| 用户管理 | 管理员可禁用/删除/重置密码/设有效期/设为管理员；改密或禁用即时踢下线 |
| 在线扫描 | 18 策略任选、参数可调，后台单任务队列 + 实时进度 |
| K线 | 任意代码看K线（MA5/10/20/60 + 成交量 + MACD 四色副图）|
| 抄底信号 | 通达信 VAR2 体系（买点1/最佳点/买点2/抄底/底初选 + 快到底绿区），免费无需授权 |
| 自选池 | 代码/名称模糊搜索、加自选、导出通达信 `.blk`/CSV，免费（未授权也能用） |
| 结果 | 表格排序、K线弹窗（策略买点 B 标记）、CSV / 通达信 `.blk` 导出 |
| 定时任务 | `web/config.json`：每日 15:10 自动扫全部策略、15:40 增量更新行情 |
| 行情更新 | `web/update_data.py`（腾讯 hfq 增量 + 代码表/复权系数），网页按钮也能触发 |
| 数据 | `data/stock_cache.db`（由 `tools/make_slim_db.py` 生成，每只 550 根） |

Tailscale 访问：Pi 上 `tailscale ip -4` 得到 `100.x.x.x`，手机/电脑浏览器打开
`http://100.x.x.x:8720/`。若开了 ufw：`sudo ufw allow in on tailscale0`。

## 七、GUI 功能

- 左侧 18 策略列表 + 参数面板（与服务端默认值一致，可改）
- 全市场扫描（约 20s，单线程最快），结果表可点表头排序
- 双击个股打开 K 线窗口（蜡烛 + MA5/10/20/60 + 入场信号 B 标记 + 量能）
- 「导出 CSV」；「导出通达信自选(.blk)」可直接复制到
  `通达信/T0002/blocknew/` 目录（沪=1 前缀、深=0 前缀，北交所跳过）
- 「刷新代码表」从东财补齐全市场名称/市值/行业
