#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publication-quality Academic Plotting Style
Nature/Science inspired — white background, clean layout, Chinese font support
"""
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib
matplotlib.use('Agg')

# ── Font Configuration ──────────────────────────────────────────
# Try multiple Chinese fonts in order of preference
CHINESE_FONTS = [
    'AR PL UKai CN', 'AR PL UMing CN',
    'Noto Sans CJK SC', 'Noto Sans CJK JP',
    'WenQuanYi Micro Hei', 'SimHei',
    'Arial Unicode MS', 'DejaVu Sans'
]

# Find first available Chinese font
import matplotlib.font_manager as fm
# Rebuild cache if needed
fm._load_fontmanager(try_read_cache=False)
_available_fonts = {f.name for f in fm.fontManager.ttflist}
# Debug: print what's available
_KWN_FONTS = [f for f in CHINESE_FONTS if f in _available_fonts]
print(f'[academic_style] Available fonts with Chinese: {_KWN_FONTS}', file=__import__('sys').stderr)
_FONT = next((f for f in CHINESE_FONTS if f in _available_fonts), 'DejaVu Sans')
print(f'[academic_style] Selected font: {_FONT}', file=__import__('sys').stderr)

rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': [_FONT] + ['DejaVu Sans'],
    'font.size': 10,
    'axes.unicode_minus': False,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#CCCCCC',
    'axes.linewidth': 1.0,
    'axes.grid': True,
    'grid.color': '#EEEEEE',
    'grid.alpha': 0.6,
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.edgecolor': '#DDDDDD',
    'legend.fancybox': False,
    'legend.fontsize': 9,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'axes.labelweight': 'bold',
})

# ── Color Palettes ──────────────────────────────────────────────

# Five Elements (Wu Xing) - academic-grade distinct colors
WUXING_COLORS = {
    '木': '#27AE60',   # Emerald - Wood
    '火': '#E74C3C',   # Crimson - Fire
    '土': '#F39C12',   # Amber - Earth
    '金': '#3498DB',   # Azure - Metal
    '水': '#8E44AD',   # Violet - Water
}

WUXING_ORDER = ['木', '火', '土', '金', '水']

# Tian Gan (10 Heavenly Stems) colors
TIANGAN_COLORS = {
    '甲': '#2ECC71', '乙': '#A8E6CF',
    '丙': '#E74C3C', '丁': '#F1948A',
    '戊': '#F39C12', '己': '#FDEBD0',
    '庚': '#3498DB', '辛': '#85C1E9',
    '壬': '#8E44AD', '癸': '#BB8FCE',
}

# Di Zhi (12 Earthly Branches) colors  
DIZHI_COLORS = {
    '子': '#8E44AD', '丑': '#F39C12', '寅': '#27AE60',
    '卯': '#2ECC71', '辰': '#F39C12', '巳': '#E74C3C',
    '午': '#C0392B', '未': '#F39C12', '申': '#3498DB',
    '酉': '#85C1E9', '戌': '#F39C12', '亥': '#8E44AD',
}

# ── Helper Functions ────────────────────────────────────────────

def get_font(size=10):
    """Get font properties with given size"""
    return {'fontsize': size, 'fontfamily': 'sans-serif'}

def add_significance_bar(ax, x1, x2, y, h, p_value, color='#333333'):
    """Add significance bracket between two groups"""
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.2, color=color)
    sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'n.s.'
    ax.text((x1+x2)/2, y+h, sig, ha='center', va='bottom', fontsize=8, color=color)

def add_pvalue_box(ax, p_value, x=0.98, y=0.98):
    """Add p-value annotation box"""
    sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'n.s.'
    text = f'Kruskal-Wallis\np = {p_value:.4f} {sig}'
    ax.text(x, y, text, transform=ax.transAxes, fontsize=8,
            ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F8F9FA',
                     edgecolor='#DDDDDD', alpha=0.9))

def set_axis_style(ax, xlabel=None, ylabel=None, title=None):
    """Apply consistent axis styling"""
    if xlabel: ax.set_xlabel(xlabel, fontsize=11, fontweight='bold')
    if ylabel: ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
    if title: ax.set_title(title, fontsize=13, fontweight='bold', pad=12)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
