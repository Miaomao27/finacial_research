#!/usr/bin/env python3
"""
T1: Data Preparation — Monthly aggregation + Ganzhi-Wuxing annotation

Extracts 38 symbols (3 stocks + 4 indexes from daily_quote, 31 Shenwan industries
from sector_daily), computes monthly close→close returns, annotates with Chinese
Five Elements (Wuxing) from trade_calendar.

Output: data/monthly_{code}.csv per symbol + data/all_monthly.csv consolidated
"""

import subprocess
import csv
import os
import re
from collections import OrderedDict

DB_HOST = "192.168.31.29"
DB_USER = "finance_user"
DB_PASS = "Finance2026!"
DB_NAME = "china_finance_db"
OUTPUT_DIR = "/home/cpy/文档/金融数据库建立/关于五行的研究/五行月份持有期收益研究/data"

# Wuxing mappings
HEAVENLY_STEMS = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
HEAVENLY_WUXING = {
    "甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土",
    "庚":"金","辛":"金","壬":"水","癸":"水"
}
EARTHLY_BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
BRANCH_WUXING = {
    "子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火",
    "未":"土","申":"金","酉":"金","戌":"土","亥":"水"
}

def mysql_query(sql):
    """Run SQL via mysql CLI and return list of OrderedDict rows."""
    cmd = [
        "mysql", "-h", DB_HOST, "-u", DB_USER,
        f"-p{DB_PASS}", DB_NAME,
        "--batch", "--skip-column-names", "-e", sql
    ]
    # First run with column names to get headers
    header_cmd = [
        "mysql", "-h", DB_HOST, "-u", DB_USER,
        f"-p{DB_PASS}", DB_NAME, "-e", sql
    ]
    result = subprocess.run(header_cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"MySQL error: {result.stderr}")
    output = result.stdout.strip()
    if not output:
        return []
    
    lines = output.split("\n")
    if len(lines) < 2:
        return []
    
    headers = [h.strip() for h in lines[0].split("\t")]
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        vals = line.split("\t")
        row = OrderedDict()
        for i, h in enumerate(headers):
            row[h] = vals[i] if i < len(vals) else ""
        rows.append(row)
    return rows


def get_monthly_close_daily_quote():
    """
    Get monthly close prices for all symbols in daily_quote.
    Uses the last trading day of each calendar month.
    Returns dict: {symbol: [(month, close, date, month_ganzhi), ...]}
    """
    sql = """
    SELECT 
        d.证券代码 AS code,
        DATE_FORMAT(d.交易日期, '%Y-%m') AS month,
        d.收盘价 AS close,
        d.交易日期 AS trade_date,
        tc.月干支 AS month_ganzhi
    FROM daily_quote d
    JOIN trade_calendar tc ON d.交易日期 = tc.交易日期
    WHERE d.交易状态 = '正常'
      AND d.是否收盘 = 1
      AND tc.月干支 IS NOT NULL
      AND (
        d.交易日期 = (
          SELECT MAX(d2.交易日期)
          FROM daily_quote d2
          WHERE d2.证券代码 = d.证券代码
            AND d2.交易状态 = '正常'
            AND d2.是否收盘 = 1
            AND DATE_FORMAT(d2.交易日期, '%Y-%m') = DATE_FORMAT(d.交易日期, '%Y-%m')
        )
      )
    ORDER BY d.证券代码, d.交易日期;
    """
    rows = mysql_query(sql)
    result = {}
    for r in rows:
        code = r["code"]
        if code not in result:
            result[code] = []
        result[code].append(r)
    return result


def get_monthly_close_sector():
    """
    Get monthly close prices for all Shenwan industry sectors.
    """
    # First get latest name for each sector code
    name_sql = """
    WITH latest_name AS (
        SELECT 行业代码, 行业名称,
               ROW_NUMBER() OVER (PARTITION BY 行业代码 ORDER BY MAX(交易日期) DESC) as rn
        FROM sector_daily
        GROUP BY 行业代码, 行业名称
    )
    SELECT 行业代码, 行业名称 FROM latest_name WHERE rn=1;
    """
    name_rows = mysql_query(name_sql)
    code_to_name = {r["行业代码"]: r["行业名称"] for r in name_rows}
    
    sql = """
    SELECT 
        s.行业代码 AS code,
        s.行业名称 AS sector_name,
        DATE_FORMAT(s.交易日期, '%Y-%m') AS month,
        s.收盘价 AS close,
        s.交易日期 AS trade_date,
        tc.月干支 AS month_ganzhi
    FROM sector_daily s
    JOIN trade_calendar tc ON s.交易日期 = tc.交易日期
    WHERE s.是否收盘 = 1
      AND tc.月干支 IS NOT NULL
      AND (
        s.交易日期 = (
          SELECT MAX(s2.交易日期)
          FROM sector_daily s2
          WHERE s2.行业代码 = s.行业代码
            AND s2.是否收盘 = 1
            AND DATE_FORMAT(s2.交易日期, '%Y-%m') = DATE_FORMAT(s.交易日期, '%Y-%m')
        )
      )
    ORDER BY s.行业代码, s.交易日期;
    """
    rows = mysql_query(sql)
    result = {}
    for r in rows:
        code = r["code"]
        if code not in result:
            result[code] = []
        # Use latest name
        r["sector_name"] = code_to_name.get(code, r.get("sector_name", ""))
        result[code].append(r)
    return result


def parse_ganzhi(ganzhi):
    """Parse 月干支 like '甲子' into heavenly_stem and earthly_branch."""
    if not ganzhi or len(ganzhi) < 2:
        return "", ""
    stem = ganzhi[0]
    branch = ganzhi[1]
    return stem, branch


def process_symbol_monthly(records, is_sector=False):
    """
    Process monthly records for one symbol.
    Input: list of OrderedDict with keys: code, month, close, trade_date, month_ganzhi
    Returns: list of dicts with fields: month, ts_code, return, heavenly_stem, 
             earthly_branch, stem_wuxing, branch_wuxing, month_wuxing
    """
    result = []
    prev_close = None
    
    for i, r in enumerate(records):
        close_str = r["close"]
        try:
            close = float(close_str)
        except (ValueError, TypeError):
            prev_close = None
            continue
        
        month_ganzhi = r.get("month_ganzhi", "")
        stem, branch = parse_ganzhi(month_ganzhi)
        
        monthly_return = None
        if prev_close is not None and prev_close > 0:
            monthly_return = round(close / prev_close - 1, 6)
        
        row = {
            "month": r["month"],
            "ts_code": r["code"],
            "return": monthly_return,
            "heavenly_stem": stem,
            "earthly_branch": branch,
            "stem_wuxing": HEAVENLY_WUXING.get(stem, ""),
            "branch_wuxing": BRANCH_WUXING.get(branch, ""),
            "month_wuxing": BRANCH_WUXING.get(branch, ""),  # month wuxing = branch wuxing
        }
        result.append(row)
        
        prev_close = close
    
    return result


def write_csv(filename, rows):
    """Write rows (list of dicts) to CSV."""
    if not rows:
        print(f"  WARNING: No data for {filename}, skipping")
        return False
    
    fieldnames = ["month", "ts_code", "return", "heavenly_stem", 
                  "earthly_branch", "stem_wuxing", "branch_wuxing", "month_wuxing"]
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return True


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Get daily_quote data (3 stocks + 4 indexes = 7 symbols)
    print("=== Fetching daily_quote monthly close data ===")
    dq_data = get_monthly_close_daily_quote()
    print(f"  Found {len(dq_data)} symbols in daily_quote")
    for code, recs in dq_data.items():
        print(f"    {code}: {len(recs)} months")
    
    # 2. Get sector_daily data (31 Shenwan industries)
    print("\n=== Fetching sector_daily monthly close data ===")
    sd_data = get_monthly_close_sector()
    print(f"  Found {len(sd_data)} sectors")
    for code, recs in sorted(sd_data.items()):
        print(f"    {code}: {len(recs)} months")
    
    # 3. Process and write per-symbol CSVs
    print("\n=== Processing and writing CSVs ===")
    all_rows = []
    
    # Process daily_quote symbols
    for code, recs in sorted(dq_data.items()):
        rows = process_symbol_monthly(recs)
        filename = os.path.join(OUTPUT_DIR, f"monthly_{code}.csv")
        if write_csv(filename, rows):
            print(f"  ✓ {filename}: {len(rows)} months")
            all_rows.extend(rows)
    
    # Process sector symbols
    for code, recs in sorted(sd_data.items()):
        rows = process_symbol_monthly(recs, is_sector=True)
        filename = os.path.join(OUTPUT_DIR, f"monthly_{code}.csv")
        if write_csv(filename, rows):
            print(f"  ✓ {filename}: {len(rows)} months")
            all_rows.extend(rows)
    
    # 4. Write consolidated file
    all_filename = os.path.join(OUTPUT_DIR, "all_monthly.csv")
    if write_csv(all_filename, all_rows):
        print(f"\n✓ Consolidated: {all_filename}: {len(all_rows)} rows total")
    
    # 5. Summary
    symbols_count = len(dq_data) + len(sd_data)
    print(f"\n{'='*50}")
    print(f"Summary: {symbols_count} symbols, {len(all_rows)} total monthly observations")
    print(f"Output: {OUTPUT_DIR}/")
    print(f"  - monthly_*.csv per symbol ({symbols_count} files)")
    print(f"  - all_monthly.csv (consolidated)")


if __name__ == "__main__":
    main()
