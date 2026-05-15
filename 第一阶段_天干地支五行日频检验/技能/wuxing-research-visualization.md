---
name: wuxing-research-visualization
description: "Publication-quality academic charts for Chinese Five Elements (WuXing) × financial market returns research. Generates 4 chart types per sample: daily boxplot, weekly rolling, monthly analysis, p-value summary. Supports both stock and index data formats."
version: 1.0.0
author: Hermes Agent
tags: [visualization, matplotlib, academic, chinese-font, wuxing, financial-research]
---

# WuXing Research Visualization

Generates Nature/Science-style academic charts for the "天干地支五行 × 金融收益率" (Chinese Heavenly Stems & Earthly Branches Five Elements × Financial Returns) research project.

## What it does

Creates 4 publication-quality charts per research sample (28 charts for 7 samples):
1. **fig1_daily_boxplot.png** — Boxplot of daily returns grouped by TianGan/DiZhi WuXing
2. **fig2_weekly_rolling.png** — Weekly rolling mean comparison across WuXing groups + pairwise differences
3. **fig3_monthly_train_test.png** — Monthly train/test split comparison (for stocks) OR time series bar (for indices)
4. **fig4_summary_pvalues.png** — Horizontal bar chart of all Kruskal-Wallis test p-values

## Usage

```bash
cd /path/to/research/root
python3 generate_all_plots.py
```

## Data format

Supports two formats auto-detected by the script:

**Stock format** (e.g., 农业银行, 五粮液):
- `data/data_daily_with_ganzhi.csv` — columns: ts_code, trade_date, log_return, day_tg_wuxing, day_dz_wuxing, ...
- `data/data_weekly.csv` — columns: week_return, week_tg_wuxing, ...
- `data/data_monthly.csv` — columns: month_return, month_tg_wuxing, month_dz_wuxing, ...
- `统计表/table_all_tests.csv` — columns: 阶段, H统计量, p值, 显著...

**Index format** (e.g., 上证指数, 深证成指):
- `data/data_daily.csv` — columns: 收益率, 五行_干, 五行_支, ...
- `data/data_weekly.csv` — columns: 收益率, 五行_干, ...
- `data/data_monthly.csv` — columns: 收益率, 五行_干, ...
- `统计表/table_all_tests.csv` — columns: 检验, H统计量, p值, 显著...

## Customization

Edit `RESEARCH_ITEMS` list in `generate_all_plots.py` to add/remove samples.
Edit `academic_style.py` for color schemes, font settings, or layout tweaks.

## Requirements

```bash
pip install matplotlib pandas numpy
```

Chinese font: `AR PL UKai CN` or `Noto Sans CJK SC` or similar.

## Chinese Font Setup

On Linux, Noto Sans CJK TTC files have a known issue where matplotlib reads only the JP variant. See `references/chinese-font-setup.md` for details on font detection, configuration, and troubleshooting.

## Reference Files

- `references/academic_style.py` — Common style module (colors, fonts, axis helpers)
- `references/generate_all_plots.py` — Master plotting script template
- `references/chinese-font-setup.md` — Chinese font troubleshooting for matplotlib
