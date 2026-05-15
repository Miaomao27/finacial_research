#!/usr/bin/env python3
"""Regenerate T4 charts with academic white-background style."""
import sys, os, numpy as np, pandas as pd

BASE = '/home/cpy/文档/金融数据库建立/关于五行的研究/五行月份持有期收益研究'
sys.path.insert(0, os.path.dirname(BASE))
from academic_style import *

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

df = pd.read_csv(os.path.join(BASE, 'analysis', 'summary.csv'))
out = os.path.join(BASE, 'charts')
os.makedirs(out, exist_ok=True)

hold_cols = ['hold_1m','hold_2m','hold_3m','hold_6m','hold_9m','hold_12m','hold_24m']
hold_labels = ['1月','2月','3月','6月','9月','12月','24月']
wxing_order = ['木','火','土','金','水']
wxing_colors = {'木':'#2E7D32','火':'#E53935','土':'#8D6E63','金':'#FDD835','水':'#1E88E5'}

# 1. Heatmap
fig, ax = plt.subplots(figsize=(10, 6))
pivot = df.groupby('month_wuxing')[hold_cols].mean()
pivot = pivot.reindex(wxing_order)
heat_data = pivot.values
im = ax.imshow(heat_data, cmap='RdYlGn', aspect='auto', norm=Normalize(vmin=-0.3, vmax=0.5))
ax.set_xticks(range(len(hold_labels)))
ax.set_xticklabels(hold_labels)
ax.set_yticks(range(len(wxing_order)))
ax.set_yticklabels(wxing_order)
for i in range(len(wxing_order)):
    for j in range(len(hold_labels)):
        v = heat_data[i, j]
        c = 'white' if abs(v) > 0.15 else 'black'
        ax.text(j, i, f'{v:.1%}', ha='center', va='center', fontsize=8, color=c)
ax.set_xlabel('持有期')
ax.set_ylabel('买入月份五行')
ax.set_title('五行×持有期 平均收益率', fontsize=13, fontweight='bold')
fig.colorbar(im, ax=ax, label='平均收益率', shrink=0.8)
plt.tight_layout()
plt.savefig(os.path.join(out, '01_wuxing_heatmap.png'))
plt.close()
print('✅ 01 热力图')

# 2. Wuxing curves
fig, ax = plt.subplots(figsize=(12, 6))
for wx in wxing_order:
    sub = df[df['month_wuxing'] == wx]
    means = [sub[c].mean() for c in hold_cols]
    ax.plot(range(len(hold_labels)), means, 'o-', label=wx,
            color=wxing_colors[wx], linewidth=2, markersize=6)
ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
ax.set_xticks(range(len(hold_labels)))
ax.set_xticklabels(hold_labels)
ax.set_xlabel('持有期')
ax.set_ylabel('平均收益')
ax.set_title('各五行买入月份 持有期收益曲线', fontsize=13, fontweight='bold')
ax.legend(title='买入月份五行', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(out, '02_wuxing_curves.png'))
plt.close()
print('✅ 02 收益曲线')

# 3. Optimal intervals
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
# Left: top 3 returns per wuxing
wx_best = {}
for wx in wxing_order:
    sub = df[df['month_wuxing'] == wx]
    means = [sub[c].mean() for c in hold_cols]
    top3_idx = np.argsort(means)[-3:][::-1]
    wx_best[wx] = [(hold_labels[i], means[i]) for i in top3_idx]

x_pos = np.arange(len(wxing_order))
bar_width = 0.25
for rank in range(3):
    vals = [wx_best[wx][rank][1] for wx in wxing_order]
    labels = [wx_best[wx][rank][0] for wx in wxing_order]
    bars = axes[0].bar(x_pos + rank*bar_width, vals, bar_width,
                       label=f'TOP{rank+1}', alpha=0.8)
    for bar, lbl in zip(bars, labels):
        axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+(0.005 if bar.get_height()>0 else -0.02),
                     lbl, ha='center', fontsize=7)

axes[0].set_xticks(x_pos + bar_width)
axes[0].set_xticklabels(wxing_order)
axes[0].set_ylabel('平均收益')
axes[0].set_title('各五行买入月份 TOP3 持有期')
axes[0].legend(fontsize=8)
axes[0].axhline(y=0, color='gray', linestyle='--', linewidth=0.5)

# Right: best buy month per wuxing (from T6)
best_data = {'木':'土月','火':'火月','土':'金月','金':'土月','水':'土月'}
axes[1].bar(best_data.keys(), [1]*5, color=[wxing_colors[k] for k in best_data], alpha=0.7)
for i, (wx, bm) in enumerate(best_data.items()):
    axes[1].text(i, 0.5, bm, ha='center', va='center', fontsize=12, fontweight='bold')
axes[1].set_ylim(0, 1.5)
axes[1].set_yticks([])
axes[1].set_title('各行业五行最佳买入月份（来自T6分析）')
plt.tight_layout()
plt.savefig(os.path.join(out, '03_optimal_intervals.png'))
plt.close()
print('✅ 03 最优区间')

# 4. Top5 per symbol
fig, ax = plt.subplots(figsize=(14, 8))
symbols = df['ts_code'].unique()[:10]
x = np.arange(len(symbols))
w = 0.12
for i, wx in enumerate(wxing_order):
    vals = []
    for sym in symbols:
        sub = df[(df['ts_code']==sym) & (df['month_wuxing']==wx)]
        vals.append(sub['hold_1m'].mean() if len(sub)>0 else 0)
    ax.bar(x + i*w, vals, w, label=wx, color=wxing_colors[wx], alpha=0.8)
ax.set_xticks(x + w*2)
ax.set_xticklabels([s.replace('.SH','').replace('.SZ','').replace('.SI','') for s in symbols], rotation=45, fontsize=8)
ax.set_ylabel('持有1月平均收益')
ax.set_title('各标的 五行买入×1月持有 收益对比（TOP10标的）')
ax.legend(title='买入月份五行', fontsize=8)
ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig(os.path.join(out, '04_top5_symbols.png'))
plt.close()
print('✅ 04 分标的对比')

print('\n所有图表已重新生成（白底科研风）')
