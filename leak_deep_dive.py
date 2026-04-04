"""Deep dive: Too Passive vs Min-Cash Machine, and Can't Close analysis."""

import csv
import numpy as np
from collections import Counter
from stake_move_model import TIERS, TIER_ORDER, calc_ev
from leak_analysis import classify_leak, get_evs


def load_and_classify():
    players = []
    with open("synthetic_players_100k.csv", "r") as f:
        for row in csv.DictReader(f):
            p = {
                "id": int(row["id"]), "tier": row["tier"],
                "tournaments": int(row["tournaments"]),
                "1st": int(row["1st"]), "2nd": int(row["2nd"]), "3rd": int(row["3rd"]),
                "4th-9th": int(row["4th-9th"]), "10th+": int(row["10th+"]),
                "total_cashes": int(row["total_cashes"]),
                "cash_rate": float(row["cash_rate"]), "ft_rate": float(row["ft_rate"]),
                "top3_conv": float(row["top3_conv"]),
                "aggression": float(row.get("aggression", 0.5)),
            }
            evs = get_evs(p)
            if evs:
                p["classification"] = classify_leak(p, evs)
                p["ev_low"] = evs["low"]
                players.append(p)
    return players


def main():
    players = load_and_classify()

    passive = [p for p in players if p["classification"] == "Leak: Too Passive"]
    mincash = [p for p in players if p["classification"] == "Leak: Min-Cash Machine"]
    cantclose = [p for p in players if p["classification"] == "Leak: Can't Close"]
    complete = [p for p in players if p["classification"] == "Strength: Complete Player"]

    # ══════════════════════════════════════════════════════════
    print("=" * 70)
    print("TOO PASSIVE vs MIN-CASH MACHINE — Are they the same?")
    print("=" * 70)

    stats = [
        ("Count", len(passive), len(mincash), "d"),
        ("Cash Rate", np.mean([p["cash_rate"] for p in passive]),
         np.mean([p["cash_rate"] for p in mincash]), "%"),
        ("Aggression", np.mean([p["aggression"] for p in passive]),
         np.mean([p["aggression"] for p in mincash]), "f"),
        ("FT Rate", np.mean([p["ft_rate"] for p in passive]),
         np.mean([p["ft_rate"] for p in mincash]), "%"),
        ("Top-3 Conv", np.mean([p["top3_conv"] for p in passive]),
         np.mean([p["top3_conv"] for p in mincash]), "%"),
        ("FT/Cash Ratio",
         np.mean([p["ft_rate"] / p["cash_rate"] for p in passive if p["cash_rate"] > 0]),
         np.mean([p["ft_rate"] / p["cash_rate"] for p in mincash if p["cash_rate"] > 0]), "%"),
        ("Min-Cash %",
         np.mean([p["10th+"] / max(1, p["total_cashes"]) for p in passive]),
         np.mean([p["10th+"] / max(1, p["total_cashes"]) for p in mincash]), "%"),
        ("Avg EV", np.mean([p["ev_low"] for p in passive]),
         np.mean([p["ev_low"] for p in mincash]), "$"),
        ("Avg Tournaments", np.mean([p["tournaments"] for p in passive]),
         np.mean([p["tournaments"] for p in mincash]), "d"),
    ]

    print(f"\n{'Stat':>20s} | {'Too Passive':>15s} | {'Min-Cash':>15s} | {'Delta':>12s}")
    print("-" * 70)
    for label, v1, v2, fmt in stats:
        if fmt == "%":
            print(f"{label:>20s} | {v1:>14.1%}  | {v2:>14.1%}  | {v2-v1:>+11.1%} ")
        elif fmt == "f":
            print(f"{label:>20s} | {v1:>15.2f} | {v2:>15.2f} | {v2-v1:>+12.2f}")
        elif fmt == "$":
            print(f"{label:>20s} | ${v1:>13,.0f} | ${v2:>13,.0f} | ${v2-v1:>+11,.0f}")
        else:
            print(f"{label:>20s} | {v1:>15,.0f} | {v2:>15,.0f} | {v2-v1:>+12,.0f}")

    # Overlap test
    print("\nOVERLAP:")
    p_crs = [p["cash_rate"] for p in passive]
    m_crs = [p["cash_rate"] for p in mincash]
    p_aggs = [p["aggression"] for p in passive]
    m_aggs = [p["aggression"] for p in mincash]
    print(f"  Too Passive:  CR P10-P90 = {np.percentile(p_crs,10):.1%} - {np.percentile(p_crs,90):.1%}"
          f"  |  Agg P10-P90 = {np.percentile(p_aggs,10):.2f} - {np.percentile(p_aggs,90):.2f}")
    print(f"  Min-Cash:     CR P10-P90 = {np.percentile(m_crs,10):.1%} - {np.percentile(m_crs,90):.1%}"
          f"  |  Agg P10-P90 = {np.percentile(m_aggs,10):.2f} - {np.percentile(m_aggs,90):.2f}")

    # Key difference
    print("\nKEY DIFFERENCE:")
    p_ft_cash = [p["ft_rate"] / p["cash_rate"] for p in passive if p["cash_rate"] > 0]
    m_ft_cash = [p["ft_rate"] / p["cash_rate"] for p in mincash if p["cash_rate"] > 0]
    print(f"  Too Passive FT/Cash:  P10={np.percentile(p_ft_cash,10):.0%}  Median={np.median(p_ft_cash):.0%}  P90={np.percentile(p_ft_cash,90):.0%}")
    print(f"  Min-Cash FT/Cash:     P10={np.percentile(m_ft_cash,10):.0%}  Median={np.median(m_ft_cash):.0%}  P90={np.percentile(m_ft_cash,90):.0%}")

    # Source tiers
    print("\nSource Tiers:")
    for label, group in [("Too Passive", passive), ("Min-Cash Machine", mincash)]:
        tc = Counter(p["tier"] for p in group)
        tiers_str = ", ".join(f"{t} {c/len(group):.0%}" for t, c in tc.most_common(4))
        print(f"  {label}: {tiers_str}")

    # ══════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("CAN'T CLOSE — What's happening at the final table?")
    print("=" * 70)
    print(f"\nTotal: {len(cantclose):,} players")

    # Break down by aggression at FT
    for lo, hi, label in [(0.0, 0.35, "Passive at FT (agg < 0.35)"),
                           (0.35, 0.55, "Balanced at FT (0.35-0.55)"),
                           (0.55, 1.0, "Aggressive at FT (agg > 0.55)")]:
        sub = [p for p in cantclose if lo <= p["aggression"] < hi]
        if not sub:
            continue
        n = len(sub)
        pct = n / len(cantclose)

        # FT placement breakdown
        ft_totals = [p["1st"] + p["2nd"] + p["3rd"] + p["4th-9th"] for p in sub]
        first_rates = [p["1st"] / max(1, ft) for p, ft in zip(sub, ft_totals)]
        second_rates = [p["2nd"] / max(1, ft) for p, ft in zip(sub, ft_totals)]
        third_rates = [p["3rd"] / max(1, ft) for p, ft in zip(sub, ft_totals)]
        bubble_rates = [p["4th-9th"] / max(1, ft) for p, ft in zip(sub, ft_totals)]

        print(f"\n  {label}: {n:,} ({pct:.0%} of all)")
        print(f"    CR: {np.mean([p['cash_rate'] for p in sub]):.1%}"
              f"  FT: {np.mean([p['ft_rate'] for p in sub]):.1%}"
              f"  T3C: {np.mean([p['top3_conv'] for p in sub]):.1%}"
              f"  Agg: {np.mean([p['aggression'] for p in sub]):.2f}")
        print(f"    At FT they finish:")
        print(f"      1st: {np.mean(first_rates):.0%}  2nd: {np.mean(second_rates):.0%}"
              f"  3rd: {np.mean(third_rates):.0%}  4th-9th: {np.mean(bubble_rates):.0%}")
        print(f"    EV: ${np.mean([p['ev_low'] for p in sub]):+,.0f}")

    # Compare to Complete Players
    if complete:
        ft_totals_c = [p["1st"] + p["2nd"] + p["3rd"] + p["4th-9th"] for p in complete]
        print(f"\n  COMPARISON — Complete Players at FT:")
        print(f"    1st: {np.mean([p['1st']/max(1,ft) for p,ft in zip(complete,ft_totals_c)]):.0%}"
              f"  2nd: {np.mean([p['2nd']/max(1,ft) for p,ft in zip(complete,ft_totals_c)]):.0%}"
              f"  3rd: {np.mean([p['3rd']/max(1,ft) for p,ft in zip(complete,ft_totals_c)]):.0%}"
              f"  4th-9th: {np.mean([p['4th-9th']/max(1,ft) for p,ft in zip(complete,ft_totals_c)]):.0%}")

    # Source tiers
    print(f"\n  Source Tiers:")
    tc = Counter(p["tier"] for p in cantclose)
    for tier, count in tc.most_common():
        print(f"    {tier:>22s}: {count:>5,d} ({count/len(cantclose):.0%})")

    # The real question: what distinguishes them?
    print(f"\n  THE REAL QUESTION: Why can't they close?")

    # Look at T3 conv by aggression more granularly
    low_t3 = [p for p in cantclose if p["top3_conv"] < 0.15]
    med_t3 = [p for p in cantclose if 0.15 <= p["top3_conv"] < 0.25]
    print(f"\n  Ultra-low T3C (<15%): {len(low_t3):,} players")
    if low_t3:
        print(f"    Avg agg: {np.mean([p['aggression'] for p in low_t3]):.2f}"
              f"  Avg CR: {np.mean([p['cash_rate'] for p in low_t3]):.1%}"
              f"  Avg FT rate: {np.mean([p['ft_rate'] for p in low_t3]):.1%}")
        # Are they busting 4th-9th or just not winning?
        ft_t = [p["1st"]+p["2nd"]+p["3rd"]+p["4th-9th"] for p in low_t3]
        avg_49 = np.mean([p["4th-9th"]/max(1,ft) for p,ft in zip(low_t3, ft_t)])
        print(f"    4th-9th rate at FT: {avg_49:.0%} (they bubble)")

    print(f"\n  Low T3C (15-25%): {len(med_t3):,} players")
    if med_t3:
        print(f"    Avg agg: {np.mean([p['aggression'] for p in med_t3]):.2f}"
              f"  Avg CR: {np.mean([p['cash_rate'] for p in med_t3]):.1%}"
              f"  Avg FT rate: {np.mean([p['ft_rate'] for p in med_t3]):.1%}")
        ft_t = [p["1st"]+p["2nd"]+p["3rd"]+p["4th-9th"] for p in med_t3]
        avg_49 = np.mean([p["4th-9th"]/max(1,ft) for p,ft in zip(med_t3, ft_t)])
        print(f"    4th-9th rate at FT: {avg_49:.0%} (they bubble)")


if __name__ == "__main__":
    main()
