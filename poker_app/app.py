"""Poker Development Platform — MVP Web App.

Free tier: CSV import, leak classification, stake move recommendation.
"""

import os
import csv
import io
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stake_move_model import (
    TIERS, TIER_ORDER, project_cash_rate, project_ft_rate,
    project_placements, calc_ev, apply_aggression, estimate_aggression,
    normalize_placements,
)
from leak_analysis import classify_leak, get_evs

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-key-change-in-prod")

# In-memory store for MVP (swap for Postgres in production)
users: dict[str, dict] = {}


def parse_csv(file_content: str) -> list[dict]:
    """Parse uploaded CSV into tournament results.

    Supports formats from Poker Bankroll Tracker, Poker Analytics,
    and our own simple format.

    Minimum fields: buy_in, finish_position, payout
    Optional: date, field_size, venue
    """
    reader = csv.DictReader(io.StringIO(file_content))
    results = []

    # Normalize column names (different apps use different names)
    column_map = {
        "buy_in": ["buy_in", "buyin", "buy-in", "entry", "cost", "expense"],
        "payout": ["payout", "cashout", "prize", "winnings", "profit"],
        "finish": ["finish", "finish_position", "position", "place", "result"],
        "field_size": ["field_size", "field", "entries", "players", "entrants"],
        "date": ["date", "session_date", "tournament_date"],
        "venue": ["venue", "location", "casino", "room"],
    }

    def find_column(row, field):
        for alias in column_map.get(field, []):
            for key in row.keys():
                if key.strip().lower().replace(" ", "_") == alias:
                    return row[key]
        return None

    for row in reader:
        try:
            buy_in = find_column(row, "buy_in")
            payout = find_column(row, "payout")
            finish = find_column(row, "finish")

            if buy_in is None or payout is None:
                continue

            buy_in = float(str(buy_in).replace("$", "").replace(",", "").strip())
            payout = float(str(payout).replace("$", "").replace(",", "").strip())

            if finish:
                finish = int(str(finish).strip())
            else:
                finish = None

            field_size = find_column(row, "field_size")
            if field_size:
                field_size = int(str(field_size).strip())
            else:
                field_size = None

            date = find_column(row, "date")
            venue = find_column(row, "venue")

            results.append({
                "buy_in": buy_in,
                "payout": payout,
                "finish": finish,
                "field_size": field_size,
                "date": date,
                "venue": venue,
                "profit": payout - buy_in,
            })
        except (ValueError, TypeError):
            continue

    return results


def analyze_results(results: list[dict]) -> dict:
    """Analyze tournament results and classify the player."""
    if not results:
        return {"error": "No valid results to analyze"}

    tournaments = len(results)
    total_buyin = sum(r["buy_in"] for r in results)
    total_payout = sum(r["payout"] for r in results)
    total_profit = total_payout - total_buyin

    # Estimate field sizes where missing
    avg_buyin = total_buyin / tournaments
    for r in results:
        if not r["field_size"]:
            if avg_buyin <= 100:
                r["field_size"] = 80
            elif avg_buyin <= 200:
                r["field_size"] = 100
            elif avg_buyin <= 300:
                r["field_size"] = 150
            else:
                r["field_size"] = 250

    avg_field = sum(r["field_size"] for r in results) / tournaments

    # Calculate placements
    cashes = [r for r in results if r["payout"] > 0]
    cash_rate = len(cashes) / tournaments

    # Classify finishes into placement buckets
    first = 0
    second = 0
    third = 0
    fourth_ninth = 0
    tenth_plus = 0

    for r in results:
        if r["payout"] <= 0:
            continue
        if r["finish"]:
            if r["finish"] == 1:
                first += 1
            elif r["finish"] == 2:
                second += 1
            elif r["finish"] == 3:
                third += 1
            elif r["finish"] <= 9:
                fourth_ninth += 1
            else:
                tenth_plus += 1
        else:
            # No finish position — estimate from payout relative to buy-in
            ratio = r["payout"] / max(1, r["buy_in"])
            if ratio >= 15:
                first += 1
            elif ratio >= 10:
                second += 1
            elif ratio >= 6:
                third += 1
            elif ratio >= 3:
                fourth_ninth += 1
            else:
                tenth_plus += 1

    total_cashes = first + second + third + fourth_ninth + tenth_plus
    ft_count = first + second + third + fourth_ninth
    ft_rate = ft_count / tournaments if tournaments > 0 else 0
    top3_conv = (first + second + third) / max(1, ft_count)
    mincash_pct = tenth_plus / max(1, total_cashes)

    # Estimate aggression from stats
    aggression = estimate_aggression(cash_rate, ft_rate, top3_conv, field_normalized=False)

    # Build player dict for model
    player = {
        "name": "You",
        "tournaments": tournaments,
        "cash_rate": cash_rate,
        "1st": first,
        "2nd": second,
        "3rd": third,
        "4th-9th": fourth_ninth,
        "10th+": tenth_plus,
        "ft_rate": ft_rate,
        "top3_conv": top3_conv,
        "total_cashes": total_cashes,
        "aggression": aggression,
        "current_tier": "low",
    }

    # Normalize for field size
    normalized = normalize_placements(player, avg_field_size=avg_field, target_field_size=250)
    normalized["total_cashes"] = (normalized["1st"] + normalized["2nd"] + normalized["3rd"]
                                   + normalized["4th-9th"] + normalized["10th+"])

    # Get EVs at all tiers
    evs = get_evs_for_player(normalized)

    # Classify leak
    leak = classify_leak(normalized, evs)

    # Stake recommendation
    best_tier = max(evs, key=lambda k: evs[k])
    best_ev = evs[best_tier]

    # Population percentile (rough estimate based on cash rate)
    if cash_rate >= 0.30:
        percentile = 95
    elif cash_rate >= 0.25:
        percentile = 88
    elif cash_rate >= 0.20:
        percentile = 78
    elif cash_rate >= 0.15:
        percentile = 60
    elif cash_rate >= 0.12:
        percentile = 45
    elif cash_rate >= 0.08:
        percentile = 25
    else:
        percentile = 10

    return {
        "tournaments": tournaments,
        "total_buyin": round(total_buyin),
        "total_payout": round(total_payout),
        "total_profit": round(total_profit),
        "roi": round((total_profit / total_buyin) * 100, 1) if total_buyin > 0 else 0,
        "cash_rate": round(cash_rate, 4),
        "ft_rate": round(ft_rate, 4),
        "top3_conv": round(top3_conv, 4),
        "mincash_pct": round(mincash_pct, 4),
        "aggression": round(aggression, 2),
        "placements": {
            "1st": first, "2nd": second, "3rd": third,
            "4th-9th": fourth_ninth, "10th+": tenth_plus,
        },
        "normalized_placements": {
            "1st": normalized["1st"], "2nd": normalized["2nd"],
            "3rd": normalized["3rd"], "4th-9th": normalized["4th-9th"],
            "10th+": normalized["10th+"],
        },
        "avg_field_size": round(avg_field),
        "classification": leak,
        "ev_by_tier": {TIERS[k]["label"]: round(evs[k]) for k in TIER_ORDER},
        "best_tier": TIERS[best_tier]["label"],
        "best_ev": round(best_ev),
        "percentile": percentile,
        "sample_reliable": tournaments >= 200,
    }


def get_evs_for_player(p):
    """Calculate EVs at all tiers."""
    t = p["tournaments"]
    agg = p.get("aggression", 0.5)
    current_placements = {
        "1st": p["1st"], "2nd": p["2nd"], "3rd": p["3rd"],
        "4th-9th": p["4th-9th"], "10th+": p["10th+"],
    }

    evs = {}
    for i, tier_key in enumerate(TIER_ORDER):
        tier = TIERS[tier_key]
        if i == 0:
            placements = current_placements
        else:
            cr = project_cash_rate(p["cash_rate"], i, aggression=agg)
            ft = project_ft_rate(p["ft_rate"], p["cash_rate"], cr)
            placements = project_placements(p, cr, ft, aggression=agg)
        evs[tier_key] = calc_ev(placements, t, tier["payouts"], tier["buyin"])
    return evs


# ── Routes ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Analyze uploaded CSV or manual entry."""
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        content = file.read().decode("utf-8")
        results = parse_csv(content)
    elif request.is_json:
        data = request.get_json()
        results = data.get("results", [])
    else:
        return jsonify({"error": "No data provided"}), 400

    if not results:
        return jsonify({"error": "No valid tournament results found"}), 400

    analysis = analyze_results(results)
    return jsonify(analysis)


@app.route("/api/quick-assess", methods=["POST"])
def quick_assess():
    """Quick assessment from manual stats entry (no CSV needed)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    tournaments = int(data.get("tournaments", 0))
    cash_rate = float(data.get("cash_rate", 0))
    first = int(data.get("first", 0))
    second = int(data.get("second", 0))
    third = int(data.get("third", 0))
    fourth_ninth = int(data.get("fourth_ninth", 0))
    tenth_plus = int(data.get("tenth_plus", 0))
    avg_field = int(data.get("avg_field_size", 150))

    if tournaments <= 0:
        return jsonify({"error": "Need at least 1 tournament"}), 400

    total_cashes = first + second + third + fourth_ninth + tenth_plus
    if total_cashes == 0 and cash_rate > 0:
        total_cashes = round(tournaments * cash_rate)
        tenth_plus = total_cashes

    ft_count = first + second + third + fourth_ninth
    ft_rate = ft_count / tournaments
    top3_conv = (first + second + third) / max(1, ft_count)

    aggression = estimate_aggression(cash_rate, ft_rate, top3_conv, field_normalized=False)

    player = {
        "name": "You",
        "tournaments": tournaments,
        "cash_rate": cash_rate,
        "1st": first, "2nd": second, "3rd": third,
        "4th-9th": fourth_ninth, "10th+": tenth_plus,
        "ft_rate": ft_rate,
        "top3_conv": top3_conv,
        "total_cashes": total_cashes,
        "aggression": aggression,
        "current_tier": "low",
    }

    normalized = normalize_placements(player, avg_field_size=avg_field, target_field_size=250)
    normalized["total_cashes"] = (normalized["1st"] + normalized["2nd"] + normalized["3rd"]
                                   + normalized["4th-9th"] + normalized["10th+"])

    evs = get_evs_for_player(normalized)
    leak = classify_leak(normalized, evs)
    best_tier = max(evs, key=lambda k: evs[k])

    return jsonify({
        "tournaments": tournaments,
        "cash_rate": round(cash_rate, 4),
        "ft_rate": round(normalized["ft_rate"], 4),
        "top3_conv": round(normalized["top3_conv"], 4),
        "aggression": round(aggression, 2),
        "classification": leak,
        "ev_by_tier": {TIERS[k]["label"]: round(evs[k]) for k in TIER_ORDER},
        "best_tier": TIERS[best_tier]["label"],
        "best_ev": round(evs[best_tier]),
        "sample_reliable": tournaments >= 200,
    })


@app.route("/api/population")
def population():
    """Return population distribution stats for comparison."""
    return jsonify({
        "total_synthetic": 100000,
        "losing_pct": 0.904,
        "tier_distribution": {
            "Brand New": {"pct": 0.30, "avg_cr": 0.047, "losing_pct": 1.0},
            "Bad Reg": {"pct": 0.29, "avg_cr": 0.090, "losing_pct": 1.0},
            "Average Player": {"pct": 0.18, "avg_cr": 0.130, "losing_pct": 0.992},
            "Slightly Profitable": {"pct": 0.10, "avg_cr": 0.170, "losing_pct": 0.928},
            "Good Reg": {"pct": 0.07, "avg_cr": 0.220, "losing_pct": 0.529},
            "Great Reg": {"pct": 0.04, "avg_cr": 0.270, "losing_pct": 0.137},
            "Low Level Pro": {"pct": 0.012, "avg_cr": 0.300, "losing_pct": 0.012},
            "Mid Level Pro": {"pct": 0.0055, "avg_cr": 0.330, "losing_pct": 0.0},
            "High Level Pro": {"pct": 0.002, "avg_cr": 0.360, "losing_pct": 0.0},
            "Best in the World": {"pct": 0.0005, "avg_cr": 0.400, "losing_pct": 0.0},
        },
        "leak_distribution": {
            "Small Sample": 0.323,
            "Skill Ceiling": 0.171,
            "Too Aggressive": 0.163,
            "Min-Cash Machine": 0.087,
            "Can't Close": 0.069,
            "Too Passive": 0.058,
            "No Final Tables": 0.032,
        },
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
