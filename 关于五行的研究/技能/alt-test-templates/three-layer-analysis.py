#!/usr/bin/env python3
"""
Template: Three-layer alternative hypothesis test for stock price data.
Usage: python3 template_analysis.py STOCK_CODE
Replaces STOCK_CODE, DB_CONFIG, and HYPOTHESIS_MAP with your parameters.
"""
import pymysql, pandas as pd, numpy as np, warnings
from scipy.stats import kruskal
import statsmodels.api as sm
warnings.filterwarnings('ignore')

# ======== CONFIG — EDIT FOR YOUR ANALYSIS ========
DB_CONFIG = {
    'host': '192.168.31.29', 'port': 3306, 'user': 'finance_user',
    'password': 'Finance2026!', 'database': 'china_finance_db', 'charset': 'utf8mb4'
}
STOCK_CODE = '601288.SH'  # ← change this
OUTPUT_DIR = '/home/cpy/文档/金融数据库建立/研究结果'

# Hypothesis-specific mapping (edit for your labeling system)
LABEL_MAP = {
    '甲': 'A', '乙': 'B', '丙': 'C', '丁': 'D', '戊': 'E',
    '己': 'F', '庚': 'G', '辛': 'H', '壬': 'I', '癸': 'J'
}
# ==================================================

print(f"Analyzing {STOCK_CODE}...")

# Step 1: Extract data
conn = pymysql.connect(**DB_CONFIG)
sql = """
SELECT d.交易日期 AS trade_date, d.收盘价 AS close_price, d.前收盘 AS pre_close,
       d.涨跌幅 AS pct_chg, c.日干支 AS day_label, c.星期几 AS weekday,
       c.年份 AS year, c.月份 AS month
FROM daily_quote d JOIN trade_calendar c ON d.交易日期 = c.交易日期
WHERE d.证券代码 = %s AND c.是否交易日 = 1 ORDER BY d.交易日期
"""
df = pd.read_sql(sql, conn, params=(STOCK_CODE,), parse_dates=['trade_date'])
conn.close()

# Step 2: Feature engineering
df['log_return'] = np.log(df['close_price'] / df['pre_close'])
df['category'] = df['day_label'].str[0].map(LABEL_MAP).fillna('OTHER')
df['direction'] = (df['log_return'] > 0).astype(int)
df['prev_return'] = df['log_return'].shift(1)

# Step 3: Daily analysis
groups = [g['log_return'].values for _, g in df.groupby('category')]
h, p = kruskal(*groups) if len(groups) > 1 else (0, 1.0)
print(f"Daily KW test: H={h:.4f}, p={p:.6f}")

# Step 4: Monthly aggregation
df['year_month'] = df['trade_date'].dt.to_period('M').astype(str)
monthly = df.groupby('year_month', sort=True).agg(
    month_start=('trade_date', 'first'),
    close_price=('close_price', lambda x: np.log(x.iloc[-1]/x.iloc[0])),
    category=('category', 'first'),
    month=('month', 'first'),
    year=('year', 'first')
).rename(columns={'close_price': 'month_return'})

# Step 5: Train/test (70/30 chronological split)
n_train = int(len(monthly) * 0.7)
train, test = monthly.iloc[:n_train], monthly.iloc[n_train:]

# Step 6: Regression with calendar control
all_data = pd.concat([train, test], axis=0)
X = pd.get_dummies(all_data['category'], prefix='cat', drop_first=True)
X = pd.concat([X, pd.get_dummies(all_data['month'], prefix='m', drop_first=True)], axis=1)
X = sm.add_constant(X)
model = sm.OLS(all_data['month_return'].values, X.astype(float)).fit(cov_type='HAC', cov_kwds={'maxlags': 3})

cat_cols = [c for c in model.params.index if c.startswith('cat_')]
any_sig = any(model.pvalues[c] < 0.05 for c in cat_cols if c in model.pvalues)

print(f"Regression R²={model.rsquared:.4f}, category survives calendar: {any_sig}")
print(f"FINAL CONCLUSION: {'Pattern found' if any_sig else 'No evidence of relationship'}")
