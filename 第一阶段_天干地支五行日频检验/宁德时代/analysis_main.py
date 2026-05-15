#!/usr/bin/env python3
"""
宁德时代 (300750.SZ) 股价与天干地支五行关系检验 - 完整分析管道
三层分析：日频 → 周频 → 月频 (含样本外验证)
方法论完全遵循农业银行(601288.SH)研究框架
"""

import pymysql
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============ 配置 ============
DB_CONFIG = {
    'host': '192.168.31.29', 'port': 3306, 'user': 'finance_user',
    'password': 'Finance2026!', 'database': 'china_finance_db', 'charset': 'utf8mb4'
}
OUTPUT_DIR = '/home/cpy/文档/金融数据库建立/研究结果/宁德时代'
STOCK_CODE = '300750.SZ'
STOCK_NAME = '宁德时代'

# 五行映射
TIAN_GAN_WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火',
                    '戊': '土', '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
DI_ZHI_WUXING = {'子': '水', '丑': '土', '寅': '木', '卯': '木',
                  '辰': '土', '巳': '火', '午': '火', '未': '土',
                  '申': '金', '酉': '金', '戌': '土', '亥': '水'}
TIAN_GAN_LIST = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DI_ZHI_LIST = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

print("=" * 60)
print(f"{STOCK_NAME} ({STOCK_CODE}) 股价 × 天干地支五行关系检验")
print("=" * 60)

# ============ Phase 1: 数据提取 ============
print("\n[Phase 1] 提取数据...")
conn = pymysql.connect(**DB_CONFIG)

sql = """
SELECT 
    d.证券代码 AS ts_code,
    d.交易日期 AS trade_date,
    d.收盘价 AS close_price,
    d.前收盘 AS pre_close,
    d.涨跌幅 AS pct_chg,
    d.成交量 AS volume,
    d.成交额 AS amount,
    c.年干支 AS year_ganzhi,
    c.月干支 AS month_ganzhi,
    c.日干支 AS day_ganzhi,
    c.星期几 AS weekday,
    c.年份 AS year,
    c.月份 AS month,
    c.是否交易日 AS is_trading_day
FROM daily_quote d
JOIN trade_calendar c ON d.交易日期 = c.交易日期
WHERE d.证券代码 = %s AND c.是否交易日 = 1
ORDER BY d.交易日期
"""
df = pd.read_sql(sql, conn, params=(STOCK_CODE,), parse_dates=['trade_date'])
conn.close()

print(f"  原始数据: {len(df)} 条, {df['trade_date'].min()} ~ {df['trade_date'].max()}")

# ============ Phase 2: 特征工程 ============
print("\n[Phase 2] 特征工程...")

# 日度对数收益率
# DB涨跌幅已经是十进制小数（如0.006493 = +0.65%），但保险起见我们用收盘价计算
df['log_return'] = np.log(df['close_price'] / df['pre_close'])
df['direction'] = (df['log_return'] > 0).astype(int)

# 日天干五行
df['day_tian_gan'] = df['day_ganzhi'].str[0]
df['day_di_zhi'] = df['day_ganzhi'].str[1]
df['day_tg_wuxing'] = df['day_tian_gan'].map(TIAN_GAN_WUXING)
df['day_dz_wuxing'] = df['day_di_zhi'].map(DI_ZHI_WUXING)

# 月干支
df['month_tian_gan'] = df['month_ganzhi'].str[0]
df['month_di_zhi'] = df['month_ganzhi'].str[1]
df['month_tg_wuxing'] = df['month_tian_gan'].map(TIAN_GAN_WUXING)
df['month_dz_wuxing'] = df['month_di_zhi'].map(DI_ZHI_WUXING)

# 控制变量
df['is_month_start'] = df['trade_date'].dt.day <= 5
df['is_month_end'] = df['trade_date'].dt.day >= (df['trade_date'].dt.days_in_month - 4)
df['prev_log_return'] = df['log_return'].shift(1)

# 周频聚合
print("\n  聚合周频数据...")
df['week_number'] = df['trade_date'].dt.isocalendar().year.astype(str) + '-W' + df['trade_date'].dt.isocalendar().week.astype(str).str.zfill(2)

weekly_data = []
for wk, grp in df.groupby('week_number', sort=True):
    first_day = grp.iloc[0]
    weekly_data.append({
        'week_number': wk,
        'week_start': first_day['trade_date'],
        'week_end': grp['trade_date'].iloc[-1],
        'week_return': np.log(grp['close_price'].iloc[-1] / grp['close_price'].iloc[0]),
        'week_tg_wuxing': first_day['day_tg_wuxing'],  # 周一的天干
        'week_dz_wuxing': first_day['day_dz_wuxing'],  # 周一的地支
        'week_tg_mode': grp['day_tg_wuxing'].mode().iloc[0] if not grp['day_tg_wuxing'].mode().empty else first_day['day_tg_wuxing'],
        'week_volatility': grp['log_return'].std(),
        'week_abs_return': grp['log_return'].abs().mean(),
    })
df_weekly = pd.DataFrame(weekly_data)
print(f"  周频数据: {len(df_weekly)} 周")

# 月频聚合 (按阳历月份)
print("\n  聚合月频数据...")
df['year_month'] = df['trade_date'].dt.to_period('M').astype(str)

monthly_data = []
for ym, grp in df.groupby('year_month', sort=True):
    first_day = grp.iloc[0]
    monthly_data.append({
        'year_month': ym,
        'month_start': first_day['trade_date'],
        'month_end': grp['trade_date'].iloc[-1],
        'year': first_day['year'],
        'month_num': first_day['month'],
        'month_return': np.log(grp['close_price'].iloc[-1] / grp['close_price'].iloc[0]),
        'month_abs_return': grp['log_return'].abs().mean(),
        'month_volatility': grp['log_return'].std(),
        'month_tg_wuxing': first_day['month_tg_wuxing'],
        'month_dz_wuxing': first_day['month_dz_wuxing'],
        'month_ganzhi': first_day['month_ganzhi'],
        'n_trading_days': len(grp),
    })
df_monthly = pd.DataFrame(monthly_data)
print(f"  月频数据: {len(df_monthly)} 个月")

# ============ 保存中间数据 ============
df.to_csv(f'{OUTPUT_DIR}/data_daily.csv', index=False, encoding='utf-8-sig')
df_weekly.to_csv(f'{OUTPUT_DIR}/data_weekly.csv', index=False, encoding='utf-8-sig')
df_monthly.to_csv(f'{OUTPUT_DIR}/data_monthly.csv', index=False, encoding='utf-8-sig')
print(f"\n  数据已保存至: {OUTPUT_DIR}/")

# ============ Phase 2: 日频分析 ============
print("\n" + "=" * 60)
print("[Phase 2] 日频分析")
print("=" * 60)

from scipy.stats import kruskal

# 日天干五行分组统计
print("\n--- 日天干五行分组 ---")
tg_groups = df.groupby('day_tg_wuxing')['log_return'].agg(['mean', 'std', 'median', 'count', lambda x: (x>0).mean()])
tg_groups.columns = ['均值', '标准差', '中位数', '天数', '上涨占比']
tg_groups['均值%'] = tg_groups['均值'] * 100
tg_groups['标准差%'] = tg_groups['标准差'] * 100
print(tg_groups.round(6).to_string())

# Kruskal-Wallis 检验
groups_tg = [g['log_return'].values for _, g in df.groupby('day_tg_wuxing')]
h_tg, p_tg = kruskal(*groups_tg)
print(f"\nKruskal-Wallis 检验 (日天干五行): H={h_tg:.4f}, p={p_tg:.6f}")

# 日地支五行分组
print("\n--- 日地支五行分组 ---")
dz_groups = df.groupby('day_dz_wuxing')['log_return'].agg(['mean', 'std', 'median', 'count', lambda x: (x>0).mean()])
dz_groups.columns = ['均值', '标准差', '中位数', '天数', '上涨占比']
dz_groups['均值%'] = dz_groups['均值'] * 100
dz_groups['标准差%'] = dz_groups['标准差'] * 100
print(dz_groups.round(6).to_string())

groups_dz = [g['log_return'].values for _, g in df.groupby('day_dz_wuxing')]
h_dz, p_dz = kruskal(*groups_dz)
print(f"\nKruskal-Wallis 检验 (日地支五行): H={h_dz:.4f}, p={p_dz:.6f}")

# 描述统计表保存
tg_groups.round(6).to_csv(f'{OUTPUT_DIR}/table_daily_tg_wuxing.csv', encoding='utf-8-sig')
dz_groups.round(6).to_csv(f'{OUTPUT_DIR}/table_daily_dz_wuxing.csv', encoding='utf-8-sig')

# ============ Phase 3: 周频分析 ============
print("\n" + "=" * 60)
print("[Phase 3] 周频分析")
print("=" * 60)

# 周天干五行分组
print("\n--- 周天干五行分组 ---")
wk_tg = df_weekly.groupby('week_tg_wuxing')['week_return'].agg(['mean', 'std', 'median', 'count', lambda x: (x>0).mean()])
wk_tg.columns = ['均值', '标准差', '中位数', '周数', '上涨占比']
wk_tg['均值%'] = wk_tg['均值'] * 100
print(wk_tg.round(6).to_string())

groups_wk_tg = [g['week_return'].values for _, g in df_weekly.groupby('week_tg_wuxing')]
hw_tg, pw_tg = kruskal(*groups_wk_tg)
print(f"\nKruskal-Wallis (周天干五行): H={hw_tg:.4f}, p={pw_tg:.6f}")

# 周地支五行分组
print("\n--- 周地支五行分组 ---")
wk_dz = df_weekly.groupby('week_dz_wuxing')['week_return'].agg(['mean', 'std', 'median', 'count', lambda x: (x>0).mean()])
wk_dz.columns = ['均值', '标准差', '中位数', '周数', '上涨占比']
wk_dz['均值%'] = wk_dz['均值'] * 100
print(wk_dz.round(6).to_string())

groups_wk_dz = [g['week_return'].values for _, g in df_weekly.groupby('week_dz_wuxing')]
hw_dz, pw_dz = kruskal(*groups_wk_dz)
print(f"\nKruskal-Wallis (周地支五行): H={hw_dz:.4f}, p={pw_dz:.6f}")

# 滚动窗口检验 (3年 ≈ 156周)
print("\n--- 滚动窗口检验 (3年滚动) ---")
window = min(156, len(df_weekly) // 2)  # 如果数据不足156周，取一半
print(f"  滚动窗口大小: {window} 周")
wuxing_pairs = []
for wx1 in ['金', '木', '水', '火', '土']:
    for wx2 in ['金', '木', '水', '火', '土']:
        if wx1 < wx2:
            roll_diffs = []
            for i in range(len(df_weekly) - window + 1):
                win = df_weekly.iloc[i:i+window]
                r1 = win[win['week_tg_wuxing']==wx1]['week_return'].mean()
                r2 = win[win['week_tg_wuxing']==wx2]['week_return'].mean()
                if not (np.isnan(r1) or np.isnan(r2)):
                    roll_diffs.append(r1 - r2)
            if roll_diffs:
                mean_diff = np.mean(roll_diffs)
                std_diff = np.std(roll_diffs)
                t_stat = mean_diff / (std_diff / np.sqrt(len(roll_diffs))) if std_diff > 0 else 0
                wuxing_pairs.append({
                    'pair': f'{wx1}-{wx2}',
                    'mean_diff_bps': mean_diff * 10000,
                    'std_diff_bps': std_diff * 10000,
                    't_stat': t_stat,
                    'n_windows': len(roll_diffs)
                })

df_roll = pd.DataFrame(wuxing_pairs)
print(df_roll.round(4).to_string())
df_roll.to_csv(f'{OUTPUT_DIR}/table_weekly_rolling.csv', index=False, encoding='utf-8-sig')

# 找出差异最大的组合
max_pair = df_roll.loc[df_roll['mean_diff_bps'].abs().idxmax()]
print(f"\n最大周收益差异组合: {max_pair['pair']} = {max_pair['mean_diff_bps']:.2f} bps")

# ============ Phase 4: 月频分析（主战场） ============
print("\n" + "=" * 60)
print("[Phase 4] 月频分析 - 主战场")
print("=" * 60)

# 按时间对半切分: 70% train, 30% test
n_total = len(df_monthly)
n_train = int(n_total * 0.7)
train = df_monthly.iloc[:n_train].copy()
test = df_monthly.iloc[n_train:].copy()

print(f"\n训练集: {len(train)} 个月 ({train['month_start'].min()} ~ {train['month_start'].max()})")
print(f"测试集: {len(test)} 个月 ({test['month_start'].min()} ~ {test['month_start'].max()})")

# === 步骤一：训练集探索 ===
print("\n--- 步骤一：训练集探索 ---")

# 月天干五行
print("\n  月天干五行分组 (训练集):")
m_tg = train.groupby('month_tg_wuxing')['month_return'].agg(['mean', 'std', 'count', lambda x: (x>0).mean()])
m_tg.columns = ['均值', '标准差', '月数', '上涨占比']
m_tg['均值%'] = m_tg['均值'] * 100
print(m_tg.round(6).to_string())

# 月地支五行
print("\n  月地支五行分组 (训练集):")
m_dz = train.groupby('month_dz_wuxing')['month_return'].agg(['mean', 'std', 'count', lambda x: (x>0).mean()])
m_dz.columns = ['均值', '标准差', '月数', '上涨占比']
m_dz['均值%'] = m_dz['均值'] * 100
print(m_dz.round(6).to_string())

# Kruskal-Wallis 训练集
groups_m_tg = [g['month_return'].values for _, g in train.groupby('month_tg_wuxing')]
groups_m_dz = [g['month_return'].values for _, g in train.groupby('month_dz_wuxing')]
hm_tg, pm_tg = kruskal(*groups_m_tg) if len(groups_m_tg) > 1 else (0, 1)
hm_dz, pm_dz = kruskal(*groups_m_dz) if len(groups_m_dz) > 1 else (0, 1)
print(f"\nKruskal-Wallis (月天干 训练集): H={hm_tg:.4f}, p={pm_tg:.6f}")
print(f"Kruskal-Wallis (月地支 训练集): H={hm_dz:.4f}, p={pm_dz:.6f}")

# 检查四库月 (辰戌丑未)
print("\n  四库月 vs 非四库月 (训练集):")
train['is_siku'] = train['month_dz_wuxing'] == '土'
siku_groups = train.groupby('is_siku')['month_return'].agg(['mean', 'std', 'count', lambda x: (x>0).mean()])
siku_groups.columns = ['均值', '标准差', '月数', '上涨占比']
siku_groups['均值%'] = siku_groups['均值'] * 100
print(siku_groups.round(6).to_string())

# 天干地支组合效应
print("\n  天干×地支组合 (训练集, 月均涨幅):")
train['tg_dz_combo'] = train['month_tg_wuxing'] + '+' + train['month_dz_wuxing']
combo_stats = train.groupby('tg_dz_combo')['month_return'].agg(['mean', 'count'])
combo_stats = combo_stats[combo_stats['count'] >= 2].sort_values('mean', ascending=False)
print(combo_stats.round(6).to_string())

# 找到训练集最强规律
train_means = train.groupby('month_tg_wuxing')['month_return'].mean()
best_tg = train_means.idxmax()
worst_tg = train_means.idxmin()
hypothesis = f"月天干为{best_tg}的月份跑赢月天干为{worst_tg}的月份"
print(f"\n  → 训练集最强规律: {hypothesis}")
print(f"     最佳({best_tg}): {train_means[best_tg]*100:.3f}% vs 最差({worst_tg}): {train_means[worst_tg]*100:.3f}%")

# 也检查地支
train_dz_means = train.groupby('month_dz_wuxing')['month_return'].mean()
best_dz = train_dz_means.idxmax()
worst_dz = train_dz_means.idxmin()

# === 步骤二：测试集验证 ===
print("\n--- 步骤二：测试集验证 ---")

test_means = test.groupby('month_tg_wuxing')['month_return'].mean()
print(f"\n  月天干五行 (测试集):")
for wx in ['金','木','水','火','土']:
    if wx in test_means:
        print(f"    {wx}: {test_means[wx]*100:.4f}%")

# 验证训练集最强规律
if best_tg in test_means and worst_tg in test_means:
    best_test = test_means[best_tg]
    worst_test = test_means[worst_tg]
    direction_ok = best_test > worst_test
    print(f"\n  验证: {best_tg} vs {worst_tg}")
    print(f"    训练集: {train_means[best_tg]*100:.4f}% vs {train_means[worst_tg]*100:.4f}%")
    print(f"    测试集: {best_test*100:.4f}% vs {worst_test*100:.4f}%")
    print(f"    方向一致: {'✅' if direction_ok else '❌'}")
else:
    direction_ok = False
    print(f"\n  {best_tg}或{worst_tg}在测试集无数据，无法验证")

# 测试集 Kruskal-Wallis
groups_m_tg_test = [g['month_return'].values for _, g in test.groupby('month_tg_wuxing')]
groups_m_dz_test = [g['month_return'].values for _, g in test.groupby('month_dz_wuxing')]
hm_tg_test, pm_tg_test = kruskal(*groups_m_tg_test) if len(groups_m_tg_test) > 1 else (0, 1)
hm_dz_test, pm_dz_test = kruskal(*groups_m_dz_test) if len(groups_m_dz_test) > 1 else (0, 1)
print(f"\nKruskal-Wallis (月天干 测试集): H={hm_tg_test:.4f}, p={pm_tg_test:.6f}")
print(f"Kruskal-Wallis (月地支 测试集): H={hm_dz_test:.4f}, p={pm_dz_test:.6f}")

# === 步骤三：剥离混杂效应 ===
print("\n--- 步骤三：剥离混杂效应 ---")

import statsmodels.api as sm

# 回归：月收益率 ~ 月天干五行 + 阳历月份 + 年份
all_data = pd.concat([train, test], axis=0)

# 回归1: 仅月天干五行
X1 = pd.get_dummies(all_data['month_tg_wuxing'], prefix='tg', drop_first=True)
X1 = sm.add_constant(X1)
y = all_data['month_return'].values
try:
    model1 = sm.OLS(y, X1.astype(float)).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
    print(f"\n  回归1 (仅月天干五行):")
    print(f"    R²={model1.rsquared:.4f}, Adj.R²={model1.rsquared_adj:.4f}")
    print(f"    F-test p={model1.f_pvalue:.6f}")
except Exception as e:
    print(f"\n  回归1 失败: {e}")
    model1 = None

# 回归2: 月天干五行 + 阳历月份
X2 = pd.get_dummies(all_data['month_tg_wuxing'], prefix='tg', drop_first=True)
X2 = pd.concat([X2, pd.get_dummies(all_data['month_num'], prefix='m', drop_first=True)], axis=1)
X2 = sm.add_constant(X2)
try:
    model2 = sm.OLS(y, X2.astype(float)).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
    print(f"\n  回归2 (月天干 + 阳历月份):")
    print(f"    R²={model2.rsquared:.4f}, Adj.R²={model2.rsquared_adj:.4f}")
    print(f"    F-test p={model2.f_pvalue:.6f}")
except Exception as e:
    print(f"\n  回归2 失败: {e}")
    model2 = None

# 回归3: 月天干五行 + 阳历月份 + 年份
try:
    year_dummies = pd.get_dummies(all_data['year'].astype(str), prefix='y', drop_first=True)
    X3 = pd.get_dummies(all_data['month_tg_wuxing'], prefix='tg', drop_first=True)
    X3 = pd.concat([X3, pd.get_dummies(all_data['month_num'], prefix='m', drop_first=True), year_dummies], axis=1)
    X3 = sm.add_constant(X3)
    model3 = sm.OLS(y, X3.astype(float)).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
    print(f"\n  回归3 (月天干 + 阳历月份 + 年份):")
    print(f"    R²={model3.rsquared:.4f}, Adj.R²={model3.rsquared_adj:.4f}")
    print(f"    F-test p={model3.f_pvalue:.6f}")
except Exception as e:
    print(f"\n  回归3 失败: {e}")
    model3 = None

# 判断五行是否只是阳历月份的代理
if model2 is not None:
    tg_cols = [c for c in model2.params.index if c.startswith('tg_')]
    any_tg_sig = any(model2.pvalues[c] < 0.05 for c in tg_cols if c in model2.pvalues)
    print(f"\n  五行变量在回归2中仍然显著: {'✅ 是 (五行有独立解释力)' if any_tg_sig else '❌ 否 (五行可能是阳历的代理)'}")
else:
    any_tg_sig = False
    print("\n  回归2失败，无法判断代理效应")

# ============ 稳健性检验 ============
print("\n" + "=" * 60)
print("[Robustness] 稳健性检验")
print("=" * 60)

# 缩尾处理 (1%和99%)
df['log_return_winsor'] = df['log_return'].clip(
    lower=df['log_return'].quantile(0.01),
    upper=df['log_return'].quantile(0.99)
)

# 重新做日频检验
groups_w = [g['log_return_winsor'].values for _, g in df.groupby('day_tg_wuxing')]
hw_tg_w, pw_tg_w = kruskal(*groups_w)
print(f"\n缩尾后 Kruskal-Wallis (日天干): H={hw_tg_w:.4f}, p={pw_tg_w:.6f}")

# ============ 保存完整检验结果 ============
results_summary = {
    '阶段': ['日频-天干', '日频-地支', '周频-天干', '周频-地支',
             '月频-天干(训练)', '月频-地支(训练)', '月频-天干(测试)', '月频-地支(测试)',
             '稳健性-缩尾日天干'],
    'H统计量': [h_tg, h_dz, hw_tg, hw_dz, hm_tg, hm_dz, hm_tg_test, hm_dz_test, hw_tg_w],
    'p值': [p_tg, p_dz, pw_tg, pw_dz, pm_tg, pm_dz, pm_tg_test, pm_dz_test, pw_tg_w],
    '显著(α=0.05)': [p < 0.05 for p in [p_tg, p_dz, pw_tg, pw_dz, pm_tg, pm_dz, pm_tg_test, pm_dz_test, pw_tg_w]]
}
df_results = pd.DataFrame(results_summary)
df_results.to_csv(f'{OUTPUT_DIR}/table_all_tests.csv', index=False, encoding='utf-8-sig')
print(f"\n  检验结果表已保存")

# ============ 最终结论 ============
print("\n" + "=" * 60)
print("[Conclusion] 初步结论")
print("=" * 60)

n_sig = sum(df_results['显著(α=0.05)'])
print(f"\n  共 {len(df_results)} 个检验, {n_sig} 个显著 (α=0.05)")
print(f"  日频: p_tg={p_tg:.6f}, p_dz={p_dz:.6f}")
print(f"  周频: p_tg={pw_tg:.6f}, p_dz={pw_dz:.6f}")
print(f"  月频(训练): p_tg={pm_tg:.6f}, p_dz={pm_dz:.6f}")
print(f"  月频(测试): p_tg={pm_tg_test:.6f}, p_dz={pm_dz_test:.6f}")
print(f"  样本外方向一致: {'✅' if direction_ok else '❌'}")

print(f"\n  === 基础分析完成 ===")
print(f"  中间数据保存在: {OUTPUT_DIR}/")
