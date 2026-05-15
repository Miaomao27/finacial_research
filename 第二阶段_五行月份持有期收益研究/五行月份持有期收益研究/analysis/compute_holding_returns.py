#!/usr/bin/env python3
"""
T2: 五行月份持有期收益计算 (pure Python, no numpy)
Input:  data/all_monthly.csv
Output: analysis/by_stock/{code}_holding.csv, analysis/summary.csv, analysis/stats.csv
"""

import csv
import os
import math
from collections import defaultdict

BASE_DIR = "/home/cpy/文档/金融数据库建立/关于五行的研究/五行月份持有期收益研究"
INPUT_PATH = os.path.join(BASE_DIR, "data", "all_monthly.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis")
BY_STOCK_DIR = os.path.join(OUTPUT_DIR, "by_stock")

HOLDING_PERIODS = [1, 2, 3, 6, 9, 12, 24]

os.makedirs(BY_STOCK_DIR, exist_ok=True)

# ── Stats helpers (pure Python) ───────────────────────────────────
def mean(vals):
    return sum(vals) / len(vals)

def median(vals):
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    else:
        return (s[n // 2 - 1] + s[n // 2]) / 2.0

def stddev(vals, mu=None):
    if mu is None:
        mu = mean(vals)
    n = len(vals)
    if n < 2:
        return 0.0
    return math.sqrt(sum((x - mu) ** 2 for x in vals) / (n - 1))

# ── 1. Read data ──────────────────────────────────────────────────
print("Reading input data...")
data = defaultdict(list)  # ts_code -> list of {month, return, month_wuxing}

with open(INPUT_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['month'] == '%Y-%m' or not row['return'] or row['return'].strip() == '':
            continue
        ts_code = row['ts_code']
        data[ts_code].append({
            'month': row['month'],
            'return': float(row['return']),
            'month_wuxing': row['month_wuxing'],
        })

# Sort each stock's data by month
for code in data:
    data[code].sort(key=lambda x: x['month'])

print(f"Loaded {len(data)} stocks, {sum(len(v) for v in data.values())} rows")

# ── 2. Compute holding returns ────────────────────────────────────
print("Computing holding returns...")
all_rows = []  # for summary.csv
stats_data = defaultdict(list)  # (wuxing, period) -> list of annualized returns

for code, rows in sorted(data.items()):
    n = len(rows)
    stock_rows = []
    for i, entry in enumerate(rows):
        entry_month = entry['month']
        wuxing = entry['month_wuxing']
        
        holding_row = {
            'entry_month': entry_month,
            'ts_code': code,
            'month_wuxing': wuxing,
        }
        
        for hp in HOLDING_PERIODS:
            if i + hp >= n:
                holding_row[f'hold_{hp}m'] = ''
            else:
                compound = 1.0
                for j in range(1, hp + 1):
                    compound *= (1.0 + rows[i + j]['return'])
                
                # Annualize: (compound)^(12/hp) - 1
                annualized = compound ** (12.0 / hp) - 1.0
                holding_row[f'hold_{hp}m'] = round(annualized, 6)
                
                stats_data[(wuxing, hp)].append(annualized)
        
        stock_rows.append(holding_row)
        all_rows.append(holding_row)
    
    # Write per-stock CSV
    out_path = os.path.join(BY_STOCK_DIR, f"{code}_holding.csv")
    fieldnames = ['entry_month', 'ts_code', 'month_wuxing'] + [f'hold_{hp}m' for hp in HOLDING_PERIODS]
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stock_rows)
    print(f"  {code}: {len(stock_rows)} entry months")

# ── 3. Write summary.csv ──────────────────────────────────────────
print("\nWriting summary.csv...")
summary_path = os.path.join(OUTPUT_DIR, "summary.csv")
fieldnames = ['entry_month', 'ts_code', 'month_wuxing'] + [f'hold_{hp}m' for hp in HOLDING_PERIODS]
with open(summary_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)
print(f"  {len(all_rows)} rows written")

# ── 4. Compute & write stats.csv ──────────────────────────────────
print("\nComputing statistics...")
stats_path = os.path.join(OUTPUT_DIR, "stats.csv")
wuxing_order = ['木', '火', '土', '金', '水']

with open(stats_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['wuxing', 'holding_period', 'mean', 'median', 'std', 'count'])
    for wuxing in wuxing_order:
        for hp in HOLDING_PERIODS:
            values = stats_data.get((wuxing, hp), [])
            if values:
                mu = mean(values)
                med = median(values)
                sd = stddev(values, mu)
                writer.writerow([
                    wuxing, f'{hp}m',
                    round(mu, 6),
                    round(med, 6),
                    round(sd, 6),
                    len(values)
                ])
            else:
                writer.writerow([wuxing, f'{hp}m', '', '', '', 0])

print(f"  stats.csv written with {len(HOLDING_PERIODS) * len(wuxing_order)} rows")

# ── 5. Quick summary table ────────────────────────────────────────
print("\n" + "=" * 80)
print("QUICK SUMMARY: Mean annualized returns by wuxing × holding period")
print("=" * 80)
header = f"{'Wuxing':<8}" + "".join(f"{hp:>14}m" for hp in HOLDING_PERIODS)
print(header)
print("-" * len(header))
for wuxing in wuxing_order:
    row = f"{wuxing:<8}"
    for hp in HOLDING_PERIODS:
        values = stats_data.get((wuxing, hp), [])
        if values:
            row += f"{mean(values)*100:>13.2f}%"
        else:
            row += f"{'':>14}"
    print(row)

print("\nDone.")
