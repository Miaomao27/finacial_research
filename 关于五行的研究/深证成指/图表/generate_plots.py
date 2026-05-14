#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深证成指(399001.SZ) 五行研究出版级可视化
Publication-quality matplotlib visualizations with white theme
Author: AI Assistant
Date: 2026-05-14
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager as fm
import warnings
warnings.filterwarnings('ignore')

# ============== 配置 ==============
# 输出目录
OUTPUT_DIR = '/home/cpy/文档/金融数据库建立/关于五行的研究/深证成指/图表/'

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False

# 五行配色方案 (白底主题)
WUXING_COLORS = {
    '木': '#2ECC71',  # 翠绿 Emerald Green
    '火': '#E74C3C',  # 火红 Coral Red
    '土': '#F39C12',  # 金黄 Amber Gold
    '金': '#3498DB',  # 天蓝 Sky Blue
    '水': '#9B59B6',  # 紫罗兰 Violet Purple
}

WUXING_ORDER = ['木', '火', '土', '金', '水']

# 白底主题配色
BG_COLOR = 'white'
BG_COLOR_SEC = '#F8F9FA'
GRID_COLOR = '#DEE2E6'
TEXT_COLOR = '#212529'
TEXT_COLOR_SEC = '#6C757D'
ACCENT_COLOR = '#2563EB'

# ============== 数据加载 ==============
def load_data():
    """加载日线、周线、月线数据和统计表"""
    df_daily = pd.read_csv('/home/cpy/文档/金融数据库建立/关于五行的研究/深证成指/数据/data_daily.csv')
    df_weekly = pd.read_csv('/home/cpy/文档/金融数据库建立/关于五行的研究/深证成指/数据/data_weekly.csv')
    df_monthly = pd.read_csv('/home/cpy/文档/金融数据库建立/关于五行的研究/深证成指/数据/data_monthly.csv')
    df_tests = pd.read_csv('/home/cpy/文档/金融数据库建立/关于五行的研究/深证成指/统计表/table_all_tests.csv')
    return df_daily, df_weekly, df_monthly, df_tests

# ============== 图1: 日收益率箱线图 ==============
def plot_daily_boxplot(df_daily, df_tests):
    """日收益率按五行分组的箱线图"""
    # 获取日频五行检验的p值
    p_value = df_tests[df_tests['检验'] == '日频_五行_天干']['p值'].values[0]
    
    # 准备数据
    data_by_wuxing = []
    labels = []
    colors = []
    
    for wx in WUXING_ORDER:
        subset = df_daily[df_daily['五行_干'] == wx]['收益率']
        data_by_wuxing.append(subset.values)
        labels.append(wx)
        colors.append(WUXING_COLORS[wx])
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 7), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    # 绘制箱线图
    bp = ax.boxplot(data_by_wuxing, labels=labels, patch_artist=True,
                    widths=0.6, showfliers=True, flierprops=dict(marker='o', markersize=3, alpha=0.5))
    
    # 设置箱体颜色
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor(color)
        patch.set_linewidth(2)
    
    # 设置其他元素颜色
    for whisker in bp['whiskers']:
        whisker.set_color(GRID_COLOR)
        whisker.set_linewidth(1.5)
    for cap in bp['caps']:
        cap.set_color(GRID_COLOR)
        cap.set_linewidth(1.5)
    for median in bp['medians']:
        median.set_color(TEXT_COLOR)
        median.set_linewidth(2)
    for flier in bp['fliers']:
        flier.set_markerfacecolor(ACCENT_COLOR)
        flier.set_markeredgecolor('none')
    
    # 添加零线
    ax.axhline(y=0, color=ACCENT_COLOR, linestyle='--', linewidth=1.5, alpha=0.8)
    
    # 添加统计标注
    significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
    stat_text = f"Kruskal-Wallis Test\np-value = {p_value:.4f} {significance}"
    ax.text(0.98, 0.98, stat_text, transform=ax.transAxes, fontsize=11,
            color=TEXT_COLOR, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=BG_COLOR_SEC, edgecolor=GRID_COLOR, alpha=0.9))
    
    # 设置标题和标签
    ax.set_title('深证成指日收益率分布 - 按天干五行分组\n(2010-2025)', 
                 fontsize=14, color=TEXT_COLOR, fontweight='bold', pad=20)
    ax.set_xlabel('五行', fontsize=12, color=TEXT_COLOR, fontweight='bold')
    ax.set_ylabel('日收益率', fontsize=12, color=TEXT_COLOR, fontweight='bold')
    
    # 设置刻度样式
    ax.tick_params(colors=TEXT_COLOR, labelsize=11)
    ax.set_xticklabels([f'{label}\n({WUXING_COLORS[label]})' for label in labels], 
                       fontsize=11, color=TEXT_COLOR)
    
    # 格式化y轴为百分比
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.2f}%'))
    
    # 网格
    ax.grid(True, alpha=0.3, color=GRID_COLOR, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # 边框
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
        spine.set_linewidth(1)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}fig1_daily_boxplot.png', dpi=300, facecolor=BG_COLOR, 
                edgecolor='none', bbox_inches='tight')
    plt.close()
    print("✓ fig1_daily_boxplot.png 已保存")

# ============== 图2: 周收益率滚动平均线 ==============
def plot_weekly_rolling(df_weekly):
    """周收益率五行分组12周滚动平均线"""
    # 按周序号排序
    df_weekly = df_weekly.sort_values('周标签').reset_index(drop=True)
    
    # 为每个五行计算12周滚动平均
    window = 12
    
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    # 绘制每个五行的滚动平均线
    for wx in WUXING_ORDER:
        mask = df_weekly['五行_干'] == wx
        df_wx = df_weekly[mask].copy().reset_index(drop=True)
        if len(df_wx) > 0:
            df_wx['rolling'] = df_wx['收益率'].rolling(window=window, min_periods=1).mean()
            ax.plot(df_wx.index, df_wx['rolling'], color=WUXING_COLORS[wx], 
                   linewidth=2, label=wx, alpha=0.9)
    
    # 添加零线
    ax.axhline(y=0, color=TEXT_COLOR_SEC, linestyle='--', linewidth=1, alpha=0.6)
    
    # 图例
    legend = ax.legend(loc='upper right', frameon=True, fontsize=11,
                       facecolor=BG_COLOR_SEC, edgecolor=GRID_COLOR)
    for text in legend.get_texts():
        text.set_color(TEXT_COLOR)
    
    # 标题和标签
    ax.set_title(f'深证成指周收益率12周滚动平均 - 按天干五行分组\n(2010-2025, n={len(df_weekly)}周)', 
                 fontsize=14, color=TEXT_COLOR, fontweight='bold', pad=20)
    ax.set_xlabel('周序', fontsize=12, color=TEXT_COLOR, fontweight='bold')
    ax.set_ylabel('滚动平均收益率', fontsize=12, color=TEXT_COLOR, fontweight='bold')
    
    # 刻度样式
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.2f}%'))
    
    # 网格
    ax.grid(True, alpha=0.3, color=GRID_COLOR, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # 边框
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
        spine.set_linewidth(1)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}fig2_weekly_rolling.png', dpi=300, facecolor=BG_COLOR, 
                edgecolor='none', bbox_inches='tight')
    plt.close()
    print("✓ fig2_weekly_rolling.png 已保存")

# ============== 图3: 月收益率柱状图 ==============
def plot_monthly_bar(df_monthly):
    """月收益率柱状图按五行着色，标注均值线"""
    # 按年月排序
    df_monthly = df_monthly.sort_values('年月').reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(16, 7), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    # 颜色映射
    bar_colors = [WUXING_COLORS[wx] for wx in df_monthly['五行_干']]
    
    # 绘制柱状图
    x = np.arange(len(df_monthly))
    bars = ax.bar(x, df_monthly['收益率'], color=bar_colors, width=0.8, alpha=0.8, edgecolor='none')
    
    # 计算各五行的均值并绘制水平线
    mean_by_wuxing = df_monthly.groupby('五行_干')['收益率'].mean()
    
    # 为每个五行添加均值虚线
    for wx in WUXING_ORDER:
        if wx in mean_by_wuxing.index:
            mean_val = mean_by_wuxing[wx]
            ax.axhline(y=mean_val, color=WUXING_COLORS[wx], linestyle='--', 
                      linewidth=2, alpha=0.9, xmin=0, xmax=1)
    
    # 零线
    ax.axhline(y=0, color=TEXT_COLOR, linestyle='-', linewidth=1, alpha=0.8)
    
    # 设置x轴标签（只显示年份标记）
    years = df_monthly['年月'].str[:4].unique()
    year_positions = []
    year_labels = []
    for year in years[::2]:  # 每隔一年显示
        pos = df_monthly[df_monthly['年月'].str[:4] == year].index[0]
        year_positions.append(pos)
        year_labels.append(year)
    
    ax.set_xticks(year_positions)
    ax.set_xticklabels(year_labels, fontsize=10, color=TEXT_COLOR)
    
    # 标题和标签
    ax.set_title('深证成指月收益率时间序列 - 按天干五行着色\n(2010-2025)', 
                 fontsize=14, color=TEXT_COLOR, fontweight='bold', pad=20)
    ax.set_xlabel('年份', fontsize=12, color=TEXT_COLOR, fontweight='bold')
    ax.set_ylabel('月收益率', fontsize=12, color=TEXT_COLOR, fontweight='bold')
    
    # 刻度样式
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.2f}%'))
    
    # 网格
    ax.grid(True, alpha=0.2, color=GRID_COLOR, linestyle='-', linewidth=0.5, axis='y')
    ax.set_axisbelow(True)
    
    # 添加五行图例
    legend_patches = [mpatches.Patch(color=WUXING_COLORS[wx], label=wx, alpha=0.8) for wx in WUXING_ORDER]
    legend = ax.legend(handles=legend_patches, loc='upper right', frameon=True, 
                       fontsize=11, facecolor=BG_COLOR_SEC, edgecolor=GRID_COLOR, title='五行')
    legend.get_title().set_color(TEXT_COLOR)
    for text in legend.get_texts():
        text.set_color(TEXT_COLOR)
    
    # 边框
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
        spine.set_linewidth(1)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}fig3_monthly.png', dpi=300, facecolor=BG_COLOR, 
                edgecolor='none', bbox_inches='tight')
    plt.close()
    print("✓ fig3_monthly.png 已保存")

# ============== 图4: p值汇总条形图 ==============
def plot_pvalue_summary(df_tests):
    """12项检验p值的水平条形图，红色虚线标α=0.05"""
    fig, ax = plt.subplots(figsize=(12, 9), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    # 准备数据
    df_tests = df_tests.sort_values('p值', ascending=True)
    tests = df_tests['检验'].values
    pvalues = df_tests['p值'].values
    significant = df_tests['显著'].values
    
    # 映射检验名称为更友好的显示
    test_names = {
        '日频_天干': '日频-天干',
        '日频_地支': '日频-地支',
        '日频_五行_天干': '日频-五行(天干)',
        '日频_五行_地支': '日频-五行(地支)',
        'weekly_天干': '周频-天干',
        'weekly_地支': '周频-地支',
        'weekly_五行_天干': '周频-五行(天干)',
        'weekly_五行_地支': '周频-五行(地支)',
        '月频_天干': '月频-天干',
        '月频_地支': '月频-地支',
        '月频_五行_天干': '月频-五行(天干)',
        '月频_五行_地支': '月频-五行(地支)',
    }
    
    display_names = [test_names.get(t, t) for t in tests]
    
    # 颜色：显著为强调色，不显著为灰色
    bar_colors = [ACCENT_COLOR if sig else GRID_COLOR for sig in significant]
    
    y_pos = np.arange(len(display_names))
    
    # 绘制水平条形图
    bars = ax.barh(y_pos, pvalues, color=bar_colors, height=0.6, alpha=0.85, edgecolor='none')
    
    # 添加显著性标记
    for i, (p, sig) in enumerate(zip(pvalues, significant)):
        sig_text = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        if sig_text:
            ax.text(p + 0.02, i, sig_text, va='center', ha='left', 
                   fontsize=10, color=ACCENT_COLOR, fontweight='bold')
    
    # 添加α=0.05显著性水平线
    ax.axvline(x=0.05, color='#F87171', linestyle='--', linewidth=2, alpha=0.9, label='α = 0.05')
    
    # 添加p=1.0参考线
    ax.axvline(x=1.0, color=GRID_COLOR, linestyle='-', linewidth=1, alpha=0.5)
    
    # 设置y轴
    ax.set_yticks(y_pos)
    ax.set_yticklabels(display_names, fontsize=11, color=TEXT_COLOR)
    
    # 设置x轴
    ax.set_xlim(0, 1.1)
    ax.set_xlabel('p-value', fontsize=12, color=TEXT_COLOR, fontweight='bold')
    
    # 标题
    ax.set_title('深证成指五行研究 - Kruskal-Wallis检验p值汇总\n(12项假设检验)', 
                 fontsize=14, color=TEXT_COLOR, fontweight='bold', pad=20)
    
    # 刻度样式
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    ax.invert_yaxis()  # 最小p值在顶部
    
    # 添加p值数值标签
    for i, (bar, p) in enumerate(zip(bars, pvalues)):
        width = bar.get_width()
        ax.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
               f'{p:.4f}', ha='left', va='center', fontsize=9, color=TEXT_COLOR_SEC)
    
    # 网格
    ax.grid(True, alpha=0.3, color=GRID_COLOR, linestyle='-', linewidth=0.5, axis='x')
    ax.set_axisbelow(True)
    
    # 图例
    legend = ax.legend(loc='lower right', frameon=True, fontsize=11,
                       facecolor=BG_COLOR_SEC, edgecolor=GRID_COLOR)
    for text in legend.get_texts():
        text.set_color(TEXT_COLOR)
    
    # 边框
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
        spine.set_linewidth(1)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}fig4_summary_pvalues.png', dpi=300, facecolor=BG_COLOR, 
                edgecolor='none', bbox_inches='tight')
    plt.close()
    print("✓ fig4_summary_pvalues.png 已保存")

# ============== 主函数 ==============
def main():
    print("=" * 60)
    print("深证成指(399001.SZ) 五行研究可视化生成")
    print("=" * 60)
    
    # 加载数据
    print("\n[1/5] 加载数据...")
    df_daily, df_weekly, df_monthly, df_tests = load_data()
    print(f"    日线数据: {len(df_daily)} 条")
    print(f"    周线数据: {len(df_weekly)} 条")
    print(f"    月线数据: {len(df_monthly)} 条")
    print(f"    检验项目: {len(df_tests)} 项")
    
    # 生成图表
    print("\n[2/5] 生成图1: 日收益率箱线图...")
    plot_daily_boxplot(df_daily, df_tests)
    
    print("\n[3/5] 生成图2: 周收益率滚动平均线...")
    plot_weekly_rolling(df_weekly)
    
    print("\n[4/5] 生成图3: 月收益率柱状图...")
    plot_monthly_bar(df_monthly)
    
    print("\n[5/5] 生成图4: p值汇总条形图...")
    plot_pvalue_summary(df_tests)
    
    print("\n" + "=" * 60)
    print("所有图表生成完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    main()
