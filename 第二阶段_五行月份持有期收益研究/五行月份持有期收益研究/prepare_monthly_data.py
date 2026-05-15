#!/usr/bin/env python3
"""
T1: Data Preparation — Daily line to monthly aggregation + Ganzhi/Wuxing annotation

Extracts 38 symbols (3 stocks + 4 indices + 31 Shenwan industries) from MySQL,
computes monthly returns (last-trading-day close / prev-month last close - 1),
annotates with heavenly stem, earthly branch, and wuxing labels from trade_calendar.

Outputs:
  - data/monthly_{code}.csv   — one file per symbol
  - data/all_monthly.csv      — consolidated table
"""

import pymysql
import pandas as pd
import os
import argparse

# ── DB Config ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host': '192.168.31.29',
    'user': 'finance_user',
    'password': 'Finance2026!',
    'database': 'china_finance_db',
    'charset': 'utf8mb4',
}

# ── Wuxing Mappings ──────────────────────────────────────────────────────────
HEAVENLY_STEM_WUXING = {
    '甲': 'Wood', '乙': 'Wood',
    '丙': 'Fire', '丁': 'Fire',
    '戊': 'Earth', '己': 'Earth',
    '庚': 'Metal', '辛': 'Metal',
    '壬': 'Water', '癸': 'Water',
}

EARTHLY_BRANCH_WUXING = {
    '子': 'Water', '丑': 'Earth',
    '寅': 'Wood', '卯': 'Wood',
    '辰': 'Earth', '巳': 'Fire',
    '午': 'Fire', '未': 'Earth',
    '申': 'Metal', '酉': 'Metal',
    '戌': 'Earth', '亥': 'Water',
}

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data'
)


def fetch_stock_index_data(conn):
    """Fetch daily close prices for 7 stock/index symbols + join trade_calendar."""
    query = """
    SELECT
        d.`证券代码` AS ts_code,
        d.`交易日期` AS trade_date,
        d.`收盘价` AS close,
        t.`月干支`,
        t.`年干支`
    FROM daily_quote d
    JOIN trade_calendar t ON d.`交易日期` = t.`交易日期`
    WHERE t.`是否交易日` = 1
      AND d.`是否收盘` = 1
    ORDER BY d.`证券代码`, d.`交易日期`
    """
    df = pd.read_sql(query, conn, parse_dates=['trade_date'])
    df['source'] = 'stock_index'
    return df


def fetch_sector_data(conn):
    """Fetch daily close prices for 31 Shenwan industry indices + join trade_calendar."""
    query = """
    SELECT
        s.`行业代码` AS ts_code,
        s.`交易日期` AS trade_date,
        s.`收盘价` AS close,
        t.`月干支`,
        t.`年干支`
    FROM sector_daily s
    JOIN trade_calendar t ON s.`交易日期` = t.`交易日期`
    WHERE t.`是否交易日` = 1
      AND s.`是否收盘` = 1
    ORDER BY s.`行业代码`, s.`交易日期`
    """
    df = pd.read_sql(query, conn, parse_dates=['trade_date'])
    df['source'] = 'sector'
    return df


def compute_monthly_returns(df):
    """
    For each symbol, find last-trading-day close of each month,
    then compute month-over-month return.
    """
    # Extract year/month from trade_date
    df['year'] = df['trade_date'].dt.year
    df['month'] = df['trade_date'].dt.month

    # Last trading day of each month per symbol
    last_day = df.loc[
        df.groupby(['ts_code', 'year', 'month'])['trade_date'].idxmax()
    ].copy()

    # Sort for shift
    last_day = last_day.sort_values(['ts_code', 'trade_date']).reset_index(drop=True)
    last_day['prev_close'] = last_day.groupby('ts_code')['close'].shift(1)
    last_day['return'] = last_day['close'] / last_day['prev_close'] - 1

    # Drop rows with no previous month
    last_day = last_day.dropna(subset=['return']).copy()

    # Parse ganzhi
    last_day['heavenly_stem'] = last_day['月干支'].str[0]
    last_day['earthly_branch'] = last_day['月干支'].str[1]

    # Map wuxing
    last_day['stem_wuxing'] = last_day['heavenly_stem'].map(HEAVENLY_STEM_WUXING)
    last_day['branch_wuxing'] = last_day['earthly_branch'].map(EARTHLY_BRANCH_WUXING)
    last_day['month_wuxing'] = last_day['branch_wuxing']  # month wuxing = branch wuxing

    # Format month label
    last_day['month'] = last_day['trade_date'].dt.strftime('%Y-%m')

    return last_day


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = pymysql.connect(**DB_CONFIG)
    print(f"Connected to {DB_CONFIG['host']}/{DB_CONFIG['database']}")

    # ── Fetch data ───────────────────────────────────────────────────────────
    stocks_df = fetch_stock_index_data(conn)
    sectors_df = fetch_sector_data(conn)
    print(f"  Stock/Index rows: {len(stocks_df):,}")
    print(f"  Sector rows:      {len(sectors_df):,}")

    all_df = pd.concat([stocks_df, sectors_df], ignore_index=True)
    print(f"  Total rows:       {len(all_df):,}")

    # ── Compute monthly returns ──────────────────────────────────────────────
    result = compute_monthly_returns(all_df)
    print(f"\nMonthly records: {len(result):,}")
    print(f"  Date range: {result['month'].min()} ~ {result['month'].max()}")

    # ── Output columns ───────────────────────────────────────────────────────
    output_cols = [
        'month', 'ts_code', 'return',
        'heavenly_stem', 'earthly_branch',
        'stem_wuxing', 'branch_wuxing', 'month_wuxing'
    ]

    # ── Write individual files ───────────────────────────────────────────────
    symbols = sorted(result['ts_code'].unique())
    print(f"\nWriting {len(symbols)} individual CSV files...")
    for code in symbols:
        sub = result[result['ts_code'] == code][output_cols].copy()
        # Sort by month
        sub = sub.sort_values('month')
        fname = f"monthly_{code}.csv"
        fpath = os.path.join(OUTPUT_DIR, fname)
        sub.to_csv(fpath, index=False, encoding='utf-8-sig')
        print(f"  {fname}  ({len(sub)} rows)")

    # ── Write consolidated table ─────────────────────────────────────────────
    all_out = result[output_cols].copy()
    all_out = all_out.sort_values(['ts_code', 'month'])
    all_path = os.path.join(OUTPUT_DIR, 'all_monthly.csv')
    all_out.to_csv(all_path, index=False, encoding='utf-8-sig')
    print(f"\nConsolidated: {all_path}  ({len(all_out)} rows)")

    # ── Summary stats ────────────────────────────────────────────────────────
    print("\n── Symbol breakdown ──")
    for code in symbols:
        sub = result[result['ts_code'] == code]
        print(f"  {code}: {len(sub)} months, "
              f"{sub['month'].min()} ~ {sub['month'].max()}")

    conn.close()
    print("\nDone!")


if __name__ == '__main__':
    main()
