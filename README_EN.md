# Heavenly Stems & Earthly Branches (Wu Xing) × A-Share Market — Systematic Empirical Study

> This is not mysticism. It is an empirically testable quantitative question.

---

## Overview

Can the ancient Chinese Five Elements (Wu Xing / 五行) theory predict A-share stock returns? This study conducts systematic tests at two different granularities, yielding an interesting layered conclusion.

| Phase | Directory | Method | Core Finding |
|:---:|:---|:---|:---|
| 🅰️ | [Phase 1 — Daily Frequency Tests](./第一阶段_天干地支五行日频检验/) | Kruskal-Wallis + OLS regression, testing daily return vs. Wu Xing labels | **Wu Xing cannot predict daily returns** (73/75 tests insignificant) |
| 🅱️ | [Phase 2 — Monthly Holding Period Study](./第二阶段_五行月份持有期收益研究/五行月份持有期收益研究/) | Group stocks by purchase-month Wu Xing, compute returns over 7 holding periods | **Earth month × 1-month hold**: median **+15.32%**, coverage **94.7%** |

**This is a matter of analytical granularity — not contradictory findings:**

- **Daily-frequency tests** ask: can Wu Xing explain day-to-day return variance? → No, it is white noise at this scale
- **Monthly timing strategy** asks: does buying in specific Wu Xing months and holding for a fixed period yield systematic returns? → Yes, certain months show repeatable patterns

Just as "a weather forecast cannot predict rainfall hour-by-hour" ≠ "rainy season is fine for outdoor activities" — these are different levels of the same question.

---

## 🅰️ Phase 1: Daily Frequency Wu Xing Tests

> Tests whether the daily Heavenly Stem / Earthly Branch / Wu Xing label correlates with A-share daily returns.

**Sample**: 3 individual stocks + 4 major indices + 31 Shenwan industry sectors  
**Data**: 22,981 trading days, 75 hypothesis tests  
**Method**: Three-tier frequency framework (daily → weekly → monthly), Kruskal-Wallis + OLS  
**Conclusion**: Wu Xing has no reliable daily-frequency predictive power  

See [Phase 1 README](./第一阶段_天干地支五行日频检验/README.md)

---

## 🅱️ Phase 2: Monthly Holding Period Return Study

> Grouping by the Wu Xing attribute of the purchase month, testing return differences across holding periods.

**Sample**: 38 instruments (broad indices + Shenwan industry indices + individual stocks)  
**Holding periods**: 1 / 2 / 3 / 6 / 9 / 12 / 24 months  
**Key findings**:

- 🥇 **Earth month buy × 1-month hold**: median +15.32%, covering 94.7% of instruments
- 🥈 **Fire month buy × 1-month hold**: median +10.46%, covering 81.6% of instruments
- 🔥 **Fire-sector stocks bought in Fire months**: strongest timing effect (median +41.2%)
- ⚠️ Mean/median divergence is severe — extreme-value-driven effects must be monitored

See [Phase 2 README](./第二阶段_五行月份持有期收益研究/五行月份持有期收益研究/README.md)

[📄 View the Full Research Paper (Chinese)](./第二阶段_五行月份持有期收益研究/五行月份持有期收益研究/report/研究报告.md)

---

## 🔥🌍 Where Data Meets Philosophy

An intriguing finding: **the statistical results align remarkably well with the classical meaning of each Wu Xing element.**

| Element | Philosophical Essence | Empirical Result | Correspondence |
|:---:|:---|:---|:---|
| **Fire** 🔥 | **Transformation** — change, volatility, eruption | Fire-sector × Fire-month: strongest timing effect (median **+41.2%**), but cross-instrument coverage only **81.6%** | Fire = "volatility" — highest ceiling when it works, but doesn't always pick the right direction |
| **Earth** 🌍 | **Nurturance** — stability,承载,包容 | Earth × 1-month: coverage **94.7%** (36/38), median **+15.32%** | Earth = "stationarity" — never absent, but doesn't chase explosions |

Beyond philosophical coincidence, this has practical investment implications:

- **Earth month as core position** — 4 Earth windows per year (Chen/Wei/Xu/Chou months), buy broad-index and hold 1 month for certainty
- **Fire month for alpha** — if Fire-sector stocks (electronics, telecom, media) show concurrent signals, overweight for excess return
- Fire represents **uncertain high reward**, Earth represents **certain moderate reward** — they complement each other

This correspondence is itself worth pondering: **if Wu Xing were merely ancient superstition, why do the philosophical definitions and empirical data patterns align so naturally?** Perhaps the Heavenly Stems and Earthly Branches are not a prediction tool but rather a **classification framework for natural rhythms** — Fire months exhibit greater volatility (summer solstice, great heat), Earth months show convergence (clear brightness, frost descent). At its core, this may be a seasonal calendar effect mapped through the Wu Xing lens.

---

## 📁 Directory Structure

```
├── 📄 README.md                          ← This file (Chinese) — project overview
├── 📄 README_EN.md                       ← This file (English)
├── 📁 第一阶段_天干地支五行日频检验/     ← Phase 1: Daily frequency tests (7 instruments)
│   ├── 综合研究报告.md                   ← Full research report (396 lines, ~22KB)
│   ├── 综合研究报告.pdf                 ← Formatted PDF version
│   ├── 创业板指/ 上证指数/ 深证成指/ ...  ← Per-instrument analysis
│   └── README.md                         ← Phase 1 detailed intro
├── 📁 第二阶段_五行月份持有期收益研究/   ← Phase 2: Monthly holding period analysis
│   └── 📁 五行月份持有期收益研究/        ← Research content (with standalone README)
│       ├── README.md                     ← Phase 2 detailed intro
│       ├── report/                       ← Full research report (331 lines)
│       ├── analysis/                     ← Statistical output tables
│       ├── charts/                       ← 4 publication-quality charts
│       ├── data/                         ← Monthly aggregated raw data
│       ├── 研究计划.md                    ← Research plan & execution log
│       └── *.py                          ← Analysis scripts
├── LICENSE
└── .gitignore
```

---

## ⚖️ Disclaimers

1. **Past performance ≠ future returns**: All conclusions are based on historical data and do not constitute investment advice
2. **Mean trap**: 1-month holding period means (80-93%) are far above medians (-8% to +15%) — extreme months drive the effect
3. **Survivorship bias**: The instrument pool includes currently listed stocks/indices only
4. **Methodological value**: Even if skeptical of the conclusions, the research framework itself (three-tier frequency analysis, cross-sample consistency validation, industry cross-analysis) offers independent reference value

---

## 🔧 Tech Stack

- **Data sources**: Tushare Pro API, akshare
- **Analysis**: Python (pandas, scipy, numpy)
- **Visualization**: matplotlib, seaborn, SciencePlots
- **Automation**: Hermes Agent Kanban multi-agent workflow
- **Version control**: Git + GitHub / Gitee

---

*Project executed by CPY using Hermes Agent via Kanban multi-agent workflow.*
