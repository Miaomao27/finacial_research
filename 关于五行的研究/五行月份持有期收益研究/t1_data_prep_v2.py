#!/usr/bin/env python3
"""
T1: Data Preparation — Monthly aggregation + Ganzhi-Wuxing annotation
Uses ROW_NUMBER() window functions for fast monthly close extraction.
"""

import subprocess
import csv
import os
from collections import OrderedDict, defaultdict

DB_HOST = "192.168.31.29"
DB_USER = "finance_user"
DB_PASS = "Finance2026!"
DB_NAME = "china_finance_db"
OUTPUT_DIR = "/home/cpy/文档/金融数据库建立/关于五行的研究/五行月份持有期收益研究/data"

# Wuxing mappings
HEAVENLY_WUXING = {
    "甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土",
    "庚":"金","辛":"金","壬":"水","癸":"水"
}
BRANCH_WUXING = {
    "子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火",
    "未":"土","申":"金","酉":"金","戌":"土","亥":"水"
}


def mysql_query(sql):
    """Run SQL via mysql CLI and return list of dicts."""
    result = subprocess.run(
        ["mysql", "-h", DB_HOST, "-u", DB_USER, f"-p{DB_PASS}", DB_NAME, "-e", sql],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"MySQL error: {result.stderr}")
    output = result.stdout.strip()
    if not output:
        return []
    lines = output.split("\n")
    lines = [l for l in lines if l.strip() and not l.startswith("mysql:")]
    if len(lines) < 2:
        return []
    headers = [h.strip() for h in lines[0].split("\t")]
    rows = []
    for line in lines[1:]:
        vals = line.split("\t")
        row = OrderedDict()
        for i, h in enumerate(headers):
            row[h] = vals[i] if i < len(vals) else ""
        rows.append(row)
    return rows


def get_monthly_dailyquote():
    """Monthly close + ganzhi for all daily_quote symbols (7 codes)."""
    sql = """
    SELECT d.code, d.month, d.close, tc.月干支 AS month_ganzhi
    FROM (
        SELECT 证券代码 AS code,
               DATE_FORMAT(交易日期, '%Y-%m') AS month,
               收盘价 AS close,
               交易日期 AS trade_date,
               ROW_NUMBER() OVER (
                   PARTITION BY 证券代码, DATE_FORMAT(交易日期, '%Y-%m')
                   ORDER BY 交易日期 DESC
               ) AS rn
        FROM daily_quote
        WHERE 交易状态 = '正常' AND 是否收盘 = 1
    ) d
    JOIN trade_calendar tc ON d.trade_date = tc.交易日期
    WHERE d.rn = 1 AND tc.月干支 IS NOT NULL
    ORDER BY d.code, d.month;
    """
    rows = mysql_query(sql)
    data = defaultdict(list)
    for r in rows:
        data[r["code"]].append(r)
    return dict(data)


def get_monthly_sector():
    """Monthly close + ganzhi for all sector_daily codes (31 Shenwan industries)."""
    sql = """
    SELECT d.code, d.sector_name, d.month, d.close, tc.月干支 AS month_ganzhi
    FROM (
        SELECT 行业代码 AS code,
               行业名称 AS sector_name,
               DATE_FORMAT(交易日期, '%Y-%m') AS month,
               收盘价 AS close,
               交易日期 AS trade_date,
               ROW_NUMBER() OVER (
                   PARTITION BY 行业代码, DATE_FORMAT(交易日期, '%Y-%m')
                   ORDER BY 交易日期 DESC
               ) AS rn
        FROM sector_daily
        WHERE 是否收盘 = 1
    ) d
    JOIN trade_calendar tc ON d.trade_date = tc.交易日期
    WHERE d.rn = 1 AND tc.月干支 IS NOT NULL
    ORDER BY d.code, d.month;
    """
    rows = mysql_query(sql)
    data = defaultdict(list)
    for r in rows:
        data[r["code"]].append(r)
    return dict(data)


def parse_ganzhi(ganzhi):
    """Parse 月干支 like '甲子' -> (heavenly_stem, earthly_branch)."""
    if not ganzhi or len(ganzhi) < 2:
        return "", ""
    return ganzhi[0], ganzhi[1]


def calc_returns(records):
    """
    Given sorted monthly records (oldest first), calculate returns and
    add wuxing annotations. Returns list of dicts for CSV output.
    """
    out = []
    prev_close = None

    for r in records:
        close_str = r["close"]
        try:
            close = float(close_str)
        except (ValueError, TypeError):
            prev_close = None
            continue

        ganzhi = r.get("month_ganzhi", "")
        stem, branch = parse_ganzhi(ganzhi)

        ret = None
        if prev_close is not None and prev_close > 0:
            ret = round((close - prev_close) / prev_close, 6)

        out.append({
            "month": r["month"],
            "ts_code": r["code"],
            "return": ret,
            "heavenly_stem": stem,
            "earthly_branch": branch,
            "stem_wuxing": HEAVENLY_WUXING.get(stem, ""),
            "branch_wuxing": BRANCH_WUXING.get(branch, ""),
            "month_wuxing": BRANCH_WUXING.get(branch, ""),
        })
        prev_close = close

    return out


def write_csv(filename, rows):
    if not rows:
        print(f"  SKIP (empty): {filename}")
        return False
    fieldnames = ["month","ts_code","return","heavenly_stem","earthly_branch",
                  "stem_wuxing","branch_wuxing","month_wuxing"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    return True


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_rows = []
    symbol_count = 0

    # 1. daily_quote (3 stocks + 4 indexes = 7)
    print("=== Daily Quote Symbols (3 stocks + 4 indexes) ===")
    dq_data = get_monthly_dailyquote()
    for code in sorted(dq_data):
        rows = calc_returns(dq_data[code])
        fname = os.path.join(OUTPUT_DIR, f"monthly_{code}.csv")
        if write_csv(fname, rows):
            print(f"  ✓ {code}: {len(rows)} months → monthly_{code}.csv")
            all_rows.extend(rows)
            symbol_count += 1

    # 2. sector_daily (31 Shenwan industries)
    print("\n=== Shenwan Industry Sectors (31) ===")
    sd_data = get_monthly_sector()
    for code in sorted(sd_data):
        rows = calc_returns(sd_data[code])
        fname = os.path.join(OUTPUT_DIR, f"monthly_{code}.csv")
        if write_csv(fname, rows):
            print(f"  ✓ {code}: {len(rows)} months → monthly_{code}.csv")
            all_rows.extend(rows)
            symbol_count += 1

    # 3. Consolidated
    all_fname = os.path.join(OUTPUT_DIR, "all_monthly.csv")
    write_csv(all_fname, all_rows)
    print(f"\n{'='*50}")
    print(f"Total: {symbol_count} symbols, {len(all_rows)} monthly observations")
    print(f"Output in: {OUTPUT_DIR}")
    print(f"  - {symbol_count} individual monthly_*.csv files")
    print(f"  - all_monthly.csv (consolidated, {len(all_rows)} rows)")


if __name__ == "__main__":
    main()
