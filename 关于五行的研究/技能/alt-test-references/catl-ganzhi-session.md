# 宁德时代(300750.SZ) 天干地支五行检验 — Session Reference

**Date**: 2026-05-14
**Stock**: 宁德时代 (300750.SZ)
**Data**: 1,918 records from 2018-06-11 to 2026-05-13 (after join with trade_calendar)

## Quick Reference: All 9 KW Tests

| Test | H-stat | p-value | Significant? |
|------|--------|---------|-------------|
| 日频-天干 | 6.7592 | 0.1492 | ❌ |
| 日频-地支 | 4.8331 | 0.3049 | ❌ |
| 周频-天干 | 2.6748 | 0.6136 | ❌ |
| 周频-地支 | 0.8319 | 0.9341 | ❌ |
| 月频-天干(训练) | 1.7186 | 0.7873 | ❌ |
| 月频-地支(训练) | 11.5666 | **0.0209** | ✅❗overfit |
| 月频-天干(测试) | 9.6844 | **0.0461** | ✅❗direction reversed |
| 月频-地支(测试) | 6.4413 | 0.1685 | ❌ |
| 稳健性-缩尾日天干 | 6.7602 | 0.1491 | ❌ |

**Result**: 2/9 nominally significant, but training pattern (火>水) completely reversed in test set (水>>火). Classic overfitting. Conclusion: 无关 (no reliable predictive power).

## Comparison with Agricultural Bank and Wuliangye

| Aspect | 农业银行(601288) | 五粮液(000858) | 宁德时代(300750) |
|--------|----------------|---------------|-----------------|
| Records | 3,833 | 3,902 | 1,918 |
| Date range | 2010-07~2026-05 | 2010-01~2026-05 | 2018-06~2026-05 |
| Coverage | ~16 years | ~16 years | ~8 years |
| Daily p (天干) | 0.917 | 0.215 | 0.149 |
| Daily p (地支) | 0.146 | 0.827 | 0.305 |
| 9 tests significant | 0 | 0 | 2 (overfit) |
| Direction consistency | ❌ | ❌ | ❌ |
| Regression finding | 五行是阳历代理变量 | 五行是阳历代理变量 | 五行是阳历代理变量 |
| **Final conclusion** | **无关** | **无关** | **无关** |

## Key Findings

1. **Daily KW tests**: No significant differences in daily returns across 天干五行 or 地支五行 groups (p=0.149, p=0.305)
2. **Weekly rolling window**: All pair differences oscillate around zero — no stable directional drift
3. **Monthly overfitting**: Training set showed 地支五行 significant (p=0.021, 火月均+11.4%), but test set reversed (水+11.85% >> 火+0.51%). Both 月天干 and 月地支 nominal significance in test set are attributed to the same overfit pattern.
4. **Calendar confounding**: After adding month dummies, all 五行 coefficients became insignificant — confirming 五行 is a proxy for solar calendar months.
5. **Robustness**: Winsorization confirms null result (p=0.149)

## Caveat

CATL has only ~8 years of trading history (2018-2026) compared to 农行/五粮液's ~16 years. The shorter sample reduces statistical power at the monthly frequency (only ~94 months total, vs ~194 for the others). The 2 nominal significances that emerged may reflect the noisier small-sample estimate rather than a true effect — and the direction reversal confirms they are not predictive.

## All Available Data

All datasets at `关于五行的研究/宁德时代/`:

- `analysis_main.py` — Full pipeline script
- `visualizations.py` — 4-figure generator
- `data_daily.csv` (1,918 rows), `data_weekly.csv`, `data_monthly.csv`
- `table_all_tests.csv`, `table_daily_tg_wuxing.csv`, `table_daily_dz_wuxing.csv`, `table_weekly_rolling.csv`
- `fig1_daily_boxplot.png` ~ `fig4_summary_all.png`
- `结论报告.md`, `学术论文_宁德时代天干地支五行检验.md`
