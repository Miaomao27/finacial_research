#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publication-quality charts for Five Elements (五行) holding period returns
Style: Deep Space Blue + Fluorescent Cyan (深空蓝+荧光青配色)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import sys

# Find Chinese font
fm._load_fontmanager(try_read_cache=False)
_available_fonts = {f.name for f in fm.fontManager.ttflist}
CHINESE_FONTS = ['AR PL UKai CN', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans']
_FONT = next((f for f in CHINESE_FONTS if f in _available_fonts), 'DejaVu Sans')
print(f'[generate_charts] Selected font: {_FONT}', file=sys.stderr)

# Deep Space Blue Theme Colors
BACKGROUND_COLOR = '#0a0e1a'      # Deep space blue
PANEL_COLOR = '#12182b'           # Slightly lighter
GRID_COLOR = '#1e2943'            # Grid lines
TEXT_COLOR = '#e6f7ff'            # Bright white-blue
ACCENT_CYAN = '#00f5ff'           # Fluorescent cyan
ACCENT_BLUE = '#00a8ff'           # Bright blue

# Five Elements colors (optimized for dark theme)
WUXING_COLORS = {
    '木': '#00ff88',   # Bright emerald
    '火': '#ff3366',   # Neon red-pink
    '土': '#ffcc00',   # Golden yellow
    '金': '#00ccff',   # Cyan-blue
    '水': '#aa66ff',   # Purple
}

WUXING_ORDER = ['木', '火', '土', '金', '水']

# Configure matplotlib for dark theme
rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': [_FONT, 'DejaVu Sans'],
    'font.size': 11,
    'axes.unicode_minus': False,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
    'savefig.facecolor': BACKGROUND_COLOR,
    'figure.facecolor': BACKGROUND_COLOR,
    'axes.facecolor': PANEL_COLOR,
    'axes.edgecolor': GRID_COLOR,
    'axes.linewidth': 1.5,
    'axes.grid': True,
    'grid.color': GRID_COLOR,
    'grid.alpha': 0.5,
    'grid.linestyle': '-',
    'grid.linewidth': 0.8,
    'xtick.color': TEXT_COLOR,
    'ytick.color': TEXT_COLOR,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 6,
    'ytick.major.size': 6,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'axes.labelcolor': TEXT_COLOR,
    'axes.titlecolor': ACCENT_CYAN,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.labelweight': 'bold',
    'legend.facecolor': PANEL_COLOR,
    'legend.edgecolor': GRID_COLOR,
    'legend.labelcolor': TEXT_COLOR,
    'legend.fontsize': 10,
    'text.color': TEXT_COLOR,
})

# ───────────────────────────────────────────────────────────────────────────────
# Load Data
# ───────────────────────────────────────────────────────────────────────────────

df_stats = pd.read_csv('/home/cpy/文档/金融数据库建立/关于五行的研究/五行月份持有期收益研究/analysis/stats.csv')
df_summary = pd.read_csv('/home/cpy/文档/金融数据库建立/关于五行的研究/五行月份持有期收益研究/analysis/summary.csv')

holding_periods = ['1m', '2m', '3m', '6m', '9m', '12m', '24m']
output_dir = '/home/cpy/文档/金融数据库建立/关于五行的研究/五行月份持有期收益研究/charts'

print(f"[generate_charts] Loaded {len(df_stats)} stat rows, {len(df_summary)} summary rows", file=sys.stderr)

# ───────────────────────────────────────────────────────────────────────────────
# Chart 1: 五行×持有期热力图 (Heatmap)
# ───────────────────────────────────────────────────────────────────────────────

print("[generate_charts] Creating Chart 1: Heatmap...", file=sys.stderr)

fig1, ax1 = plt.subplots(figsize=(10, 7))

# Prepare heatmap data (mean returns)
heatmap_data = []
for wuxing in WUXING_ORDER:
    row = []
    for period in holding_periods:
        val = df_stats[(df_stats['wuxing'] == wuxing) & (df_stats['holding_period'] == period)]['mean'].values
        row.append(val[0] if len(val) > 0 else 0)
    heatmap_data.append(row)

heatmap_df = pd.DataFrame(heatmap_data, index=WUXING_ORDER, columns=holding_periods)

# Custom colormap for dark theme (dark blue -> cyan -> white)
from matplotlib.colors import LinearSegmentedColormap
colors = ['#0a0e1a', '#1a3a5c', '#0066aa', '#00a8ff', '#00f5ff', '#ffffff']
cmap_dark = LinearSegmentedColormap.from_list('deep_space', colors)

sns.heatmap(heatmap_df, annot=True, fmt='.3f', cmap=cmap_dark,
            linewidths=1.5, linecolor=GRID_COLOR,
            cbar_kws={'label': '平均收益', 'shrink': 0.8},
            ax=ax1, vmin=-0.1, vmax=1.0,
            annot_kws={'color': '#ffffff', 'fontsize': 10, 'weight': 'bold'})

ax1.set_xlabel('持有期', fontsize=12, fontweight='bold', color=TEXT_COLOR)
ax1.set_ylabel('五行', fontsize=12, fontweight='bold', color=TEXT_COLOR)
ax1.set_title('五行×持有期平均收益热力图', fontsize=15, fontweight='bold', 
              color=ACCENT_CYAN, pad=15)

# Style colorbar
cbar = ax1.collections[0].colorbar
cbar.ax.yaxis.label.set_color(TEXT_COLOR)
cbar.ax.tick_params(colors=TEXT_COLOR)

plt.tight_layout()
plt.savefig(f'{output_dir}/01_wuxing_heatmap.png', facecolor=BACKGROUND_COLOR)
plt.close()
print("[generate_charts] Chart 1 saved: 01_wuxing_heatmap.png", file=sys.stderr)

# ───────────────────────────────────────────────────────────────────────────────
# Chart 2: 各五行收益曲线 (Return Curves)
# ───────────────────────────────────────────────────────────────────────────────

print("[generate_charts] Creating Chart 2: Return Curves...", file=sys.stderr)

fig2, ax2 = plt.subplots(figsize=(12, 7))

periods_numeric = [1, 2, 3, 6, 9, 12, 24]

for wuxing in WUXING_ORDER:
    values = []
    for period in holding_periods:
        val = df_stats[(df_stats['wuxing'] == wuxing) & (df_stats['holding_period'] == period)]['mean'].values
        values.append(val[0] if len(val) > 0 else 0)
    
    ax2.plot(periods_numeric, values, marker='o', markersize=8, linewidth=2.5,
             label=wuxing, color=WUXING_COLORS[wuxing],
             markerfacecolor=WUXING_COLORS[wuxing], markeredgecolor='white',
             markeredgewidth=1.5)

ax2.set_xlabel('持有期 (月)', fontsize=12, fontweight='bold')
ax2.set_ylabel('平均收益', fontsize=12, fontweight='bold')
ax2.set_title('各五行收益曲线 (持有期1-24月)', fontsize=15, fontweight='bold', 
              color=ACCENT_CYAN, pad=15)
ax2.set_xticks(periods_numeric)
ax2.set_xticklabels(holding_periods)
ax2.legend(loc='upper right', framealpha=0.9, edgecolor=GRID_COLOR, 
           facecolor=PANEL_COLOR, fontsize=11)
ax2.set_axisbelow(True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color(GRID_COLOR)
ax2.spines['bottom'].set_color(GRID_COLOR)
ax2.tick_params(colors=TEXT_COLOR)

# Add subtle glow effect to axes
ax2.spines['left'].set_linewidth(2)
ax2.spines['bottom'].set_linewidth(2)

plt.tight_layout()
plt.savefig(f'{output_dir}/02_wuxing_curves.png', facecolor=BACKGROUND_COLOR)
plt.close()
print("[generate_charts] Chart 2 saved: 02_wuxing_curves.png", file=sys.stderr)

# ───────────────────────────────────────────────────────────────────────────────
# Chart 3: 最优区间标注图 (Optimal Intervals)
# ───────────────────────────────────────────────────────────────────────────────

print("[generate_charts] Creating Chart 3: Optimal Intervals...", file=sys.stderr)

fig3, ax3 = plt.subplots(figsize=(14, 8))

# Find top 3 (wuxing, period) combinations by mean return
top_combinations = df_stats.nlargest(3, 'mean')[['wuxing', 'holding_period', 'mean']]
print(f"[generate_charts] Top 3 combinations:\n{top_combinations}", file=sys.stderr)

# Plot all combinations as scatter
all_x = []
all_y = []
all_colors = []
all_sizes = []
all_labels = []

for idx, row in df_stats.iterrows():
    wuxing = row['wuxing']
    period = row['holding_period']
    mean_ret = row['mean']
    
    period_idx = holding_periods.index(period)
    wuxing_idx = WUXING_ORDER.index(wuxing)
    
    all_x.append(period_idx)
    all_y.append(wuxing_idx)
    all_colors.append(mean_ret)
    all_sizes.append(100 + mean_ret * 300)
    all_labels.append(f"{wuxing}-{period}")

scatter = ax3.scatter(all_x, all_y, c=all_colors, s=all_sizes, cmap=cmap_dark,
                      edgecolors='white', linewidths=0.5, alpha=0.8, vmin=0, vmax=1)

# Annotate top 3
for idx, row in top_combinations.iterrows():
    wuxing = row['wuxing']
    period = row['holding_period']
    mean_ret = row['mean']
    
    period_idx = holding_periods.index(period)
    wuxing_idx = WUXING_ORDER.index(wuxing)
    
    # Draw arrow annotation
    ax3.annotate(f'TOP\n{wuxing}-{period}\n{mean_ret:.3f}',
                 xy=(period_idx, wuxing_idx),
                 xytext=(period_idx + 1.5, wuxing_idx - 0.5),
                 fontsize=10, fontweight='bold', color=ACCENT_CYAN,
                 ha='center', va='center',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor=PANEL_COLOR,
                          edgecolor=ACCENT_CYAN, linewidth=2, alpha=0.95),
                 arrowprops=dict(arrowstyle='->', color=ACCENT_CYAN, lw=2))

ax3.set_xticks(range(len(holding_periods)))
ax3.set_xticklabels(holding_periods)
ax3.set_yticks(range(len(WUXING_ORDER)))
ax3.set_yticklabels(WUXING_ORDER)
ax3.set_xlabel('持有期', fontsize=12, fontweight='bold')
ax3.set_ylabel('五行', fontsize=12, fontweight='bold')
ax3.set_title('最优投资区间标注图 (圆点大小代表收益水平)', 
              fontsize=15, fontweight='bold', color=ACCENT_CYAN, pad=15)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax3, shrink=0.6)
cbar.set_label('平均收益', fontsize=11, color=TEXT_COLOR)
cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=TEXT_COLOR)

ax3.set_axisbelow(True)
ax3.grid(True, alpha=0.3, color=GRID_COLOR)

plt.tight_layout()
plt.savefig(f'{output_dir}/03_optimal_intervals.png', facecolor=BACKGROUND_COLOR)
plt.close()
print("[generate_charts] Chart 3 saved: 03_optimal_intervals.png", file=sys.stderr)

# ───────────────────────────────────────────────────────────────────────────────
# Chart 4: 分标的TOP5五行收益对比 (Top 5 Symbols Bar Chart)
# ───────────────────────────────────────────────────────────────────────────────

print("[generate_charts] Creating Chart 4: Top 5 Symbols Comparison...", file=sys.stderr)

# Calculate average return by symbol for each wuxing
stock_wuxing_returns = df_summary.groupby(['ts_code', 'month_wuxing'])[['hold_1m', 'hold_3m', 'hold_6m', 'hold_12m']].mean()
stock_wuxing_returns['avg_return'] = stock_wuxing_returns.mean(axis=1)

# Get top 5 symbols by overall average return
symbol_avg = stock_wuxing_returns.groupby('ts_code')['avg_return'].mean().sort_values(ascending=False)
top5_symbols = symbol_avg.head(5).index.tolist()
print(f"[generate_charts] Top 5 symbols: {top5_symbols}", file=sys.stderr)

fig4, ax4 = plt.subplots(figsize=(14, 8))

x = np.arange(len(top5_symbols))
width = 0.15
multiplier = 0

for wuxing in WUXING_ORDER:
    values = []
    for symbol in top5_symbols:
        try:
            val = stock_wuxing_returns.loc[(symbol, wuxing), 'avg_return']
        except KeyError:
            val = 0
        values.append(val)
    
    offset = width * multiplier
    bars = ax4.bar(x + offset, values, width, label=wuxing, color=WUXING_COLORS[wuxing],
                   edgecolor='white', linewidth=0.5, alpha=0.9)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        if abs(height) > 0.01:
            ax4.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -12),
                        textcoords="offset points",
                        ha='center', va='bottom' if height >= 0 else 'top',
                        fontsize=7, color=TEXT_COLOR, rotation=90 if abs(height) > 0.5 else 0)
    
    multiplier += 1

ax4.set_xlabel('标的代码', fontsize=12, fontweight='bold')
ax4.set_ylabel('平均收益', fontsize=12, fontweight='bold')
ax4.set_title('TOP5标的五行收益对比柱状图', fontsize=15, fontweight='bold', 
              color=ACCENT_CYAN, pad=15)
ax4.set_xticks(x + width * 2)
ax4.set_xticklabels(top5_symbols, rotation=30, ha='right')
ax4.legend(loc='upper right', framealpha=0.9, fontsize=10, 
           facecolor=PANEL_COLOR, edgecolor=GRID_COLOR)
ax4.axhline(y=0, color=TEXT_COLOR, linestyle='-', linewidth=0.8, alpha=0.5)
ax4.set_axisbelow(True)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.spines['left'].set_color(GRID_COLOR)
ax4.spines['bottom'].set_color(GRID_COLOR)

plt.tight_layout()
plt.savefig(f'{output_dir}/04_top5_symbols.png', facecolor=BACKGROUND_COLOR)
plt.close()
print("[generate_charts] Chart 4 saved: 04_top5_symbols.png", file=sys.stderr)

print("[generate_charts] All 4 charts generated successfully!", file=sys.stderr)
