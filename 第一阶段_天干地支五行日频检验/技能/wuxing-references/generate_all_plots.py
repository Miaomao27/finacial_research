#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五行天干地支 × 金融市场收益率 — 出版级可视化合集
Covers: 7 research items (3 stocks + 4 indices), 4 charts each = 28 figures
Nature/Science-style white background, academic quality.
"""
import sys, os, json, textwrap
import numpy as np
import pandas as pd

# Add style module
sys.path.insert(0, '/home/cpy/文档/金融数据库建立/关于五行的研究')
from academic_style import *

# ── Configuration ────────────────────────────────────────────────
BASE = '/home/cpy/文档/金融数据库建立/关于五行的研究'

# Research items definition: (folder_name, type, sample_name_for_labels)
RESEARCH_ITEMS = [
    # Stocks (个股) — data in subdirectories
    ('农业银行', 'stock', '农业银行 (601288)'),
    ('五粮液',   'stock', '五粮液 (000858)'),
    # CATL — flat structure (data in root)
    ('宁德时代', 'stock_flat', '宁德时代 (300750)'),
    # Indices (指数)
    ('上证指数',  'index', '上证指数 (000001.SH)'),
    ('深证成指',  'index', '深证成指 (399001.SZ)'),
    ('创业板指',  'index', '创业板指 (399006.SZ)'),
    ('科创50',    'index', '科创50 (000688.SH)'),
]

# ═══════════════════════════════════════════════════════════════
#  DATA LOADING  —  unified loaders for each type
# ═══════════════════════════════════════════════════════════════

def load_stock_data(name):
    """Load stock-type data (农业银行/五粮液 structure)"""
    d = f'{BASE}/{name}/数据'
    daily = pd.read_csv(f'{d}/data_daily_with_ganzhi.csv', parse_dates=['trade_date'])
    weekly = pd.read_csv(f'{d}/data_weekly.csv')
    monthly = pd.read_csv(f'{d}/data_monthly.csv')
    tests = pd.read_csv(f'{BASE}/{name}/统计表/table_all_tests.csv')
    # Summary tables
    tg_summary = pd.read_csv(f'{BASE}/{name}/统计表/table_daily_tg_wuxing.csv')
    dz_summary = pd.read_csv(f'{BASE}/{name}/统计表/table_daily_dz_wuxing.csv')
    return daily, weekly, monthly, tests, tg_summary, dz_summary

def load_stock_flat_data(name):
    """Load flat-stock data (宁德时代 structure)"""
    d = f'{BASE}/{name}'
    daily = pd.read_csv(f'{d}/data_daily.csv', parse_dates=['trade_date'])
    weekly = pd.read_csv(f'{d}/data_weekly.csv')
    monthly = pd.read_csv(f'{d}/data_monthly.csv')
    tests = pd.read_csv(f'{d}/table_all_tests.csv')
    tg_summary = pd.read_csv(f'{d}/table_daily_tg_wuxing.csv')
    dz_summary = pd.read_csv(f'{d}/table_daily_dz_wuxing.csv')
    return daily, weekly, monthly, tests, tg_summary, dz_summary

def load_index_data(name):
    """Load index-type data (上证/深证/创业板/科创50 structure)"""
    d = f'{BASE}/{name}/数据'
    daily = pd.read_csv(f'{d}/data_daily.csv', parse_dates=['交易日期'])
    weekly = pd.read_csv(f'{d}/data_weekly.csv')
    monthly = pd.read_csv(f'{d}/data_monthly.csv')
    tests = pd.read_csv(f'{BASE}/{name}/统计表/table_all_tests.csv')
    return daily, weekly, monthly, tests

# ═══════════════════════════════════════════════════════════════
#  CHART 1: Daily Return Boxplot  (天干 + 地支)
# ═══════════════════════════════════════════════════════════════

def fig1_daily_boxplot(daily, tests, out_path, sample_label, is_stock=True):
    """Publication-quality daily return boxplot with tian-gan and di-zhi"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.5))
    
    # Determine column names based on data type
    if is_stock:
        tg_col, dz_col, ret_col = 'day_tg_wuxing', 'day_dz_wuxing', 'log_return'
    else:
        tg_col, dz_col, ret_col = '五行_干', '五行_支', '收益率'
    
    # Parse p-values from tests
    p_tg, p_dz = None, None
    for _, row in tests.iterrows():
        t = str(row.iloc[0])
        p = float(row['p值'])
        if '天干' in t or '五行_干' in t or ('日频' in t and '天干' in t):
            if p_tg is None: p_tg = p
        if '地支' in t or '五行_支' in t or ('日频' in t and '地支' in t):
            if p_dz is None: p_dz = p
    
    # ── Panel A: 天干五行 ──
    ax = axes[0]
    data_by_wx = []
    labels = []
    colors = []
    for wx in WUXING_ORDER:
        subset = daily[daily[tg_col] == wx][ret_col].dropna() * 100
        if len(subset) > 0:
            data_by_wx.append(subset.values)
            labels.append(wx)
            colors.append(WUXING_COLORS.get(wx, '#999999'))
    
    bp = ax.boxplot(data_by_wx, labels=labels, patch_artist=True,
                    widths=0.55, showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='#E74C3C',
                                   markersize=4, markeredgecolor='none'),
                    flierprops=dict(marker='o', markersize=2.5, alpha=0.35,
                                    markeredgecolor='none'))
    for patch, c in zip(bp['boxes'], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.55)
        patch.set_edgecolor(c)
        patch.set_linewidth(1.5)
    for med in bp['medians']:
        med.set_color('#333333')
        med.set_linewidth(2)
    
    ax.axhline(y=0, color='#E74C3C', linestyle='--', linewidth=1, alpha=0.6)
    if p_tg is not None: add_pvalue_box(ax, p_tg, x=0.97, y=0.97)
    set_axis_style(ax, xlabel='天干五行', ylabel='日收益率 (%)',
                   title='日收益率 × 天干五行')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.2f}'))
    # Auto-scale y-axis based on data
    all_vals = np.concatenate([d for d in data_by_wx if len(d) > 0])
    q1, q3 = np.percentile(all_vals, [25, 75])
    iqr = q3 - q1
    y_lim = max(abs(q1 - 1.5*iqr), abs(q3 + 1.5*iqr)) * 1.5
    ax.set_ylim(-y_lim, y_lim)
    
    # Add mean marker legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='D', color='w', markerfacecolor='#E74C3C',
                               markersize=5, label='Mean')]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8, framealpha=0.8)
    
    # ── Panel B: 地支五行 ──
    ax = axes[1]
    data_by_wx = []
    labels_dz = []
    colors_dz = []
    
    # Use dz_summary for consistent ordering
    dz_order = ['木', '火', '土', '金', '水']
    for wx in dz_order:
        subset = daily[daily[dz_col] == wx][ret_col].dropna() * 100
        if len(subset) > 0:
            data_by_wx.append(subset.values)
            labels_dz.append(wx)
            colors_dz.append(WUXING_COLORS.get(wx, '#999999'))
    
    bp = ax.boxplot(data_by_wx, labels=labels_dz, patch_artist=True,
                    widths=0.55, showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='#E74C3C',
                                   markersize=4, markeredgecolor='none'),
                    flierprops=dict(marker='o', markersize=2.5, alpha=0.35,
                                    markeredgecolor='none'))
    for patch, c in zip(bp['boxes'], colors_dz):
        patch.set_facecolor(c)
        patch.set_alpha(0.55)
        patch.set_edgecolor(c)
        patch.set_linewidth(1.5)
    for med in bp['medians']:
        med.set_color('#333333')
        med.set_linewidth(2)
    
    ax.axhline(y=0, color='#E74C3C', linestyle='--', linewidth=1, alpha=0.6)
    if p_dz is not None: add_pvalue_box(ax, p_dz, x=0.97, y=0.97)
    set_axis_style(ax, xlabel='地支五行', ylabel='日收益率 (%)',
                   title='日收益率 × 地支五行')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.2f}'))
    # Auto-scale y-axis based on data
    all_vals_dz = np.concatenate([d for d in data_by_wx if len(d) > 0])
    q1_dz, q3_dz = np.percentile(all_vals_dz, [25, 75])
    iqr_dz = q3_dz - q1_dz
    y_lim_dz = max(abs(q1_dz - 1.5*iqr_dz), abs(q3_dz + 1.5*iqr_dz)) * 1.5
    ax.set_ylim(-y_lim_dz, y_lim_dz)
    
    # Add mean marker legend
    legend_elements = [Line2D([0], [0], marker='D', color='w', markerfacecolor='#E74C3C',
                               markersize=5, label='Mean')]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8, framealpha=0.8)
    
    # ── Super title ──
    fig.suptitle(f'日收益率按五行分组分布 — {sample_label}',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {out_path}')

# ═══════════════════════════════════════════════════════════════
#  CHART 2: Weekly Rolling Window Analysis
# ═══════════════════════════════════════════════════════════════

def fig2_weekly_rolling(weekly, out_path, sample_label, is_stock=True):
    """Weekly rolling mean comparison across WuXing groups"""
    if is_stock:
        tg_col, ret_col = 'week_tg_wuxing', 'week_return'
    else:
        tg_col, ret_col = '五行_干', '收益率'
    
    window = 12  # ~quarter for weekly data
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    
    # ── Panel A: Rolling means by WuXing ──
    ax = axes[0]
    weekly_sorted = weekly.sort_index()
    
    for wx in WUXING_ORDER:
        mask = weekly[tg_col] == wx
        df_wx = weekly[mask].copy().reset_index(drop=True)
        if len(df_wx) < 3: continue
        df_wx['rolling'] = df_wx[ret_col].rolling(window=min(window, len(df_wx)//2),
                                                    min_periods=1).mean() * 100
        ax.plot(df_wx.index, df_wx['rolling'],
                color=WUXING_COLORS.get(wx, '#999'), linewidth=1.2,
                alpha=0.85, label=wx)
    
    ax.axhline(y=0, color='#E74C3C', linestyle='--', linewidth=0.8, alpha=0.5)
    set_axis_style(ax, xlabel='周序', ylabel='滚动平均收益率 (%)',
                   title=f'{window}周滚动平均 × 天干五行')
    ax.legend(loc='best', ncol=3, fontsize=8)
    ax.set_xticklabels([])
    
    # ── Panel B: Pairwise difference rolling ──
    ax = axes[1]
    pairs = [('木', '金'), ('火', '水'), ('土', '木'), ('火', '金')]
    pair_colors = ['#27AE60', '#E74C3C', '#F39C12', '#8E44AD']
    
    for (wx1, wx2), color in zip(pairs, pair_colors):
        diffs, indices = [], []
        for i in range(len(weekly) - window + 1):
            win = weekly.iloc[i:i+window]
            r1 = win[win[tg_col]==wx1][ret_col].mean()
            r2 = win[win[tg_col]==wx2][ret_col].mean()
            if not (np.isnan(r1) or np.isnan(r2)):
                diffs.append((r1 - r2) * 100)
                indices.append(i + window//2)
        if len(diffs) > 0:
            ax.plot(indices, diffs, color=color, linewidth=0.9, alpha=0.75,
                    label=f'{wx1}-{wx2}')
    
    ax.axhline(y=0, color='#333333', linestyle='--', linewidth=0.8, alpha=0.5)
    set_axis_style(ax, xlabel='窗口中心', ylabel='收益率差 (%)',
                   title='五行对周收益率差 (滚动窗口)')
    ax.legend(loc='best', fontsize=8)
    ax.set_xticklabels([])
    
    fig.suptitle(f'周频五行收益比较 — {sample_label}',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {out_path}')

# ═══════════════════════════════════════════════════════════════
#  CHART 3: Monthly — Train/Test (stocks) OR Time Series Bar (indices)
# ═══════════════════════════════════════════════════════════════

def fig3_monthly_stock(monthly, out_path, sample_label):
    """Monthly: train/test split comparison (for stocks)"""
    n_train = int(len(monthly) * 0.7)
    monthly = monthly.copy()
    monthly['period'] = ['Train Set'] * n_train + ['Test Set'] * (len(monthly) - n_train)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    # TG (天干五行)
    ax = axes[0]
    train_m = monthly[monthly['period']=='Train Set'].groupby('month_tg_wuxing')['month_return'].mean() * 100
    test_m = monthly[monthly['period']=='Test Set'].groupby('month_tg_wuxing')['month_return'].mean() * 100
    
    x = np.arange(len(WUXING_ORDER))
    w = 0.35
    train_v = [train_m.get(wx, 0) for wx in WUXING_ORDER]
    test_v = [test_m.get(wx, 0) for wx in WUXING_ORDER]
    
    ax.bar(x - w/2, train_v, w, label='Train (70%)', color='#3498DB', alpha=0.8, edgecolor='white', linewidth=0.5)
    ax.bar(x + w/2, test_v, w, label='Test (30%)', color='#E74C3C', alpha=0.8, edgecolor='white', linewidth=0.5)
    ax.axhline(y=0, color='#333', linewidth=0.8, linestyle='-', alpha=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels([f'{wx}\n(n={int(train_m.get(wx,0)+test_m.get(wx,0))})' for wx in WUXING_ORDER])
    set_axis_style(ax, xlabel='天干五行', ylabel='月均收益率 (%)',
                   title='月收益率 × 天干五行: 样本外检验')
    ax.legend(fontsize=9)
    
    # Add reversal annotations
    for i, wx in enumerate(WUXING_ORDER):
        if train_m.get(wx, 0) * test_m.get(wx, 0) < 0:
            ax.annotate('↕', (i, 0), textcoords="offset points",
                       xytext=(0, -18), ha='center', fontsize=10, color='#E74C3C')
    
    # DZ (地支五行)
    ax = axes[1]
    train_m = monthly[monthly['period']=='Train Set'].groupby('month_dz_wuxing')['month_return'].mean() * 100
    test_m = monthly[monthly['period']=='Test Set'].groupby('month_dz_wuxing')['month_return'].mean() * 100
    
    train_v = [train_m.get(wx, 0) for wx in WUXING_ORDER]
    test_v = [test_m.get(wx, 0) for wx in WUXING_ORDER]
    
    ax.bar(x - w/2, train_v, w, label='Train (70%)', color='#3498DB', alpha=0.8, edgecolor='white', linewidth=0.5)
    ax.bar(x + w/2, test_v, w, label='Test (30%)', color='#E74C3C', alpha=0.8, edgecolor='white', linewidth=0.5)
    ax.axhline(y=0, color='#333', linewidth=0.8, linestyle='-', alpha=0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(WUXING_ORDER)
    set_axis_style(ax, xlabel='地支五行', ylabel='月均收益率 (%)',
                   title='月收益率 × 地支五行: 样本外检验')
    ax.legend(fontsize=9)
    
    for i, wx in enumerate(WUXING_ORDER):
        if train_m.get(wx, 0) * test_m.get(wx, 0) < 0:
            ax.annotate('↕', (i, 0), textcoords="offset points",
                       xytext=(0, -18), ha='center', fontsize=10, color='#E74C3C')
    
    fig.suptitle(f'月频样本外检验 — {sample_label}',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {out_path}')

def fig3_monthly_index(monthly, out_path, sample_label):
    """Monthly: time series bar chart colored by WuXing (for indices)"""
    monthly = monthly.sort_values('年月').reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(14, 5.5))
    
    rets = monthly['收益率'] * 100
    bar_colors = [WUXING_COLORS.get(wx, '#999') for wx in monthly['五行_干']]
    
    bars = ax.bar(range(len(monthly)), rets, color=bar_colors, width=0.85,
                  alpha=0.8, edgecolor='none')
    
    # Mean lines per WuXing
    for wx in WUXING_ORDER:
        m = monthly[monthly['五行_干']==wx]['收益率'].mean() * 100
        ax.axhline(y=m, color=WUXING_COLORS[wx], linestyle='--',
                   linewidth=1.5, alpha=0.7)
    
    ax.axhline(y=0, color='#333333', linewidth=1)
    
    # Year labels
    years = monthly['年月'].str[:4].unique()
    year_positions = [monthly[monthly['年月'].str[:4]==y].index[0] for y in years[::3]]
    ax.set_xticks(year_positions)
    ax.set_xticklabels(years[::3], fontsize=9)
    
    set_axis_style(ax, xlabel='年份', ylabel='月收益率 (%)',
                   title=f'月收益率时间序列 (按天干五行着色) — {sample_label}')
    
    # Legend
    patches = [plt.Rectangle((0,0),1,1, facecolor=WUXING_COLORS[wx], alpha=0.8)
               for wx in WUXING_ORDER]
    ax.legend(patches, [f'{wx}' for wx in WUXING_ORDER],
              loc='upper right', ncol=5, fontsize=9,
              framealpha=0.9, edgecolor='#DDDDDD')
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1f}'))
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {out_path}')

# ═══════════════════════════════════════════════════════════════
#  CHART 4: P-value Summary (horizontal bar)
# ═══════════════════════════════════════════════════════════════

def fig4_pvalue_summary(tests, out_path, sample_label):
    """Horizontal bar chart of all hypothesis test p-values"""
    fig, ax = plt.subplots(figsize=(10, max(5, len(tests)*0.5)))
    
    # Clean test names
    tests = tests.copy()
    test_names = [str(t).replace('_', '-') for t in tests.iloc[:, 0]]
    pvalues = tests['p值'].values
    significant = tests.get('显著(α=0.05)', tests.get('显著', None))
    if significant is not None:
        if significant.dtype == bool:
            sig_bool = significant.values
        else:
            sig_bool = significant.values.astype(str).str.lower() == 'true'
    else:
        sig_bool = [False] * len(pvalues)
    
    # Sort by p-value
    sort_idx = np.argsort(pvalues)
    test_names_s = [test_names[i] for i in sort_idx]
    pvalues_s = pvalues[sort_idx]
    sig_bool_s = [sig_bool[i] for i in sort_idx]
    
    y_pos = np.arange(len(test_names_s))
    colors = ['#E74C3C' if s else '#BDC3C7' for s in sig_bool_s]
    edge_colors = ['#C0392B' if s else '#95A5A6' for s in sig_bool_s]
    
    bars = ax.barh(y_pos, pvalues_s, color=colors, edgecolor=edge_colors,
                   linewidth=0.8, height=0.6, alpha=0.85)
    
    # α=0.05 line
    ax.axvline(x=0.05, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.8,
               label='α = 0.05')
    ax.axvline(x=1.0, color='#CCCCCC', linestyle='-', linewidth=0.8, alpha=0.5)
    
    # P-value labels
    for i, (bar, p) in enumerate(zip(bars, pvalues_s)):
        ax.text(max(p + 0.02, 0.01), bar.get_y() + bar.get_height()/2,
               f'{p:.4f}', ha='left', va='center', fontsize=8, color='#555555')
        # Significance stars
        if p < 0.001:
            ax.text(p/2, bar.get_y() + bar.get_height()/2, '***',
                   ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        elif p < 0.01:
            ax.text(p/2, bar.get_y() + bar.get_height()/2, '**',
                   ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        elif p < 0.05:
            ax.text(p/2, bar.get_y() + bar.get_height()/2, '*',
                   ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(test_names_s, fontsize=9)
    ax.set_xlim(0, 1.15)
    ax.invert_yaxis()
    
    set_axis_style(ax, xlabel='p-value', ylabel='假设检验',
                   title=f'Kruskal-Wallis检验p值汇总 — {sample_label}')
    ax.legend(loc='lower right', fontsize=9)
    
    # Summary annotation
    n_sig = sum(sig_bool_s)
    ax.text(0.98, 0.02, f'{n_sig}/{len(pvalues_s)} significant at α=0.05',
            transform=ax.transAxes, ha='right', va='bottom',
            fontsize=9, color='#E74C3C' if n_sig > 0 else '#555555',
            style='italic')
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'  ✓ {out_path}')

# ═══════════════════════════════════════════════════════════════
#  MASTER RUNNER
# ═══════════════════════════════════════════════════════════════

def run_all():
    print('=' * 65)
    print('  五行 × 金融市场收益率 — 出版级可视化')
    print(f'  生成 {len(RESEARCH_ITEMS)} 个样本 × 4 张图 = {len(RESEARCH_ITEMS)*4} 张图表')
    print('=' * 65)
    
    for name, rtype, sample_label in RESEARCH_ITEMS:
        print(f'\n── {sample_label} ──')
        
        if rtype == 'stock':
            daily, weekly, monthly, tests, tg_s, dz_s = load_stock_data(name)
            out_dir = f'{BASE}/{name}/图表'
        elif rtype == 'stock_flat':
            daily, weekly, monthly, tests, tg_s, dz_s = load_stock_flat_data(name)
            out_dir = f'{BASE}/{name}'
        else:  # index
            daily, weekly, monthly, tests = load_index_data(name)
            out_dir = f'{BASE}/{name}/图表'
        
        os.makedirs(out_dir, exist_ok=True)
        
        # Fig 1: Daily boxplot
        fig1_daily_boxplot(daily, tests, f'{out_dir}/fig1_daily_boxplot.png',
                          sample_label, is_stock=(rtype != 'index'))
        
        # Fig 2: Weekly rolling
        fig2_weekly_rolling(weekly, f'{out_dir}/fig2_weekly_rolling.png',
                           sample_label, is_stock=(rtype != 'index'))
        
        # Fig 3: Monthly (different per type)
        if rtype in ('stock', 'stock_flat'):
            fig3_monthly_stock(monthly, f'{out_dir}/fig3_monthly_train_test.png',
                             sample_label)
        else:
            fig3_monthly_index(monthly, f'{out_dir}/fig3_monthly.png',
                             sample_label)
        
        # Fig 4: P-value summary
        fig4_pvalue_summary(tests, f'{out_dir}/fig4_summary_pvalues.png',
                           sample_label)
    
    print(f'\n{"=" * 65}')
    print(f'  ✅ 全部 {len(RESEARCH_ITEMS)*4} 张图表生成完成!')
    print(f'{"=" * 65}')

if __name__ == '__main__':
    run_all()
