# ICM-Adjusted Solves Through TexasSolver — Strategy Document

## The Problem

TexasSolver computes **chip EV** — it treats every chip as having equal value. In cash games, this is correct. In tournaments, it's wrong.

In tournaments, chips have **diminishing marginal value** because of the payout structure. Doubling your stack doesn't double your equity in the prize pool. Losing all your chips costs you 100% of your equity, but winning all your chips doesn't give you 100% of the prize pool.

This means tournament decisions — especially at final tables — require **ICM adjustments** to the solver output.

## How ICM Works

### The Math

ICM (Independent Chip Model) converts chip stacks to tournament equity using the Malmuth-Harville formula:

```
P(player i finishes 1st) = chips_i / total_chips

P(player i finishes 2nd) = sum over all j != i of:
    P(j finishes 1st) * (chips_i / (total_chips - chips_j))

P(player i finishes 3rd) = ... (recursion continues)
```

Then: `equity_i = sum(P(finish k) * payout_k) for all k`

### Example

9-player FT, $10K prize pool: 50%/30%/20% payout.

| Player | Chips | % of Total | Chip EV | ICM Equity | Difference |
|--------|-------|-----------|---------|------------|------------|
| Chip leader | 40,000 | 40% | $4,000 | $3,200 | -$800 |
| Average | 10,000 | 10% | $1,000 | $1,050 | +$50 |
| Short stack | 5,000 | 5% | $500 | $600 | +$100 |

The chip leader's chips are worth LESS than face value because they can't win more than 1st place. The short stack's chips are worth MORE because each chip is critical to survival.

**This changes every decision.** A chip-EV shove that's +100 chips might be -$50 in ICM equity because the risk of busting outweighs the gain.

## How PioSolver Handles ICM

PioSolver has built-in ICM support:
1. User inputs stack sizes and payout structure
2. Solver modifies the **payoff matrix** at terminal nodes — instead of awarding chips, it awards ICM equity
3. CFR runs normally but optimizes for ICM $ instead of chips
4. Output strategies are inherently ICM-adjusted

This is the gold standard approach — ICM is baked into the solve itself, not applied after.

## Our Approach: ICM on Top of TexasSolver

Since TexasSolver doesn't support ICM natively, we have three approaches, from simplest to most accurate:

### Approach 1: Post-Processing (Simplest, ~80% accurate)

1. Run TexasSolver normally (chip EV)
2. Take the output strategies
3. Apply ICM adjustment weights to modify frequencies

**How:**
- For each decision point, calculate the ICM cost of the worst case (busting or losing big pot)
- Tighten calling ranges proportionally to ICM pressure
- Widen folding ranges near pay jumps
- Apply a "risk premium" multiplier: actions that risk elimination get penalized

**Implementation:**
```python
def icm_adjust_strategy(chip_ev_strategy, stacks, payouts, hero_stack):
    icm_equity = calculate_icm(stacks, payouts)
    risk_premium = icm_risk_factor(hero_stack, stacks, payouts)

    adjusted = {}
    for action, freq in chip_ev_strategy.items():
        if action == "FOLD":
            adjusted[action] = freq  # folding is never ICM-penalized
        elif action == "ALLIN" or is_large_bet(action):
            adjusted[action] = freq * (1 - risk_premium)
        else:
            adjusted[action] = freq
    # Renormalize frequencies to sum to 1
    return normalize(adjusted)
```

**Pros:** Fast, easy to implement, works with any solver output
**Cons:** Doesn't account for how ICM changes the opponent's strategy too (they should also be tighter)

### Approach 2: Modified Input Ranges (Better, ~90% accurate)

1. Calculate ICM equity for all players
2. Adjust the input ranges BEFORE solving based on ICM pressure:
   - Short stacks get tighter ranges (survival mode)
   - Big stacks get slightly wider (can apply pressure)
   - Bubble players get much tighter
3. Run TexasSolver with ICM-adjusted ranges
4. The output is approximately ICM-correct because the ranges reflect ICM reality

**How:**
```python
def icm_adjust_ranges(base_range, stack_bb, avg_stack_bb, bubble_factor):
    # bubble_factor: 0.0 (no bubble) to 1.0 (stone bubble)
    # Tighten range based on ICM pressure
    tightening = bubble_factor * 0.3 + (1 - stack_bb/avg_stack_bb) * 0.2
    tightening = max(0, min(0.5, tightening))

    # Remove the bottom X% of the range
    return remove_bottom_hands(base_range, tightening)
```

**Pros:** Solver produces better strategies because ranges reflect reality
**Cons:** Still not true ICM since payoffs are in chips

### Approach 3: Custom Payoff Wrapper (Most Accurate, Hardest)

Fork TexasSolver and modify the terminal node payoff calculation:
1. Instead of awarding chips at showdown/fold, calculate the resulting ICM equity for both players
2. The CFR algorithm then naturally optimizes for ICM

**How:**
- In the source code, find where chip payoffs are calculated at leaf nodes
- Replace with ICM equity calculation: `payoff = icm_equity_after - icm_equity_before`
- This requires knowing all stack sizes (not just the two players in the hand)

**Pros:** True ICM-optimal strategies
**Cons:** Requires modifying C++ source, slower solves (ICM calc at every terminal node), need to handle the multi-player context

### Recommended Path

**Phase 1 (MVP):** Approach 1 (post-processing) for initial product
- Fast to implement
- Good enough for "Can't Close" study packs
- Users get directional ICM advice immediately

**Phase 2 (v2):** Approach 2 (modified input ranges)
- Better accuracy for pre-solved FT library
- Can pre-compute range adjustments for common FT scenarios

**Phase 3 (v3):** Approach 3 (fork solver) OR lobby PioSolver-style ICM directly into TexasSolver open source
- True ICM solving
- This becomes a major competitive advantage

---

## Pre-Solved ICM Spot Library

Rather than solving on the fly, we pre-solve the most common FT scenarios and serve them from a database.

### Priority Scenarios (Phase 1: 50 spots)

**9-Handed FT (20 scenarios)**
Standard payouts: 30% / 20% / 15% / 12% / 8% / 5% / 4% / 3.5% / 2.5%

| Scenario | Hero Stack | Villain Stack | Board Type | Key Decision |
|----------|-----------|--------------|------------|-------------|
| Chip leader vs short stack | 25BB | 8BB | Dry | Shoving range |
| Short stack vs chip leader | 8BB | 25BB | Dry | Calling range vs shove |
| Average vs average, bubble | 15BB | 15BB | Wet | C-bet frequency |
| 3 short stacks, you're medium | 12BB | 6BB (3 players) | Any | ICM pressure exploitation |
| ... | ... | ... | ... | ... |

**6-Handed FT (15 scenarios)**
After 3 eliminations, ranges widen, ICM pressure shifts.

**3-Handed (10 scenarios)**
Big pay jumps between 3rd and 1st. Maximum ICM pressure.

**Heads-Up for the Win (5 scenarios)**
ICM is minimal HU (only 1st/2nd left). Nearly pure chip EV.

### Stack Distribution Templates

Based on real final table data from our database:

| Stage | Chip Leader | 2nd Stack | Average | Short Stack |
|-------|------------|-----------|---------|-------------|
| 9-handed start | 35BB | 25BB | 15BB | 8BB |
| 6-handed | 45BB | 30BB | 18BB | 10BB |
| 3-handed | 60BB | 30BB | 15BB | — |
| Heads-up | 80BB | 40BB | — | — |

---

## ICM Calculator Module

We need a fast ICM calculator regardless of which approach we use.

```python
def calculate_icm(stacks: list[int], payouts: list[float]) -> list[float]:
    """
    Calculate ICM equity for each player.

    Args:
        stacks: chip count for each player [40000, 20000, 10000, ...]
        payouts: prize for each finishing position [5000, 3000, 2000, ...]

    Returns:
        ICM equity for each player [$3200, $2100, $1500, ...]
    """
    n = len(stacks)
    total = sum(stacks)
    equities = [0.0] * n

    def prob_finish(player, position, remaining, remaining_chips):
        """Recursive probability of player finishing in position."""
        if position == 1:
            return stacks[player] / total if player in remaining else 0

        prob = 0
        for other in remaining:
            if other == player:
                continue
            # Probability other wins (finishes in an earlier position)
            p_other_wins = stacks[other] / remaining_chips
            new_remaining = [p for p in remaining if p != other]
            new_chips = remaining_chips - stacks[other]
            prob += p_other_wins * prob_finish(player, position - 1,
                                                new_remaining, new_chips)
        return prob

    all_players = list(range(n))
    for i in range(n):
        for pos in range(min(n, len(payouts))):
            p = prob_finish(i, pos + 1, all_players, total)
            equities[i] += p * payouts[pos]

    return equities
```

Note: This naive implementation is O(n!) — fine for 9 players, needs optimization for speed. Caching and the Malmuth-Harville approximation help.

---

## Technical Architecture for ICM in the Product

```
User at FT → selects stack sizes + payout structure
    |
    v
[ICM Calculator] → shows current equity for each player
    |
    v
[Scenario Matcher] → finds closest pre-solved spot in library
    |
    v
[TexasSolver output] → chip EV strategy
    |
    v
[ICM Post-Processor] → adjusts frequencies for ICM
    |
    v
[Display] → "GTO says raise 40% here. With ICM, tighten to 28%."
            → "This fold saves you $X in ICM equity"
            → "Shoving here is +$50 chip EV but -$120 ICM EV"
```

## Critical Technical Detail: Non-Zero-Sum

In chip EV, heads-up poker is zero-sum (your gain = opponent's loss). **With ICM, the game becomes non-zero-sum** because chips have diminishing marginal value. A pot where you risk 50bb to win 50bb is NOT symmetric in tournament equity terms.

This has implications for solving:
- Standard CFR converges for zero-sum games with theoretical guarantees
- For non-zero-sum ICM games, convergence is approximate — a "solution" with zero exploitability could mean one player can still improve at the other's expense
- PioSolver handles this internally; if we fork TexasSolver we'd need to accept approximate convergence or use correlated equilibrium approaches
- In practice, for the study pack use case, approximate convergence is fine — we're teaching directional strategy, not computing exact Nash frequencies

## Open Source ICM Calculators (Ready to Use)

| Repo | Language | Notes |
|------|----------|-------|
| [poker-apprentice/icm-calculator](https://github.com/poker-apprentice/icm-calculator) | JS/TS | Most comprehensive, exact + estimation |
| [aidanf/SimpleICM](https://github.com/aidanf/SimpleICM) | Python | Simple, good starting point |
| [apcode/poker-mtt-icm](https://github.com/apcode/poker-mtt-icm) | Python | Handles larger MTT fields |
| [atinm/SNGEGT](https://github.com/atinm/SNGEGT) | — | SNG push/fold + ICM |

For Phase 1, we use `aidanf/SimpleICM` (Python) for the post-processing ICM adjustments.

## Alternative Solver Fork Target

[b-inary/postflop-solver](https://github.com/b-inary/postflop-solver) (Rust) uses modern Discounted CFR and may be a better fork target than TexasSolver for native ICM. Development is suspended but codebase is reportedly excellent. Worth evaluating for Phase 3.

## Commercial Considerations

- TexasSolver is AGPL-V3: **commercial use requires contacting the author** for a separate license
- If we fork and modify for ICM, our modifications must also be open source under AGPL
- Alternative: use TexasSolver as an external tool (subprocess), not a linked library — this may avoid AGPL copyleft requirements for our own code (legal review needed)
- Long-term: building our own solver with native ICM would eliminate licensing concerns entirely
