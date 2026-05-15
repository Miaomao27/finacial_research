# Agricultural Bank × 天干地支五行 — Complete Session Reference

**Date**: 2026-05-14
**Stock**: 601288.SH (Agricultural Bank of China)
**Data**: 3,833 trading days, 2010-07-15 to 2026-05-13
**Conclusion**: NULL — no significant relationship found (9 tests, 0 significant)

## Complete Results

### All Kruskal-Wallis Tests

| Layer | Test | H-stat | p-value | Significant? |
|-------|------|--------|---------|-------------|
| Daily | 天干五行 | 0.95 | 0.917 | ❌ |
| Daily | 地支五行 | 6.82 | 0.146 | ❌ |
| Weekly | 天干五行 | 5.83 | 0.212 | ❌ |
| Weekly | 地支五行 | 4.81 | 0.307 | ❌ |
| Monthly (train) | 天干五行 | 5.31 | 0.257 | ❌ |
| Monthly (train) | 地支五行 | 4.79 | 0.310 | ❌ |
| Monthly (test) | 天干五行 | 6.90 | 0.141 | ❌ |
| Monthly (test) | 地支五行 | 5.15 | 0.272 | ❌ |
| Robustness (winsorized) | 天干五行 | 0.95 | 0.917 | ❌ |

### Best Training Pattern (reversed in test — classic overfitting)
- Training set: 土 (月均+1.13%) > 火 (月均-1.47%)
- Test set: 土 (-1.17%) < 火 (+0.92%)
- Direction reversed: ❌

### Regression Evidence
| Model | R² | F-test p | Category vars significant? |
|-------|-----|----------|--------------------------|
| Only 天干五行 | 0.03 | 0.206 | — |
| + Calendar month | 0.10 | 0.038 | ❌ No |
| + Year | 0.21 | <0.001 | ❌ No |

## Deliverables

All files at: `/home/cpy/文档/金融数据库建立/研究结果/`

- `analysis_main.py` — Full analysis pipeline
- `visualizations.py` — 4 figure generator
- `fig1_daily_boxplot.png` to `fig4_summary_all.png`
- `结论报告.md` — One-page conclusive report
- `学术论文_农行天干地支五行检验.md` — Academic-style paper
- `data_daily/ weekly/ monthly.csv` — Intermediate data
- `table_all_tests.csv` — All hypothesis test summaries

## Key SQL Patterns

### Join stock data with trade_calendar (with 天干地支)
```sql
SELECT d.证券代码, d.交易日期, d.收盘价, d.前收盘, d.涨跌幅,
       c.年干支, c.月干支, c.日干支, c.星期几, c.年份, c.月份
FROM daily_quote d
JOIN trade_calendar c ON d.交易日期 = c.交易日期
WHERE d.证券代码 = '601288.SH' AND c.是否交易日 = 1
ORDER BY d.交易日期
```

### 五行 Mapping
```python
TIAN_GAN_WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火',
                    '戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
DI_ZHI_WUXING = {'子':'水','丑':'土','寅':'木','卯':'木',
                  '辰':'土','巳':'火','午':'火','未':'土',
                  '申':'金','酉':'金','戌':'土','亥':'水'}
```

### Three-Frequency Aggregation Helper
```python
# Weekly: use first trading day's category
weekly = df.groupby('week_number', sort=True).agg({
    'trade_date': 'first',
    'close_price': lambda x: np.log(x.iloc[-1]/x.iloc[0]),  # weekly return
    'day_tg_wuxing': 'first',  # Monday's category
    'log_return': 'std'  # weekly volatility
})

# Monthly: use month_ganzhi from trade_calendar (by 节气)
monthly = df.groupby('year_month', sort=True).agg({
    'trade_date': 'first',
    'close_price': lambda x: np.log(x.iloc[-1]/x.iloc[0]),
    'month_tg_wuxing': 'first',  # pre-computed from trade_calendar
    'log_return': 'std',
    'trade_date': 'count'  # trading days in month
})
```

## Common Error to Avoid

The SQL column `d.证券代码` must match exactly — Chinese column names in MySQL, not translated aliases. The first attempt failed with `Unknown column 'd.证券_code'` because the underscore translation was wrong.
