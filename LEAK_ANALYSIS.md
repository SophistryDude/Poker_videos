# Player Leak & Strength Analysis

Based on 100,000 synthetic player profiles run through the 4-tier stake move model with aggression coefficients, field size normalization, and real payout data.

## Leak Categories (Losing Players — 41.9% of all players)

### Skill Ceiling — 17.7% of all players
The #1 leak. These players have balanced aggression (avg 0.49), reasonable style, but simply aren't good enough to beat the field. Nothing to "fix" about their approach — they need to improve fundamentals.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 19.0% |
| Avg Aggression | 0.49 |
| Avg EV@$300 | -$65 |
| Min-Cash % | 64.3% |

**Real player example:** Becker (0.68 agg, 18% CR, 10x stacks) — his style is fine, he's just not skilled enough for tough fields. Dan also maps here (0.18 agg, 13.7% CR) though his passivity compounds the problem.

---

### Too Passive — 5.6% of all players
High cash rate but tiny stacks at the money. 84% min-cash rate means they're nursing short stacks into the money and bleeding out. They FEEL like they're doing well because they cash often, but the money is in deep runs, not min-cashes.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 22.3% |
| Avg Aggression | 0.23 |
| Avg EV@$300 | -$96 |
| Min-Cash % | 84.0% |

**Real player example:** Frankie (0.22 agg, 5x stacks, 90% min-cash rate, 2.1% FT rate). Only 10% of his cashes are final table finishes.

**Fix:** Take more risk pre-money. Build bigger stacks even if it means cashing less often. A player who cashes 18% with 10x stacks makes far more than one who cashes 25% with 5x stacks.

---

### Small Sample — 5.7% of all players
Fewer than 100 tournaments. Stats are unreliable — could be running hot or cold. Can't determine if they're winning or losing long-term.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 10.5% |
| Avg Aggression | 0.47 |
| Avg EV@$300 | -$167 |
| Avg Tournaments | 41 |

**Fix:** Play more. Need 200+ tournaments minimum for reliable stats, 500+ for confidence.

---

### Can't Close — 4.5% of all players
Makes final tables at a decent rate but has terrible top-3 conversion (under 25%). Gets to the FT and then bubbles out or finishes 4th-9th consistently. The money in tournaments is heavily top-weighted, so failing to convert FTs to wins is extremely costly.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 15.8% |
| Avg Aggression | 0.49 |
| Avg EV@$300 | -$100 |
| Avg Top-3 Conv | <25% |
| Min-Cash % | 50.9% |

**Real player parallel:** Dan's old stats showed 20.5% top-3 conversion — worst in the group. He makes FTs but doesn't close.

**Fix:** Study final table strategy specifically. ICM, short-handed play, heads-up. The FT is a different game than the early/mid stages.

---

### Too Aggressive — 4.3% of all players
High aggression craters their cash rate below viability. Busting out before the money too often. Even though they have big stacks when they do cash, they don't cash enough to compensate.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 10.6% |
| Avg Aggression | 0.76 |
| Avg EV@$300 | -$136 |
| Min-Cash % | 53.9% |

**Fix:** Dial back aggression slightly. The pro optimal is ~0.55-0.70, not 0.80+. There's a point of diminishing returns where bigger stacks don't compensate for the extra bustouts.

---

### Min-Cash Machine — 3.8% of all players
Similar to "Too Passive" but even more extreme. 86.5% of all cashes are min-cashes. These players are surviving to the money but with such short stacks that they have almost zero chance of making a deep run.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 16.3% |
| Avg Aggression | 0.45 |
| Avg EV@$300 | -$140 |
| Min-Cash % | 86.5% |

**Fix:** Same as Too Passive but more urgent. These players need a fundamental mindset shift: a min-cash in a $250 tournament is worth $500, but 1st place is $5,500. You need to play FOR the win, not for the cash.

---

### No Final Tables — 0.4% of all players
Rare leak. These players cash but literally never reach a final table. Their placement distribution is entirely 10th+ finishes. Often the result of extremely passive play combined with low skill.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 13.2% |
| Avg Aggression | 0.46 |
| Avg EV@$300 | -$178 |
| Min-Cash % | 94.6% |

---

## Strength Categories (Winning Players — 58.1% of all players)

### Complete Player — 18.0% of all players
The gold standard. Strong across every metric: high cash rate, balanced aggression, good FT rate, solid top-3 conversion. These players have no significant leaks and extract value at every stage of the tournament.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 33.7% |
| Avg Aggression | 0.54 |
| Avg EV@$300 | +$293 |
| Min-Cash % | 43.8% |

**Real player examples:** Nicholas (0.58 agg, 34.5% CR, 62.5% T3C) and Vincent (0.55 agg, 33.8% CR, 70.6% T3C).

---

### Deep Run Specialist — 13.2% of all players
High FT-to-cash ratio. When these players cash, they tend to go deep. Their stacks at the money are above average, giving them a runway to reach FTs and compete for top prizes.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 27.3% |
| Avg Aggression | 0.59 |
| Avg EV@$300 | +$199 |
| Min-Cash % | 37.9% |

---

### Optimal Aggression — 11.4% of all players
These players have found the aggression sweet spot (avg 0.65). Lower cash rate than Complete Players but compensated by bigger stacks and more 1st-place finishes. They're playing the way pros recommend.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 24.9% |
| Avg Aggression | 0.65 |
| Avg EV@$300 | +$155 |
| Min-Cash % | 40.2% |

**Real player example:** Bryan (0.72 agg, 25% CR, 11x stacks, 68.7% T3 conversion). His lower CR is by design — he trades cashes for big stacks and wins.

---

### Passive Grinder — 5.1% of all players
Profitable despite low aggression. These players have such high cash rates that the volume of cashes compensates for smaller stacks. They're leaving money on the table compared to Complete Players, but they're still winning.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 35.3% |
| Avg Aggression | 0.25 |
| Avg EV@$300 | +$109 |
| Min-Cash % | 66.8% |

**Ceiling warning:** Passive Grinders average +$109/entry vs Complete Players at +$293. They could nearly 3x their EV by adjusting their aggression upward.

---

### Solid Overall — 4.9% of all players
Profitable but without a standout strength. Decent across the board but not elite in any single area. These players are winning but have room to specialize.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 28.9% |
| Avg Aggression | 0.43 |
| Avg EV@$300 | +$70 |
| Min-Cash % | 63.1% |

---

### Volume Edge — 4.7% of all players
Large tournament sample (1000+) with a small but consistent edge. These players grind out profit through sheer volume rather than big scores. Often passive with high cash rates.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 35.4% |
| Avg Aggression | 0.29 |
| Avg EV@$300 | +$102 |
| Min-Cash % | 66.8% |

---

### Closer — 0.5% of all players
Rare strength. High top-3 conversion (>55%) at final tables. When they get to a FT, they win. Their overall stats may not look elite, but their endgame is deadly.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 32.2% |
| Avg Aggression | 0.44 |
| Avg EV@$300 | +$152 |

**Real player example:** Nikko (0.40 agg, 32% CR, 68.3% T3 conversion). Passive overall but lethal at final tables.

---

### Aggressive + Skilled — <0.1% of all players
Extremely rare. High aggression (0.80+) AND profitable. These players have such high skill that they can sustain an aggressive style that would bankrupt most players.

| Stat | Value |
|------|-------|
| Avg Cash Rate | 18.4% |
| Avg Aggression | 0.80 |
| Avg EV@$300 | +$17 |

---

## Distribution by Player Tier

| Tier | % Losing | Top Leak | Top Strength |
|------|----------|----------|-------------|
| Brand New | 99.9% | Small Sample (52%) | — |
| Bad Reg | 99.4% | Skill Ceiling (37%) | — |
| Average Player | 85.6% | Skill Ceiling (48%) | — |
| Slightly Profitable | 44.8% | Skill Ceiling (31%) | Optimal Aggression (21%) |
| Good Reg | 15.1% | — | Optimal Aggression (25%) |
| Great Reg | 1.1% | — | Complete Player (35%) |
| Low Level Pro | 0.0% | — | Complete Player (48%) |
| Mid Level Pro | 0.0% | — | Complete Player (56%) |
| High Level Pro | 0.0% | — | Complete Player (56%) |
| Best in the World | 0.0% | — | Complete Player (58%) |

## Key Takeaways

1. **Skill Ceiling is the #1 leak** — 17.7% of all players. Style is fine, skill isn't. No shortcut to fix this.
2. **Too Passive and Too Aggressive are roughly even** (5.6% vs 4.3%), but passive is sneakier because high CR feels like winning.
3. **Complete Player is the #1 strength** — balanced aggression (~0.54), high CR, good FT rate. This is the archetype to aim for.
4. **Optimal Aggression (0.65 avg) is the breakout zone** — the tier where "Slightly Profitable" players graduate to "Good Reg." Finding the right aggression level is the single biggest lever for mid-tier players.
5. **Passive Grinders leave ~2.7x EV on the table** compared to Complete Players. If you're profitable but passive, adjusting aggression is the highest-ROI improvement.
6. **"Can't Close" is a fixable leak** — FT strategy is a learnable skill. Players who make FTs but don't convert are one study session away from a significant EV jump.
