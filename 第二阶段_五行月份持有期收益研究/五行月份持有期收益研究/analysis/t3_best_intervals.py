#!/usr/bin/env python3
"""
T3: Best Interval Mining — Top 10 (wuxing × holding_period) per stock + cross-stock consistency

Reads T2's summary.csv and per-stock monthly data for ganzhi info.
Outputs:
  - best_intervals.csv — per-stock top 10 intervals with buy/sell ganzhi
  - consistency.csv — cross-stock consistency analysis
  - conclusion.txt — text summary
"""

import csv
import os
import sys
from collections import defaultdict, Counter
import calendar

ANALYSIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(ANALYSIS_DIR), "data")
SUMMARY_PATH = os.path.join(ANALYSIS_DIR, "summary.csv")
BEST_INTERVALS_PATH = os.path.join(ANALYSIS_DIR, "best_intervals.csv")
CONSISTENCY_PATH = os.path.join(ANALYSIS_DIR, "consistency.csv")
CONCLUSION_PATH = os.path.join(ANALYSIS_DIR, "conclusion.txt")

HOLDING_COLS = ["hold_1m", "hold_2m", "hold_3m", "hold_6m", "hold_9m", "hold_12m", "hold_24m"]
HOLDING_LABELS = {f"hold_{k}m": (k, f"{k}个月") for k in [1, 2, 3, 6, 9, 12, 24]}

# ── 1. Load monthly ganzhi data ──────────────────────────────────
def load_month_ganzhi():
    """
    Read per-stock monthly CSVs to build a map:
      (ts_code, month) -> {
        heavenly_stem, earthly_branch, stem_wuxing, branch_wuxing, month_wuxing
      }
    """
    monthly_dir = DATA_DIR
    ganzhi_map = {}  # (ts_code, month) -> dict

    for fname in os.listdir(monthly_dir):
        if not fname.startswith("monthly_") or not fname.endswith(".csv"):
            continue
        ts_code = fname.replace("monthly_", "").replace(".csv", "")
        fpath = os.path.join(monthly_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                month = row["month"].strip()
                if not month:
                    continue
                key = (ts_code, month)
                ganzhi_map[key] = {
                    "heavenly_stem": row.get("heavenly_stem", "").strip(),
                    "earthly_branch": row.get("earthly_branch", "").strip(),
                    "stem_wuxing": row.get("stem_wuxing", "").strip(),
                    "branch_wuxing": row.get("branch_wuxing", "").strip(),
                    "month_wuxing": row.get("month_wuxing", "").strip(),
                }
        print(f"  Loaded {fname}: {sum(1 for k in ganzhi_map if k[0] == ts_code)} months")
    return ganzhi_map


def add_months(ym_str, n):
    """Add n months to a YYYY-MM string, return YYYY-MM."""
    year, month = int(ym_str[:4]), int(ym_str[5:7])
    total = year * 12 + (month - 1) + n
    y = total // 12
    m = (total % 12) + 1
    return f"{y:04d}-{m:02d}"


def get_ganzhi_tag(ganzhi_map, ts_code, month):
    """Return a short tag like '甲子(木)' from the ganzhi map."""
    info = ganzhi_map.get((ts_code, month))
    if info:
        stem = info["heavenly_stem"]
        branch = info["earthly_branch"]
        wx = info["month_wuxing"]
        return f"{stem}{branch}({wx})"
    return f"??(?)"


# ── 2. Build per-stock top-10 ──────────────────────────────────
def build_best_intervals(summary_path, ganzhi_map):
    """
    For each stock, find top 10 (entry_month, month_wuxing, holding) by return.
    """
    # Read summary.csv
    stock_rows = defaultdict(list)
    ts_codes_seen = set()

    with open(summary_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts_code = row["ts_code"].strip()
            entry_month = row["entry_month"].strip()
            month_wuxing = row["month_wuxing"].strip()
            ts_codes_seen.add(ts_code)
            for hcol in HOLDING_COLS:
                val_str = row[hcol].strip()
                try:
                    val = float(val_str)
                except (ValueError, TypeError):
                    continue
                if hcol in HOLDING_LABELS:
                    hold_months, _ = HOLDING_LABELS[hcol]
                    sell_month = add_months(entry_month, hold_months)
                    stock_rows[ts_code].append({
                        "entry_month": entry_month,
                        "month_wuxing": month_wuxing,
                        "holding_months": hold_months,
                        "sell_month": sell_month,
                        "return": val,
                    })

    # For each stock, sort by return descending, take top 10
    best_rows = []
    for ts_code in sorted(stock_rows.keys()):
        rows = stock_rows[ts_code]
        rows.sort(key=lambda r: -r["return"])
        top10 = rows[:10]

        for rank, r in enumerate(top10, 1):
            buy_tag = get_ganzhi_tag(ganzhi_map, ts_code, r["entry_month"])
            sell_tag = get_ganzhi_tag(ganzhi_map, ts_code, r["sell_month"])
            best_rows.append({
                "ts_code": ts_code,
                "rank": rank,
                "entry_month": r["entry_month"],
                "buy_ganzhi": buy_tag,
                "buy_wuxing": r["month_wuxing"],
                "holding_months": r["holding_months"],
                "sell_month": r["sell_month"],
                "sell_ganzhi": sell_tag,
                "return": r["return"],
            })

    return best_rows, ts_codes_seen


# ── 3. Cross-stock consistency ──────────────────────────────────
def build_consistency(summary_path, best_rows):
    """
    For each (wuxing, holding_months) combination, count how many stocks
    have it in their top 10, and the average rank and return.
    Also compute total instances across all summary rows.
    """
    # Count how many stocks total
    all_stocks = set(r["ts_code"] for r in best_rows)
    n_stocks = len(all_stocks)

    # For each (wuxing, hold), collect rank and return across all stocks' top-10
    combo_data = defaultdict(list)
    for r in best_rows:
        key = (r["buy_wuxing"], r["holding_months"])
        combo_data[key].append({
            "stock": r["ts_code"],
            "rank": r["rank"],
            "return": r["return"],
        })

    # Total instances of each combo in full data
    combo_total_count = defaultdict(int)
    with open(summary_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            wx = row["month_wuxing"].strip()
            for hcol in HOLDING_COLS:
                if hcol in HOLDING_LABELS:
                    hm, _ = HOLDING_LABELS[hcol]
                    combo_total_count[(wx, hm)] += 1

    consistency_rows = []
    for (wx, hm), entries in sorted(combo_data.items()):
        stocks_with = set(e["stock"] for e in entries)
        cover_ratio = len(stocks_with) / n_stocks * 100
        avg_rank = sum(e["rank"] for e in entries) / len(entries)
        avg_return = sum(e["return"] for e in entries) / len(entries)
        total_instances = combo_total_count.get((wx, hm), 0)
        pick_rate = len(entries) / total_instances * 100 if total_instances > 0 else 0

        consistency_rows.append({
            "wuxing": wx,
            "holding_months": hm,
            "stocks_in_top10": len(stocks_with),
            "total_stocks": n_stocks,
            "coverage_pct": round(cover_ratio, 1),
            "total_instances": total_instances,
            "top10_entries": len(entries),
            "pick_rate_pct": round(pick_rate, 1),
            "avg_rank": round(avg_rank, 2),
            "avg_return": round(avg_return, 4),
        })

    consistency_rows.sort(key=lambda r: (-r["stocks_in_top10"], r["avg_rank"]))
    return consistency_rows


# ── 4. Write outputs ──────────────────────────────────────────
def write_best_intervals(rows, path):
    fieldnames = [
        "ts_code", "rank", "entry_month", "buy_ganzhi", "buy_wuxing",
        "holding_months", "sell_month", "sell_ganzhi", "return"
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"  Written: {path} ({len(rows)} rows)")


def write_consistency(rows, path):
    fieldnames = [
        "wuxing", "holding_months", "stocks_in_top10", "total_stocks",
        "coverage_pct", "total_instances", "top10_entries", "pick_rate_pct",
        "avg_rank", "avg_return"
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"  Written: {path} ({len(rows)} rows)")


def write_conclusion(best_rows, consistency_rows, n_stocks, ts_codes_seen, path):
    lines = []
    lines.append("=" * 70)
    lines.append("T3 最优区间挖掘 — 结论摘要")
    lines.append("=" * 70)
    lines.append(f"分析范围：{n_stocks}个标的，涵盖{len(ts_codes_seen)}个时间序列")
    lines.append(f"持有期选项：1/2/3/6/9/12/24个月")
    lines.append(f"五行属性：木火土金水")
    lines.append("")

    # ── Top combos across all stocks ──
    lines.append("─" * 70)
    lines.append("一、跨标的一直性最强组合（覆盖最多标的）")
    lines.append("─" * 70)
    top_consistency = consistency_rows[:10]
    header = f"{'五行':>4} | {'持有期':>6} | {'覆盖标的':>8} | {'覆盖率':>6} | {'选取率':>7} | {'平均排名':>8} | {'平均收益':>9}"
    lines.append(header)
    lines.append("-" * len(header))
    for r in top_consistency:
        lines.append(
            f"{r['wuxing']:>4} | {r['holding_months']:>4}个月 | "
            f"{r['stocks_in_top10']:>3}/{r['total_stocks']:>3} | "
            f"{r['coverage_pct']:>5.1f}% | "
            f"{r['pick_rate_pct']:>5.1f}% | "
            f"{r['avg_rank']:>8.2f} | "
            f"{r['avg_return']:>+9.2%}"
        )

    lines.append("")
    lines.append("─" * 70)
    lines.append("二、各标的Top1最优区间速览")
    lines.append("─" * 70)
    # For each stock, show rank 1
    stock_top1 = {}
    for r in best_rows:
        if r["rank"] == 1:
            stock_top1[r["ts_code"]] = r
    header2 = f"{'标的':>12} | {'买入月':>10} | {'买入干支':>12} | {'买入五行':>6} | {'持有':>4} | {'卖出月':>10} | {'卖出干支':>12} | {'收益率':>9}"
    lines.append(header2)
    lines.append("-" * len(header2))
    for ts_code in sorted(stock_top1.keys()):
        r = stock_top1[ts_code]
        lines.append(
            f"{r['ts_code']:>12} | {r['entry_month']:>10} | {r['buy_ganzhi']:>12} | "
            f"{r['buy_wuxing']:>6} | {r['holding_months']:>3}个月 | "
            f"{r['sell_month']:>10} | {r['sell_ganzhi']:>12} | {r['return']:>+8.2%}"
        )

    # ── Key findings ──
    lines.append("")
    lines.append("─" * 70)
    lines.append("三、关键发现")
    lines.append("─" * 70)

    if consistency_rows:
        best_combo = consistency_rows[0]
        lines.append(f"1. 最稳定的跨标组合：{best_combo['wuxing']}×{best_combo['holding_months']}个月，"
                      f"覆盖{best_combo['stocks_in_top10']}/{best_combo['total_stocks']}个标的"
                      f"（{best_combo['coverage_pct']}%），"
                      f"平均排名{best_combo['avg_rank']:.2f}，"
                      f"平均收益{best_combo['avg_return']:+.2%}")

        # Check if any combo covers > 50% stocks
        high_cover = [r for r in consistency_rows if r["coverage_pct"] >= 50]
        if high_cover:
            lines.append(f"2. 覆盖率≥50%的组合共{len(high_cover)}个：")
            for r in high_cover[:5]:
                lines.append(f"   · {r['wuxing']}×{r['holding_months']}月 "
                              f"(覆盖{r['coverage_pct']}%，均排名{r['avg_rank']:.1f})")
        else:
            lines.append(f"2. 无单个组合覆盖超过50%标的，最佳覆盖率仅{best_combo['coverage_pct']}%")

        # Wuxing ranking
        wx_avg = defaultdict(list)
        for r in consistency_rows:
            wx_avg[r["wuxing"]].append(r["avg_rank"])
        wx_ranking = sorted(
            [(wx, sum(v)/len(v)) for wx, v in wx_avg.items()],
            key=lambda x: x[1]
        )
        lines.append(f"3. 五行平均排名（越低越好）：{' → '.join(f'{wx}({rank:.1f})' for wx, rank in wx_ranking)}")

        # Holding period ranking
        hp_avg = defaultdict(list)
        for r in consistency_rows:
            hp_avg[r["holding_months"]].append(r["avg_rank"])
        hp_ranking = sorted(
            [(hp, sum(v)/len(v)) for hp, v in hp_avg.items()],
            key=lambda x: x[1]
        )
        lines.append(f"4. 持有期平均排名（越低越好）：{' → '.join(f'{hp}月({rank:.1f})' for hp, rank in hp_ranking)}")

    lines.append("")
    lines.append("─" * 70)
    lines.append("四、注意事项")
    lines.append("─" * 70)
    lines.append("1. 年化收益率在短持有期（1-3月）被极端放大——实际月收益率才是可比指标")
    lines.append("2. 短持有期Top10收益多来自单月异常行情（如2015牛市、2020疫情反弹），非稳定规律")
    lines.append("3. 长持有期（12-24月）收益更平稳但绝对值低，需结合年化收益率判断")
    lines.append("4. 选取率(pick_rate)反映该组合在所有实例中进入Top10的比例，"
                 "低选取率+高覆盖率意味着该组合在部分标的上表现极好而在其他标的平庸")
    lines.append("5. 建议结合T2的stats.csv中位数进行验证——中位数更能代表一般情况")

    conclusion = "\n".join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(conclusion)
    print(f"  Written: {path} ({len(lines)} lines)")
    return conclusion


# ── Main ──────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("T3: 最优区间挖掘")
    print("=" * 60)

    print("\n[1/4] Loading per-stock monthly ganzhi data...")
    ganzhi_map = load_month_ganzhi()
    n_months = len(set(m for (_, m) in ganzhi_map.keys()))
    print(f"  Loaded {len(ganzhi_map)} entries across {n_months} months")

    print("\n[2/4] Building per-stock best intervals (Top10 per stock)...")
    best_rows, ts_codes_seen = build_best_intervals(SUMMARY_PATH, ganzhi_map)
    n_stocks = len(set(r["ts_code"] for r in best_rows))
    print(f"  Found {len(best_rows)} top-10 entries across {n_stocks} stocks")
    print(f"  Stocks: {', '.join(sorted(ts_codes_seen))}")

    print("\n[3/4] Computing cross-stock consistency...")
    consistency_rows = build_consistency(SUMMARY_PATH, best_rows)
    print(f"  {len(consistency_rows)} unique (wuxing × holding_period) combinations ranked")

    print("\n[4/4] Writing output files...")
    write_best_intervals(best_rows, BEST_INTERVALS_PATH)
    write_consistency(consistency_rows, CONSISTENCY_PATH)
    conclusion = write_conclusion(best_rows, consistency_rows, n_stocks, ts_codes_seen, CONCLUSION_PATH)

    print("\n" + "=" * 60)
    print("DONE — T3 analysis complete")
    print(f"  {BEST_INTERVALS_PATH}")
    print(f"  {CONSISTENCY_PATH}")
    print(f"  {CONCLUSION_PATH}")
    print()

    # ── Print conclusion to stdout ──
    print(conclusion)


if __name__ == "__main__":
    main()
