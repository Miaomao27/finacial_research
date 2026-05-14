#!/usr/bin/env python3
"""
Chinese/CJK charting bootstrap for matplotlib.
Run this first to verify font rendering before generating production charts.

Detects available CJK fonts, tests rendering, and sets up rcParams.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings('ignore')

# ===== Step 1: Detect useful CJK fonts =====
cjk_fonts = {}
for f in fm.fontManager.ttflist:
    name = f.name
    if 'Noto Sans CJK' in name:
        cjk_fonts[name] = f.fname

# Priority: Noto Sans CJK JP (has both CJK + Latin)
preferred = None
for try_name in ['Noto Sans CJK JP', 'Noto Sans CJK SC', 'Noto Sans CJK']:
    if try_name in cjk_fonts:
        preferred = try_name
        break

if preferred:
    print(f'Using: {preferred} ({cjk_fonts[preferred]})')
    plt.rcParams['font.sans-serif'] = [preferred, 'DejaVu Sans']
else:
    print('WARNING: No Noto Sans CJK found. Trying alternatives...')
    # Fallback chain
    plt.rcParams['font.sans-serif'] = [
        'AR PL UKai CN', 'AR PL UMing CN',
        'WenQuanYi Micro Hei', 'DejaVu Sans'
    ]

plt.rcParams['axes.unicode_minus'] = False

# ===== Step 2: Verify rendering =====
test_text = '中文测试Test123%()金木水火土p=0.917'
fig, ax = plt.subplots(figsize=(6, 1.5))
ax.text(0.5, 0.5, test_text, ha='center', va='center', fontsize=14,
        transform=ax.transAxes)
ax.set_title('字体渲染验证 Font Rendering Test', fontsize=12)
# Also test % and () which often fail
ax.text(0.5, 0.2, '百分号: 25%  括号: (123)  小数点: 0.917  负号: -0.05',
        ha='center', va='center', fontsize=11, transform=ax.transAxes)
fig.savefig('/tmp/cjk_font_test.png', dpi=100)
plt.close()
print(f'Test chart saved to /tmp/cjk_font_test.png')
print('Open it visually. If ANY character shows as a box → pick a different font.')
print('Common problematic characters: % ( ) - . 0-9 a-z A-Z')
