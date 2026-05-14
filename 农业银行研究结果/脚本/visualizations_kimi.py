#!/usr/bin/env python3
"""
可视化学术图 v4 — Kimi 美学版
Publication-quality charts with elegant styling, 五行 color palette,
clean typography, subtle grids, and professional academic look.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ============================================================
#  Global style configuration — Kimi's aesthetic
# ============================================================

# Elegant 五行 palette (used throughout)
WUXING_COLORS = {'金': '#FFD700', '木': '#228B22', '水': '#4169E1',
                 '火': '#FF4500', '土': '#8B4513'}
WX_ORDER = ['金', '木', '水', '火', '土']

# Font setup
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'DejaVu Sans',
                                     'Arial Unicode MS', 'AR PL UMing CN',
                                     'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Global style overrides for publication quality
plt.rcParams.update({
    'axes.facecolor': 'white',
    'axes.edgecolor': '#CCCCCC',
    'axes.grid': True,
    'axes.grid.which': 'major',
    'axes.axisbelow': True,
    'grid.color': '#E8E8E8',
    'grid.alpha': 0.6,
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'xtick.color': '#666666',
    'ytick.color': '#666666',
    'legend.fontsize': 9,
    'legend.frameon': True,
    'legend.fancybox': False,
    'legend.edgecolor': '#CCCCCC',
    'legend.facecolor': 'white',
    'figure.facecolor': 'white',
})

# Paths
OUTPUT_DIR = '/home/cpy/文档/金融数据库建立/研究结果'
CHART_DIR = f'{OUTPUT_DIR}/图表'

# Load data
df = pd.read_csv(f'{OUTPUT_DIR}/数据/data_daily_with_ganzhi.csv', parse_dates=['trade_date'])
df_weekly = pd.read_csv(f'{OUTPUT_DIR}/数据/data_weekly.csv')
df_monthly = pd.read_csv(f'{OUTPUT_DIR}/数据/data_monthly.csv')

print(f"Data loaded: daily={len(df)}, weekly={len(df_weekly)}, monthly={len(df_monthly)}")


def style_ax(ax, title='', xlabel='', ylabel=''):
    """Apply consistent styling to an axis."""
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10, color='#222222')
    ax.set_xlabel(xlabel, fontsize=11, labelpad=6, color='#444444')
    ax.set_ylabel(ylabel, fontsize=11, labelpad=6, color='#444444')
    ax.tick_params(axis='both', which='major', pad=4, colors='#666666')
    ax.grid(True, which='major', color='#E8E8E8', linestyle='-', linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#CCCCCC')
        ax.spines[spine].set_linewidth(0.8)


# ============================================================
#  Fig 1: 日频箱线图 — 双面板
# ============================================================
print("Generating Fig 1...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
fig.patch.set_facecolor('white')

for idx, (ax, col, group_label) in enumerate(zip(
    axes,
    ['day_tg_wuxing', 'day_dz_wuxing'],
    ['天干五行', '地支五行']
)):
    style_ax(ax, f'日收益率 × {group_label}',
             '五行', '日收益率 (%)')
    bp_data = [df[df[col] == wx]['log_return'].values * 100 for wx in WX_ORDER]
    bp = ax.boxplot(bp_data, labels=WX_ORDER, patch_artist=True,
                    showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='#CC3333',
                                   markeredgecolor='#CC3333', markersize=5),
                    medianprops=dict(color='#333333', linewidth=1.2),
                    whiskerprops=dict(color='#666666', linewidth=0.8),
                    capprops=dict(color='#666666', linewidth=0.8),
                    flierprops=dict(marker='o', markerfacecolor='#AAAAAA',
                                    markersize=3, alpha=0.4, markeredgecolor='none'),
                    widths=0.5)
    for patch, label in zip(bp['boxes'], WX_ORDER):
        patch.set_facecolor(WUXING_COLORS.get(label, '#999999'))
        patch.set_alpha(0.55)
        patch.set_edgecolor('#555555')
        patch.set_linewidth(0.8)
    ax.axhline(y=0, color='#888888', linestyle='--', linewidth=0.7, alpha=0.5)

fig.suptitle('农业银行 (601288)  2010–2026  日收益率按五行分组分布',
             fontsize=15, fontweight='bold', y=1.02, color='#222222')
plt.tight_layout(pad=2.0)
plt.savefig(f'{CHART_DIR}/fig1_daily_boxplot.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("  ✓ Fig 1 done")


# ============================================================
#  Fig 2: 周频滚动窗口差异时序 — 2×2 grid
# ============================================================
print("Generating Fig 2...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.patch.set_facecolor('white')

PAIR_COLORS = {'火-金': '#FF4500', '水-金': '#4169E1',
               '木-火': '#228B22', '土-火': '#8B4513'}
PAIRS = ['火-金', '水-金', '木-火', '土-火']
WINDOW = 156

for ax, pair_name in zip(axes.flatten(), PAIRS):
    wx1, wx2 = pair_name.split('-')
    diffs, dates = [], []
    for i in range(len(df_weekly) - WINDOW + 1):
        win = df_weekly.iloc[i:i+WINDOW]
        r1 = win[win['week_tg_wuxing'] == wx1]['week_return'].mean()
        r2 = win[win['week_tg_wuxing'] == wx2]['week_return'].mean()
        if not (np.isnan(r1) or np.isnan(r2)):
            diffs.append((r1 - r2) * 10000)
            dates.append(pd.to_datetime(win['week_start'].iloc[WINDOW // 2]))

    mean_diff = np.mean(diffs) if diffs else 0
    style_ax(ax, f'{pair_name}  周均收益率差 (3年滚动)',
             '窗口中心日期', '收益率差 (bps)')
    ax.plot(dates, diffs, color=PAIR_COLORS.get(pair_name, '#555555'),
            linewidth=0.9, alpha=0.75)
    ax.fill_between(dates, diffs, 0,
                     where=[d >= 0 for d in diffs] if diffs else [],
                     color=PAIR_COLORS.get(pair_name, '#555555'),
                     alpha=0.08, interpolate=True)
    ax.axhline(y=0, color='#888888', linestyle='--', linewidth=0.7, alpha=0.5)
    ax.axhline(y=mean_diff, color='#CC3333', linestyle='-', linewidth=0.9,
               alpha=0.7, label=f'均值 = {mean_diff:.1f} bps')
    ax.legend(loc='best', framealpha=0.85, edgecolor='#CCCCCC')

fig.suptitle('农业银行  五行分组周收益率  3年滚动窗口差异 (156周)',
             fontsize=15, fontweight='bold', y=1.01, color='#222222')
plt.tight_layout(pad=2.5)
plt.savefig(f'{CHART_DIR}/fig2_weekly_rolling.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("  ✓ Fig 2 done")


# ============================================================
#  Fig 3: 月频训练/测试对比 — 双面板柱状图
# ============================================================
print("Generating Fig 3...")
n_train = int(len(df_monthly) * 0.7)
df_monthly['period'] = ['训练集'] * n_train + ['测试集'] * (len(df_monthly) - n_train)

fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
fig.patch.set_facecolor('white')

train_color = '#4A7FB5'  # elegant steel blue
test_color = '#D4755E'   # warm coral

for idx, (ax, col, group_label) in enumerate(zip(
    axes,
    ['month_tg_wuxing', 'month_dz_wuxing'],
    ['天干五行', '地支五行']
)):
    style_ax(ax, f'月收益率 × {group_label}: 训练集 vs 测试集',
             '五行', '月均收益率 (%)')

    train_means = df_monthly[df_monthly['period'] == '训练集'].groupby(col)['month_return'].mean() * 100
    test_means = df_monthly[df_monthly['period'] == '测试集'].groupby(col)['month_return'].mean() * 100
    train_vals = [train_means.get(w, 0) for w in WX_ORDER]
    test_vals = [test_means.get(w, 0) for w in WX_ORDER]

    x = np.arange(len(WX_ORDER))
    width = 0.32

    bars1 = ax.bar(x - width/2 - 0.02, train_vals, width, label='训练集 (70%)',
                   color=train_color, alpha=0.85, edgecolor='white', linewidth=0.3)
    bars2 = ax.bar(x + width/2 + 0.02, test_vals, width, label='测试集 (30%)',
                   color=test_color, alpha=0.85, edgecolor='white', linewidth=0.3)

    ax.set_xticks(x)
    ax.set_xticklabels(WX_ORDER)
    ax.axhline(y=0, color='#888888', linestyle='-', linewidth=0.5, alpha=0.4)
    ax.legend(loc='lower right', framealpha=0.9, edgecolor='#CCCCCC')

    # Mark reversals
    for w in WX_ORDER:
        t = train_means.get(w, 0)
        te = test_means.get(w, 0)
        if t * te < 0:
            ax.annotate('↕ 反转', (WX_ORDER.index(w), 0),
                        textcoords="offset points", xytext=(0, -26),
                        ha='center', fontsize=9, color='#CC3333',
                        fontweight='bold',
                        arrowprops=dict(arrowstyle='-', color='#CC3333',
                                        lw=0.5, alpha=0.5))

fig.suptitle('农业银行  月频样本外检验 — 训练集 (70%) vs 测试集 (30%)',
             fontsize=15, fontweight='bold', y=1.02, color='#222222')
plt.tight_layout(pad=2.0)
plt.savefig(f'{CHART_DIR}/fig3_monthly_train_test.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("  ✓ Fig 3 done")


# ============================================================
#  Fig 4: 汇总四格图
# ============================================================
print("Generating Fig 4...")
fig, axes = plt.subplots(2, 2, figsize=(13, 10.5))
fig.patch.set_facecolor('white')

# ---- Top-left: KDE distribution ----
ax = axes[0, 0]
style_ax(ax, '日收益率分布 × 天干五行', '日收益率 (%)', '密度')
for wx in WX_ORDER:
    subset = df[df['day_tg_wuxing'] == wx]['log_return'] * 100
    if len(subset) > 0:
        sns.kdeplot(subset, label=wx, color=WUXING_COLORS.get(wx, '#999'),
                    ax=ax, linewidth=1.8, alpha=0.85)
ax.legend(loc='upper right', framealpha=0.85, edgecolor='#CCCCCC')

# ---- Top-right: Weekly bar chart ----
ax = axes[0, 1]
style_ax(ax, '周均收益率 × 天干五行', '五行', '周均收益率 (%)')
wk_means = df_weekly.groupby('week_tg_wuxing')['week_return'].mean() * 100
wk_vals = [wk_means.get(w, 0) for w in WX_ORDER]
bars = ax.bar(WX_ORDER, wk_vals,
              color=[WUXING_COLORS.get(w, '#999') for w in WX_ORDER],
              alpha=0.75, edgecolor='white', linewidth=0.3, width=0.55)
ax.axhline(y=0, color='#888888', linestyle='--', linewidth=0.7, alpha=0.5)
# Add value labels
for bar, val in zip(bars, wk_vals):
    y_pos = bar.get_height() if val >= 0 else bar.get_height()
    va = 'bottom' if val >= 0 else 'top'
    offset = 1.5 if val >= 0 else -1.5
    ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
            f'{val:.2f}%', ha='center', va=va, fontsize=8,
            color='#555555', fontweight='bold')

# ---- Bottom-left: Monthly cumulative return ----
ax = axes[1, 0]
df_monthly_sorted = df_monthly.sort_values('month_start').copy()
df_monthly_sorted['cum_return'] = (1 + df_monthly_sorted['month_return']).cumprod()
dates_m = pd.to_datetime(df_monthly_sorted['month_start'])
cum_ret = df_monthly_sorted['cum_return'].values

style_ax(ax, '农业银行 月累计收益 (2010–2026)', '日期', '累计净值')
ax.plot(dates_m, cum_ret, color='#333333', linewidth=1.2, alpha=0.85)
ax.axhline(y=1, color='#888888', linestyle='-', linewidth=0.5, alpha=0.3)
# Train/test split line
split_date = pd.to_datetime(df_monthly_sorted.iloc[n_train]['month_start'])
ax.axvline(x=split_date, color='#CC3333', linestyle='--', linewidth=0.9,
           alpha=0.7, label='训练/测试分界')
# Add fill between train and test
ax.axvspan(dates_m.iloc[0], split_date, alpha=0.04, color='#4A7FB5')
ax.axvspan(split_date, dates_m.iloc[-1], alpha=0.04, color='#D4755E')
ax.legend(loc='upper left', framealpha=0.85, edgecolor='#CCCCCC')
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))

# ---- Bottom-right: p-value horizontal bar chart ----
ax = axes[1, 1]
test_names = ['日天干', '日地支', '周天干', '周地支',
              '月天干(训练)', '月地支(训练)',
              '月天干(测试)', '月地支(测试)', '稳健性(缩尾)']
p_values = [0.917, 0.146, 0.212, 0.307, 0.257, 0.310, 0.141, 0.272, 0.917]
bar_colors = ['#CC3333' if p < 0.05 else '#8AB4D6' for p in p_values]

style_ax(ax, '全部假设检验 p 值汇总', 'p 值', '')
ax.set_yticks(range(len(test_names)))
ax.set_yticklabels(test_names, fontsize=9, color='#444444')
bars = ax.barh(range(len(test_names)), p_values, color=bar_colors,
               edgecolor='white', linewidth=0.3, height=0.55)
ax.axvline(x=0.05, color='#CC3333', linestyle='--', linewidth=0.9,
           alpha=0.7, label='α = 0.05')
ax.legend(loc='lower right', framealpha=0.85, edgecolor='#CCCCCC')
ax.set_xlim(0, 1.05)
ax.invert_yaxis()

# Add p-value labels
for i, (bar, p) in enumerate(zip(bars, p_values)):
    ax.text(bar.get_width() + 0.015, bar.get_y() + bar.get_height() / 2,
            f'{p:.3f}', va='center', fontsize=8.5, color='#555555',
            fontweight='bold')

fig.suptitle('农业银行 × 天干地支五行  综合分析汇总',
             fontsize=15, fontweight='bold', y=1.01, color='#222222')
plt.tight_layout(pad=2.5)
plt.savefig(f'{CHART_DIR}/fig4_summary_all.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print("  ✓ Fig 4 done")


# ============================================================
#  Verification
# ============================================================
import os
total_size = 0
for fn in ['fig1_daily_boxplot.png', 'fig2_weekly_rolling.png',
           'fig3_monthly_train_test.png', 'fig4_summary_all.png']:
    fp = os.path.join(CHART_DIR, fn)
    sz = os.path.getsize(fp)
    total_size += sz
    print(f"  {fn}: {sz / 1024:.1f} KB")
print(f"\n✅ All 4 charts generated! Total: {total_size / 1024 / 1024:.2f} MB")
print("Saved to: {}/".format(CHART_DIR))
