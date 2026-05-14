---
name: alternative-hypothesis-testing
description: "Rigorous statistical framework for testing non-standard/alternative/meta-physical hypotheses against financial market data — three-layer frequency analysis, sample-out-of-sample validation, calendar-effect confounding detection, and robustness checks for Chinese A-share markets."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [finance, statistics, hypothesis-testing, calendar-effect, alternative-investment]
    related_skills: [quantitative-finance-analysis, financial-database-design]
---

# Alternative Hypothesis Testing in Finance

A rigorous framework for testing non-standard or alternative hypotheses (天干地支五行, 节气效应, 生肖论, astrology, numerology, etc.) against financial market data — designed to statistically disprove rather than confirm biases.

## When to Use

Use this skill when:
- User wants to test whether some non-standard factor (calendar-based, metaphysical, astrological) predicts stock returns
- Need a rigorous debunking framework with sample-out-of-sample validation
- Doing multi-frequency analysis (daily/weekly/monthly) to avoid cherry-picking
- Need to separate true signal from calendar-effect confounding
- The hypothesis involves categorical groupings from a non-standard classification system

## Core Philosophy

> **Default assumption: no relationship exists.** The burden of proof is on the hypothesis. All training-set patterns must be validated on a held-out test set. Any relationship that disappears after controlling for calendar variables is a proxy, not a discovery.

## Prerequisites

- Access to `china_finance_db` MySQL database (or equivalent stock price DB)
- Python: `pandas numpy scipy statsmodels matplotlib seaborn`
- The database must contain daily price data and a `trade_calendar` table with the non-standard labels

## Step-by-Step Framework

### Step 1: Data Preparation

```python
# Extract + merge stock data with alternative labels from trade_calendar
import pymysql, pandas as pd, numpy as np

conn = pymysql.connect(host='192.168.31.29', user='finance_user',
                       password='Finance2026!', database='china_finance_db')

sql = """
SELECT d.证券代码 AS ts_code, d.交易日期 AS trade_date,
       d.收盘价 AS close_price, d.前收盘 AS pre_close,
       d.涨跌幅 AS pct_chg, d.成交量 AS volume, d.成交额 AS amount,
       c.年干支 AS year_ganzhi, c.月干支 AS month_ganzhi, c.日干支 AS day_ganzhi,
       c.星期几 AS weekday, c.年份 AS year, c.月份 AS month
FROM daily_quote d
JOIN trade_calendar c ON d.交易日期 = c.交易日期
WHERE d.证券代码 = %s AND c.是否交易日 = 1
ORDER BY d.交易日期
"""
df = pd.read_sql(sql, conn, params=('601288.SH',), parse_dates=['trade_date'])
conn.close()
```

### Step 2: Feature Engineering

**Returns**: Use log returns (log(close/prev_close)) for normality properties. Also create binary direction label.

**Category mapping**: Map the alternative classification to 5-10 groups using a domain-specific dictionary.

```python
# Example: 天干五行 mapping
TIAN_GAN_WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火',
                    '戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
df['day_tg_wuxing'] = df['day_ganzhi'].str[0].map(TIAN_GAN_WUXING)
```

**Control variables** (MANDATORY):
- Day of week dummies (Monday-Friday)
- Calendar month dummies (1-12)
- Year dummies
- Month start/end flags (first/last 5 days)
- Previous day return

### Step 3: Three-Layer Frequency Analysis

**Layer 1 — Daily (baseline)**: Groups by daily category label. Use Kruskal-Wallis non-parametric test. At ~3,800 observations, this has high power to detect even small effects. Expected: no significance.

**Layer 2 — Weekly (noise filtering)**: Aggregate to weekly returns. Key technique: **3-year rolling window** (~156 weeks). Slide window by 1 week, compute mean return difference between category pairs at each window. Plot the difference time series. If the difference oscillates around zero, there's no stable effect.

```python
window = 156
diffs = []
for i in range(len(df_weekly) - window + 1):
    win = df_weekly.iloc[i:i+window]
    r1 = win[win['category']=='A']['return'].mean()
    r2 = win[win['category']=='B']['return'].mean()
    if not (np.isnan(r1) or np.isnan(r2)):
        diffs.append(r1 - r2)
```

**Layer 3 — Monthly (main battlefield)**: This is where overfitting is most dangerous. CRITICAL: split data chronologically (70% train / 30% test). Explore patterns ONLY on training set. Fix one hypothesis. Test on held-out set.

### Step 4: Sample-Out-of-Sample Validation

```python
n_train = int(len(df_monthly) * 0.7)
train = df_monthly.iloc[:n_train]
test = df_monthly.iloc[n_train:]

# Step A: On training set only, find the strongest pattern
train_means = train.groupby('category')['return'].mean()
best = train_means.idxmax()
worst = train_means.idxmin()
hypothesis = f"{best} > {worst}"

# Step B: On test set, verify the SAME direction holds
test_means = test.groupby('category')['return'].mean()
direction_ok = test_means[best] > test_means[worst]
# If direction_ok == False → overfitting detected
```

### Step 5: Confounding Variable Detection

Build three nested regression models:

| Model | Variables | Purpose |
|-------|-----------|---------|
| M1 | Category dummies only | Baseline explanatory power |
| M2 | M1 + Calendar month dummies | Does category survive calendar control? |
| M3 | M2 + Year dummies | Does category survive year fixed effects? |

If M1 is significant but category coefficients become insignificant in M2 → **category is just a calendar proxy**. This is the most common pathway for alternative hypotheses.

```python
import statsmodels.api as sm

# Model 2: category + calendar month
X = pd.get_dummies(all_data['category'], prefix='cat', drop_first=True)
X = pd.concat([X, pd.get_dummies(all_data['month_num'], prefix='m', drop_first=True)], axis=1)
X = sm.add_constant(X)
model = sm.OLS(y, X.astype(float)).fit(cov_type='HAC', cov_kwds={'maxlags': 3})

cat_cols = [c for c in model.params.index if c.startswith('cat_')]
any_significant = any(model.pvalues[c] < 0.05 for c in cat_cols if c in model.pvalues)
```

### Step 6: Robustness Checks

- **Winsorization**: Clip returns at 1%/99% and re-run all tests
- **Bonferroni correction**: If testing multiple hypotheses, adjust α threshold
- **Alternative aggregation**: Repeat weekly analysis using mode-based grouping instead of first-day

### .docx Paper Generation

After completing the analysis, generate a Word document with embedded figures for submission. **Organize all deliverables into a clean directory structure** before presenting the results to the user.

### Index Analysis Reusable Script

For testing indices (上证综合指数, 深证成指, 创业板指, 科创50, etc.), a dedicated script exists at the project level:

```
scripts/index_wuxing_analysis.py <ts_code> <display_name>
```

This script handles:
- Data loading from daily_quote + trade_calendar JOIN
- 12 Kruskal-Wallis tests (日/周/月 × 天干/地支/五行干/五行支)
- OLS regression with calendar month controls
- Winsorization robustness check
- Full output: conclusion report, statistical tables, intermediate CSVs

**Data source for indices**: Since Tushare free tier (`20积分`) does not have `index_daily` API access, use akshare's `stock_zh_index_daily(symbol)` as primary source, or Sina Finance as fallback.

Example:
```bash
python3 scripts/index_wuxing_analysis.py 000001.SH 上证指数
```

### Index Visualization

For each index after analysis, generate 4 publication-quality charts using **kimi-k2.5** (not the parent agent's model). Kimi produces superior visual design:

```bash
# Let kimi write its own visualization code from scratch
hermes chat -q "
为[指数名]写一份出版级matplotlib可视化代码，数据在[路径]。
生成4幅图：
1. fig1_daily_boxplot.png - 日收益率按五行分组箱线图
2. fig2_weekly_rolling.png - 周五行分组滚动平均线
3. fig3_monthly.png - 月收益率柱状图按五行着色
4. fig4_summary_pvalues.png - 检验p值汇总条形图
" -m kimi-k2.5 --provider kimi-cn -t "terminal,file" -Q
```

**Visualization constraints**:
- **White background only** (用户明确要求不要暗色主题): use `BG_COLOR = 'white'`, `TEXT_COLOR = '#212529'`, `GRID_COLOR = '#DEE2E6'`
- **dpi=300** for print publication
- **Let kimi design from scratch** — do not provide a pre-written script; kimi's own layout and color choices produce better-looking charts
- After kimi writes the script, run it directly via `python3 generate_plots.py`

Generate exactly 4 charts with consistent styling (Noto Sans CJK JP for font, 300dpi, 150dpi preview):

1. **fig1**: `subplots(1,2)` — Daily boxplot by label (天干 + 地支), colored by category, with mean markers
2. **fig2**: `subplots(2,2)` — Rolling window difference time series (3yr = 156wks), plot the 4 most divergent category pairs
3. **fig3**: `subplots(1,2)` — Monthly train(70%)/test(30%) bar comparison, annotated with reversals (red "反转" labels)
4. **fig4**: `subplots(2,2)` — Summary panel: KDE distributions (top-left), weekly bar chart (top-right), cumulative return with split line (bottom-left), p-value bar chart (bottom-right, all 9 tests on one horizontal bar chart)

This 4-panel pattern is stock-agnostic — run after analysis_main.py by reading the generated CSV files.

### Single-Study Directory Structure

Each study lives in its own subdirectory named after the stock/topic:

```
研究主题名/
├── README.md                    # Study overview
├── 结论报告.md                   # One-page conclusive report
├── 学术论文_研究主题.docx         # Full paper (.docx, charts embedded)
├── 参考文献/                     # Saved academic references
│   └── references.md            # Full citation list (metaso-sourced)
├── 图表/                         # High-res figures (300dpi PNG)
│   ├── fig1_*.png
│   └── ...
├── 数据/                         # Intermediate CSV data
│   ├── data_daily.csv
│   └── ...
├── 统计表/                       # Statistical results tables
│   └── table_all_tests.csv
└── 脚本/                         # All scripts retained (not deleted)
    ├── analysis_main.py
    ├── visualizations_v3.py
    └── ...
```

- DO keep all intermediate scripts (user explicitly wants them preserved)
- DO organize references into a dedicated directory (references from metaso are valuable)
- DO NOT delete old script versions — they have reference value

### Multi-Study Consolidation

When multiple studies share the same hypothesis (e.g., 天干地支五行 tested across multiple stocks), consolidate them:

```
关于XX的研究/                          # Umbrella directory naming the hypothesis
├── README.md                         # Index: comparison table across all studies
│                                      # Lists each stock's data range, record count,
│                                      # key p-values, and overall conclusion
├── 股票A/                            # Single-study directory (structure above)
├── 股票B/
└── 股票C/
```

**Rules:**
- The umbrella README is the **only** place with the full comparison table and evidence chain.
- The project-level README (README.md at project root) must contain **only a brief reference link** to the umbrella directory — never inline research detail, result tables, or deliverable lists.
- Update the umbrella README whenever a new study is added to maintain the cross-study consistency narrative.
- Name the umbrella after the hypothesis being tested, not the individual stock (e.g., `关于五行的研究/`, not `农业银行研究/`).

### Prerequisites
```bash
pip install python-docx
```

### Workflow
1. Generate all charts first (save as .png, 300dpi)
2. Create a python-docx Document
3. Use `doc.add_picture(path, width=Inches(5.5))` to embed figures
4. Use `doc.add_heading()`, `doc.add_paragraph()`, and `doc.add_table()` for content
5. Use metaso MCP (`mcp_metaso_metaso_chat`) to search for relevant academic references (calendar effect, market anomalies, existing alternative hypothesis papers in Chinese/English)

### Example: .docx with embedded figures
```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
doc.add_heading('Title', level=0)
doc.add_paragraph('Abstract text...')

# Insert figure
doc.add_picture('fig1_daily_boxplot.png', width=Inches(5.5))
last_paragraph = doc.paragraphs[-1]
last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
caption = doc.add_paragraph('图1  日收益率按五行分组箱线图')
caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
caption.runs[0].font.size = Pt(9)

doc.save('paper.docx')
```

### Metaso for academic references
Use `mcp_metaso_metaso_chat` with search terms like `中国股市日历效应`, `天干地支择时`, `market calendar effect A-share`, etc. Metaso returns structured citations (authors, date, title, link) that can be formatted into the references section.

## Chinese Font Rendering in matplotlib

### ⚠️ CRITICAL: Avoid DroidSansFallback for charts with mixed CJK+Latin text

`/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf` covers CJK characters but **lacks basic Latin glyphs** (letters, numbers, %, (), etc.). Using it as the only font will render all ASCII text as empty boxes. This is the #1 cause of "Chinese characters show as squares" bugs.

### Correct approach: Use a font with BOTH CJK + Latin coverage

The recommended font is **Noto Sans CJK** (pre-installed on Ubuntu via `fonts-noto-cjk`). Set via `rcParams` with a proper Latin fallback:

```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'DejaVu Sans',
                                     'Arial Unicode MS', 'AR PL UMing CN']
plt.rcParams['axes.unicode_minus'] = False
```

This works because `Noto Sans CJK JP` has complete CJK Unified Ideographs AND full ASCII/Latin-1 character coverage. The DejaVu Sans fallback ensures any missing glyphs are handled gracefully.

### Verification

Always test before generating full figures:

```python
fig, ax = plt.subplots(figsize=(4,1))
ax.text(0.5, 0.5, '测试中文Test123%()', ha='center', va='center', fontsize=14)
fig.savefig('/tmp/font_verify.png', dpi=72)
# Open the file visually — if any characters render as boxes, pick a different font
```

### Available CJK fonts on Ubuntu

```bash
$ fc-list :lang=zh -f "%{family}\n"
# Noto Sans CJK JP       ← BEST: full CJK + Latin, pre-installed
# AR PL UKai CN           ← OK: CJK + Latin, Kai style
# AR PL UMing CN          ← OK: CJK + Latin, Ming style
# Droid Sans Fallback     ← AVOID: CJK only, no Latin glyphs
```

### Fallback: using FontProperties (only if rcParams approach fails)

If for some reason the rcParams approach doesn't work, use FontProperties **with Noto Sans CJK** (NOT DroidSansFallback):

```python
from matplotlib.font_manager import FontProperties
zh_font = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')

ax.set_title('中文标题', fontproperties=zh_font)
ax.set_xlabel('中文标签', fontproperties=zh_font)
for label in ax.get_xticklabels():
    label.set_fontproperties(zh_font)
```

**Related companion skill**: `publication-quality-charts` (data-science category) — a dedicated, standalone skill for generating Nature/Science-style charts from pandas DataFrames. It covers the same visualization workflow but without the hypothesis-testing context, making it reusable for any data visualization task. For pure charting tasks (no statistical analysis), use that skill instead.

A minimal starter script that validates font rendering and sets up matplotlib for mixed CJK/Latin charting. Use `skill_view(name='alternative-hypothesis-testing', file_path='templates/chinese-charting-bootstrap.py')` to load it.

### Available template: templates/generate-paper-docx.py

A reusable starter script for generating a Word document with embedded statistical figures and formatted academic references. Edit the OUTPUT_DIR and data paths, then run.

## Common Pitfalls

1. **Data mining / multiple comparison**: If you test 20 category pairs, expect 1 to be "significant" at α=0.05 by chance. Apply Bonferroni correction (α/n).
2. **Survivorship bias**: The stock exists today — but that doesn't make the non-standard factor predictive.
3. **Post-diction vs prediction**: Finding patterns in full-sample analysis is data mining. Only the train/test split provides honest out-of-sample evidence.
4. **Confusing correlation with calendar effect**: If a label system is derived from the calendar (like 天干地支), it mathematically MUST correlate with months. Always run the M2 regression.
5. **P-hacking through frequency selection**: Results might look significant at one frequency but not others. The three-layer framework prevents this.
6. **Looking at the test set before fixing the hypothesis**: This invalidates the entire validation. Fix your hypothesis on training data, THEN look at test data.
7. **Putting research detail in the project README**: The project root README should only contain a brief reference link to the research umbrella directory. Inline p-values, deliverable lists, figure paths, and methodology explanations bloat the README and create a maintenance burden — every new study requires re-editing the same section. Keep the narrative in the umbrella README; the project README just points there.
8. **Siloed parallel studies on the same hypothesis**: When testing the same hypothesis on different stocks, do not scatter them in separate root-level directories (`A研究/`, `B研究/`). Consolidate under one umbrella with a comparison index. This makes the cross-study consistency narrative (e.g., "three independent samples all null") immediately visible rather than buried across unrelated folders.

## Reporting Template

### Conclusion Statement

**[DEFINITIVE / NULL]**: The alternative hypothesis shows [no / weak / strong] evidence of predictive power for [STOCK] over [PERIOD].

### Evidence Chain (exactly 5 items)

1. Daily frequency: KW test p=XXX — [significant / not significant]
2. Weekly rolling window: pair differences oscillate around zero / drift persistently
3. Monthly train/test: best pattern [survives / reverses] in test set
4. Regression: category [survives / disappears] after calendar month controls
5. Robustness: winsorized results [confirm / contradict] main findings

## Files

- `references/agricultural-bank-ganzhi-session.md` — Full session reference with exact results from the Agricultural Bank × 天干地支五行 test (all 9 KW tests, regression evidence, SQL patterns)
- `references/wuliangye-ganzhi-session.md` — Second application to 五粮液(000858.SZ), same methodology, same null result. Quick-reference for multi-stock comparative analysis.
- `references/catl-ganzhi-session.md` — Third application to 宁德时代(300750.SZ), shorter sample (~8yr), 2/9 nominally significant but overfitted. Completes the three-stock trilogy.
- `references/four-index-ganzhi-session.md` — Fourth application to 上证指数/深证成指/创业板指/科创50 (2026-05-14). All four indices null — 0/12 significant each. Documents akshare data source for indices when Tushare free tier lacks index_daily access, and kimi-k2.5 visualization workflow with white-background preference.
- `templates/three-layer-analysis.py` — Reusable analysis template (edit STOCK_CODE and LABEL_MAP)
- `templates/generate-paper-docx.py` — Word document generator with embedded figures and formatted references (includes metaso reference workflow)
- `templates/chinese-charting-bootstrap.py` — Minimal matplotlib CJK font setup test (run before generating production charts)
