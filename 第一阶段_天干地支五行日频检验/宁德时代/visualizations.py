#!/usr/bin/env python3
"""
可视化：宁德时代(300750.SZ) × 天干地支五行
生成4张核心图表 (300dpi)
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

plt.rcParams.update({
    'font.sans-serif': ['Noto Sans CJK SC', 'Noto Sans CJK JP', 'WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans'],
    'axes.unicode_minus': False,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'figure.figsize': (10, 6)
})

OUTPUT_DIR = '/home/cpy/文档/金融数据库建立/研究结果/宁德时代'

# Load data
df = pd.read_csv(f'{OUTPUT_DIR}/data_daily.csv', parse_dates=['trade_date'])
df_weekly = pd.read_csv(f'{OUTPUT_DIR}/data_weekly.csv')
df_monthly = pd.read_csv(f'{OUTPUT_DIR}/data_monthly.csv')
df_results = pd.read_csv(f'{OUTPUT_DIR}/table_all_tests.csv')

print(f"Loaded: daily={len(df)}, weekly={len(df_weekly)}, monthly={len(df_monthly)}")

# ============ Fig 1: 日频箱线图 ============
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
colors = {'金': '#FFD700', '木': '#228B22', '水': '#4169E1', '火': '#FF4500', '土': '#8B4513'}

# 日天干
ax = axes[0]
bp_data = [g['log_return'].values * 100 for _, g in df.groupby('day_tg_wuxing')]
bp_labels = sorted(df['day_tg_wuxing'].unique())
bp_data_ordered = [bp_data[bp_labels.index(l)] for l in bp_labels]
bp = ax.boxplot(bp_data_ordered, labels=bp_labels, patch_artist=True,
                showmeans=True, meanprops=dict(marker='D', markerfacecolor='red', markersize=5))
for patch, label in zip(bp['boxes'], bp_labels):
    patch.set_facecolor(colors.get(label, '#999999'))
    patch.set_alpha(0.6)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_title('日收益率 × 天干五行', fontsize=13, fontweight='bold')
ax.set_xlabel('天干五行')
ax.set_ylabel('日收益率 (%)')
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))

# 日地支
ax = axes[1]
bp_data = [g['log_return'].values * 100 for _, g in df.groupby('day_dz_wuxing')]
bp_labels = sorted(df['day_dz_wuxing'].unique())
bp_data_ordered = [bp_data[bp_labels.index(l)] for l in bp_labels]
bp = ax.boxplot(bp_data_ordered, labels=bp_labels, patch_artist=True,
                showmeans=True, meanprops=dict(marker='D', markerfacecolor='red', markersize=5))
for patch, label in zip(bp['boxes'], bp_labels):
    patch.set_facecolor(colors.get(label, '#999999'))
    patch.set_alpha(0.6)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_title('日收益率 × 地支五行', fontsize=13, fontweight='bold')
ax.set_xlabel('地支五行')
ax.set_ylabel('日收益率 (%)')
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))

fig.suptitle('宁德时代(300750) 2018-2026 日收益率按五行分组分布', fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fig1_daily_boxplot.png', dpi=300)
plt.close()
print("✅ Fig 1: 日频箱线图已完成")

# ============ Fig 2: 周频滚动窗口差异时序图 ============
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
colors2 = {'火-金': '#FF4500', '水-金': '#4169E1', '木-火': '#228B22', '土-火': '#8B4513'}
pairs_to_plot = ['火-金', '水-金', '木-火', '土-火']
window = min(156, len(df_weekly) // 2)

df_weekly['week_start'] = pd.to_datetime(df_weekly['week_start'])

for ax, pair_name in zip(axes.flatten(), pairs_to_plot):
    wx1, wx2 = pair_name.split('-')
    diffs = []
    dates = []
    for i in range(len(df_weekly) - window + 1):
        win = df_weekly.iloc[i:i+window]
        r1 = win[win['week_tg_wuxing']==wx1]['week_return'].mean()
        r2 = win[win['week_tg_wuxing']==wx2]['week_return'].mean()
        if not (np.isnan(r1) or np.isnan(r2)):
            diffs.append((r1 - r2) * 10000)  # bps
            dates.append(win['week_start'].iloc[window//2])
    ax.plot(dates, diffs, color=colors2.get(pair_name, '#333'), linewidth=0.8, alpha=0.8)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=np.mean(diffs), color='red', linestyle='-', alpha=0.6, label=f'均值={np.mean(diffs):.1f}bps')
    ax.set_title(f'{pair_name} 周均收益率差 (3年滚动)', fontsize=11)
    ax.set_xlabel('窗口中心日期')
    ax.set_ylabel('收益率差 (bps)')
    ax.legend(fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f'))

fig.suptitle('宁德时代 五行分组周收益率 3年滚动窗口差异', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fig2_rolling_window.png', dpi=300)
plt.close()
print("✅ Fig 2: 周频滚动窗口图已完成")

# ============ Fig 3: 月频 训练/测试 对比 ============
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

n_train = int(len(df_monthly) * 0.7)
df_monthly['period'] = ['训练集'] * n_train + ['测试集'] * (len(df_monthly) - n_train)

# 月天干
ax = axes[0]
train_means = df_monthly[df_monthly['period']=='训练集'].groupby('month_tg_wuxing')['month_return'].mean() * 100
test_means = df_monthly[df_monthly['period']=='测试集'].groupby('month_tg_wuxing')['month_return'].mean() * 100

wx_labels = ['金', '木', '水', '火', '土']
train_vals = [train_means.get(w, 0) for w in wx_labels]
test_vals = [test_means.get(w, 0) for w in wx_labels]

x = np.arange(len(wx_labels))
width = 0.35
bars1 = ax.bar(x - width/2, train_vals, width, label='训练集', color='steelblue', alpha=0.8)
bars2 = ax.bar(x + width/2, test_vals, width, label='测试集', color='coral', alpha=0.8)
ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
ax.set_xticks(x)
ax.set_xticklabels(wx_labels)
ax.set_title('月收益率 × 天干五行: 训练集 vs 测试集', fontsize=12, fontweight='bold')
ax.set_ylabel('月均收益率 (%)')
ax.legend()

# 标注方向反转
for w in wx_labels:
    tv = train_means.get(w, 0)
    tv2 = test_means.get(w, 0)
    if tv * tv2 < 0:
        ax.annotate('反转', (wx_labels.index(w), 0), textcoords="offset points",
                    xytext=(0, -20), ha='center', fontsize=9, color='red', fontweight='bold')

# 月地支
ax = axes[1]
train_means = df_monthly[df_monthly['period']=='训练集'].groupby('month_dz_wuxing')['month_return'].mean() * 100
test_means = df_monthly[df_monthly['period']=='测试集'].groupby('month_dz_wuxing')['month_return'].mean() * 100

dz_labels = ['金', '木', '水', '火', '土']
train_vals = [train_means.get(w, 0) for w in dz_labels]
test_vals = [test_means.get(w, 0) for w in dz_labels]

x = np.arange(len(dz_labels))
bars1 = ax.bar(x - width/2, train_vals, width, label='训练集', color='steelblue', alpha=0.8)
bars2 = ax.bar(x + width/2, test_vals, width, label='测试集', color='coral', alpha=0.8)
ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
ax.set_xticks(x)
ax.set_xticklabels(dz_labels)
ax.set_title('月收益率 × 地支五行: 训练集 vs 测试集', fontsize=12, fontweight='bold')
ax.set_ylabel('月均收益率 (%)')
ax.legend()

for w in dz_labels:
    tv = train_means.get(w, 0)
    tv2 = test_means.get(w, 0)
    if tv * tv2 < 0:
        ax.annotate('反转', (dz_labels.index(w), 0), textcoords="offset points",
                    xytext=(0, -20), ha='center', fontsize=9, color='red', fontweight='bold')

fig.suptitle('宁德时代 月频样本外检验 — 训练集(70%) vs 测试集(30%)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fig3_monthly_train_test.png', dpi=300)
plt.close()
print("✅ Fig 3: 月频训练/测试对比图已完成")

# ============ Fig 4: 汇总四格图 ============
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 左上: 日收益率分布 (核密度)
ax = axes[0, 0]
for wx in ['金', '木', '水', '火', '土']:
    subset = df[df['day_tg_wuxing'] == wx]['log_return'] * 100
    if len(subset) > 0:
        sns.kdeplot(subset, label=wx, color=colors.get(wx, '#999'), ax=ax, linewidth=1.5)
ax.set_xlabel('日收益率 (%)')
ax.set_ylabel('密度')
ax.set_title('日收益率分布 × 天干五行', fontsize=12)
ax.legend(fontsize=8)

# 右上: 周收益柱状图
ax = axes[0, 1]
wk_means = df_weekly.groupby('week_tg_wuxing')['week_return'].mean() * 100
wk_means.reindex(['金', '木', '水', '火', '土']).plot(kind='bar', ax=ax, color=[colors.get(w, '#999') for w in ['金', '木', '水', '火', '土']], alpha=0.8)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.set_title('周均收益率 × 天干五行', fontsize=12)
ax.set_ylabel('周均收益率 (%)')
ax.set_xlabel('')

# 左下: 月收益时序
ax = axes[1, 0]
df_monthly['cum_return'] = (1 + df_monthly['month_return']).cumprod()
ax.plot(df_monthly['month_start'], df_monthly['cum_return'], color='#333', linewidth=1)
ax.axvline(x=df_monthly.iloc[n_train]['month_start'], color='red', linestyle='--', alpha=0.7, label='训练/测试分界')
ax.set_title('宁德时代月累计收益 (2018-2026)', fontsize=12)
ax.set_ylabel('累计净值')
ax.legend()
ax.axhline(y=1, color='gray', linestyle='-', alpha=0.3)

# 右下: p值汇总
ax = axes[1, 1]
test_names = ['日天干', '日地支', '周天干', '周地支', '月天干\n(训练)', '月地支\n(训练)', '月天干\n(测试)', '月地支\n(测试)', '稳健性\n(缩尾)']
p_values = list(df_results['p值'])
ax.barh(test_names, p_values, color=['#e74c3c' if p < 0.05 else '#95a5a6' for p in p_values])
ax.axvline(x=0.05, color='red', linestyle='--', alpha=0.7, label='α=0.05')
ax.set_xlabel('p值')
ax.set_title('所有假设检验p值汇总', fontsize=12)
ax.legend()
for i, p in enumerate(p_values):
    ax.text(p + 0.01, i, f'{p:.3f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fig4_summary_all.png', dpi=300)
plt.close()
print("✅ Fig 4: 汇总四格图已完成")

print(f"\n所有可视化完成！输出目录: {OUTPUT_DIR}/")
