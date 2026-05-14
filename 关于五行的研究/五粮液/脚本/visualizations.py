#!/usr/bin/env python3
"""
可视化：五粮液(000858.SZ) × 天干地支五行
4张图：日频箱线图 / 周频滚动窗口 / 月频训练测试对比 / 汇总面板
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ===== 字体设置 =====
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'Noto Sans CJK SC',
                                     'DejaVu Sans', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['figure.figsize'] = (10, 6)

OUTPUT_DIR = '/home/cpy/文档/金融数据库建立/五粮液研究'

df = pd.read_csv(f'{OUTPUT_DIR}/数据/data_daily_with_ganzhi.csv', parse_dates=['trade_date'])
df_weekly = pd.read_csv(f'{OUTPUT_DIR}/数据/data_weekly.csv')
df_monthly = pd.read_csv(f'{OUTPUT_DIR}/数据/data_monthly.csv')
df_tests = pd.read_csv(f'{OUTPUT_DIR}/统计表/table_all_tests.csv')

colors = {'金': '#FFD700', '木': '#228B22', '水': '#4169E1', '火': '#FF4500', '土': '#8B4513'}
wx_order = ['金', '木', '水', '火', '土']
STOCK_NAME = '五粮液(000858.SZ)'

# ============ Fig 1: 日频箱线图 ============
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 日天干
ax = axes[0]
bp_data = [df[df['day_tg_wuxing']==wx]['log_return'].values * 100 for wx in wx_order]
bp = ax.boxplot(bp_data, labels=wx_order, patch_artist=True,
                showmeans=True, meanprops=dict(marker='D', markerfacecolor='red', markersize=5))
for patch, label in zip(bp['boxes'], wx_order):
    patch.set_facecolor(colors.get(label, '#999999'))
    patch.set_alpha(0.6)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_title('日收益率 × 天干五行', fontsize=13, fontweight='bold')
ax.set_xlabel('天干五行', fontsize=11)
ax.set_ylabel('日收益率 (%)', fontsize=11)

# 日地支
ax = axes[1]
bp_data = [df[df['day_dz_wuxing']==wx]['log_return'].values * 100 for wx in wx_order]
bp = ax.boxplot(bp_data, labels=wx_order, patch_artist=True,
                showmeans=True, meanprops=dict(marker='D', markerfacecolor='red', markersize=5))
for patch, label in zip(bp['boxes'], wx_order):
    patch.set_facecolor(colors.get(label, '#999999'))
    patch.set_alpha(0.6)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_title('日收益率 × 地支五行', fontsize=13, fontweight='bold')
ax.set_xlabel('地支五行', fontsize=11)
ax.set_ylabel('日收益率 (%)', fontsize=11)

fig.suptitle(f'{STOCK_NAME} 2010-2026 日收益率按五行分组分布', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/图表/fig1_daily_boxplot.png', dpi=300)
plt.close()
print("Fig 1 done")

# ============ Fig 2: 周频滚动窗口差异时序图 ============
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
colors2 = {'火-金': '#FF4500', '水-金': '#4169E1', '木-火': '#228B22', '土-火': '#8B4513'}
pairs_to_plot = ['火-金', '水-金', '木-火', '土-火']
window = 156

for ax, pair_name in zip(axes.flatten(), pairs_to_plot):
    wx1, wx2 = pair_name.split('-')
    diffs, dates = [], []
    for i in range(len(df_weekly) - window + 1):
        win = df_weekly.iloc[i:i+window]
        r1 = win[win['week_tg_wuxing']==wx1]['week_return'].mean()
        r2 = win[win['week_tg_wuxing']==wx2]['week_return'].mean()
        if not (np.isnan(r1) or np.isnan(r2)):
            diffs.append((r1 - r2) * 10000)
            dates.append(pd.to_datetime(win['week_start'].iloc[window//2]))
    ax.plot(dates, diffs, color=colors2.get(pair_name, '#333'), linewidth=0.8, alpha=0.8)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=np.mean(diffs), color='red', linestyle='-', alpha=0.6,
               label=f'均值={np.mean(diffs):.1f}bps')
    ax.set_title(f'{pair_name} 周均收益率差 (3年滚动)', fontsize=12, fontweight='bold')
    ax.set_xlabel('窗口中心日期', fontsize=10)
    ax.set_ylabel('收益率差 (bps)', fontsize=10)
    ax.legend(fontsize=9)

fig.suptitle(f'{STOCK_NAME} 五行分组周收益率 3年滚动窗口差异 (156周)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/图表/fig2_weekly_rolling.png', dpi=300)
plt.close()
print("Fig 2 done")

# ============ Fig 3: 月频 训练/测试 对比 ============
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

n_train = int(len(df_monthly) * 0.7)
df_monthly['period'] = ['训练集'] * n_train + ['测试集'] * (len(df_monthly) - n_train)

# 月天干
ax = axes[0]
train_means = df_monthly[df_monthly['period']=='训练集'].groupby('month_tg_wuxing')['month_return'].mean() * 100
test_means = df_monthly[df_monthly['period']=='测试集'].groupby('month_tg_wuxing')['month_return'].mean() * 100
train_vals = [train_means.get(w, 0) for w in wx_order]
test_vals = [test_means.get(w, 0) for w in wx_order]

x = np.arange(len(wx_order))
width = 0.35
ax.bar(x - width/2, train_vals, width, label='训练集', color='steelblue', alpha=0.8)
ax.bar(x + width/2, test_vals, width, label='测试集', color='coral', alpha=0.8)
ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
ax.set_xticks(x)
ax.set_xticklabels(wx_order)
ax.set_title('月收益率 × 天干五行: 训练集 vs 测试集', fontsize=12, fontweight='bold')
ax.set_ylabel('月均收益率 (%)', fontsize=11)
ax.legend(fontsize=10)
for w in wx_order:
    if train_means.get(w, 0) * test_means.get(w, 0) < 0:
        ax.annotate('反转', (wx_order.index(w), 0), textcoords="offset points",
                    xytext=(0, -22), ha='center', fontsize=10, color='red', fontweight='bold')

# 月地支
ax = axes[1]
train_means = df_monthly[df_monthly['period']=='训练集'].groupby('month_dz_wuxing')['month_return'].mean() * 100
test_means = df_monthly[df_monthly['period']=='测试集'].groupby('month_dz_wuxing')['month_return'].mean() * 100
train_vals = [train_means.get(w, 0) for w in wx_order]
test_vals = [test_means.get(w, 0) for w in wx_order]

ax.bar(x - width/2, train_vals, width, label='训练集', color='steelblue', alpha=0.8)
ax.bar(x + width/2, test_vals, width, label='测试集', color='coral', alpha=0.8)
ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
ax.set_xticks(x)
ax.set_xticklabels(wx_order)
ax.set_title('月收益率 × 地支五行: 训练集 vs 测试集', fontsize=12, fontweight='bold')
ax.set_ylabel('月均收益率 (%)', fontsize=11)
ax.legend(fontsize=10)
for w in wx_order:
    if train_means.get(w, 0) * test_means.get(w, 0) < 0:
        ax.annotate('反转', (wx_order.index(w), 0), textcoords="offset points",
                    xytext=(0, -22), ha='center', fontsize=10, color='red', fontweight='bold')

fig.suptitle(f'{STOCK_NAME} 月频样本外检验 — 训练集(70%) vs 测试集(30%)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/图表/fig3_monthly_train_test.png', dpi=300)
plt.close()
print("Fig 3 done")

# ============ Fig 4: 汇总四格图 ============
p_vals = dict(zip(df_tests['阶段'], df_tests['p值']))

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 左上: 日收益率分布
ax = axes[0, 0]
for wx in wx_order:
    subset = df[df['day_tg_wuxing'] == wx]['log_return'] * 100
    if len(subset) > 0:
        sns.kdeplot(subset, label=wx, color=colors.get(wx, '#999'), ax=ax, linewidth=1.5)
ax.set_xlabel('日收益率 (%)', fontsize=11)
ax.set_ylabel('密度', fontsize=11)
ax.set_title('日收益率分布 × 天干五行', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)

# 右上: 周收益柱状图
ax = axes[0, 1]
wk_means = df_weekly.groupby('week_tg_wuxing')['week_return'].mean() * 100
wk_vals = [wk_means.get(w, 0) for w in wx_order]
ax.bar(wx_order, wk_vals, color=[colors.get(w, '#999') for w in wx_order], alpha=0.8)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_title('周均收益率 × 天干五行', fontsize=12, fontweight='bold')
ax.set_ylabel('周均收益率 (%)', fontsize=11)

# 左下: 月收益时序 + 分界线
ax = axes[1, 0]
df_monthly['cum_return'] = (1 + df_monthly['month_return']).cumprod()
ax.plot(pd.to_datetime(df_monthly['month_start']), df_monthly['cum_return'], color='#333', linewidth=1)
ax.axvline(x=pd.to_datetime(df_monthly.iloc[n_train]['month_start']), color='red', linestyle='--', alpha=0.7, label='训练/测试分界')
ax.set_title(f'{STOCK_NAME} 月累计收益 (2010-2026)', fontsize=12, fontweight='bold')
ax.set_ylabel('累计净值', fontsize=11)
ax.legend(fontsize=9)
ax.axhline(y=1, color='gray', linestyle='-', alpha=0.3)

# 右下: p值汇总
ax = axes[1, 1]
test_names = ['日天干', '日地支', '周天干', '周地支', '月天干\\n(训练)', '月地支\\n(训练)', '月天干\\n(测试)', '月地支\\n(测试)', '稳健性\\n(缩尾)']
p_values = [p_vals.get(n, 1) for n in ['日频-天干', '日频-地支', '周频-天干', '周频-地支',
                                         '月频-天干(训练)', '月频-地支(训练)', '月频-天干(测试)',
                                         '月频-地支(测试)', '稳健性-缩尾日天干']]
colors_bar = ['#e74c3c' if p < 0.05 else '#95a5a6' for p in p_values]
ax.barh(range(len(test_names)), p_values, color=colors_bar)
ax.set_yticks(range(len(test_names)))
ax.set_yticklabels(test_names, fontsize=9)
ax.axvline(x=0.05, color='red', linestyle='--', alpha=0.7, label='α=0.05')
ax.set_xlabel('p值', fontsize=11)
ax.set_title('所有假设检验p值汇总', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.set_xlim(0, 1.0)
for i, p in enumerate(p_values):
    ax.text(p + 0.01, i, f'{p:.3f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/图表/fig4_summary_all.png', dpi=300)
plt.close()
print("Fig 4 done")

print("\n✅ 五粮液可视化完成！4张图已保存。")
