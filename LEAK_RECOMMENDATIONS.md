# Leak-to-Recommendation Pipeline

When a user imports their data, we classify their leak and serve a personalized development plan. This is the core product loop: **diagnose → prescribe → track progress → re-diagnose.**

## Input: User Data

User imports from CSV (Poker Bankroll Tracker, Poker Analytics) or manual entry:
- Tournament date
- Buy-in amount
- Finish position
- Payout received
- Field size (estimated if not provided)
- Venue (optional)

From this we derive: cash rate, FT rate, top-3 conversion, min-cash %, placement distribution, aggression estimate, and field-normalized stats.

---

## Pipeline by Leak Category

### 1. Small Sample + Skill Ceiling (combined: ~49% of users)
**Message:** "You need more data and more study."

**Phase 1 — Data Collection (0-200 tournaments)**
- Track everything. Every session, every result.
- Baseline assessment at 50, 100, 150, 200 tournaments
- Show confidence intervals: "Your cash rate is 15% +/- 8% — we need more data"
- Don't give definitive leak classification yet — flag as "provisional"

**Phase 2 — Skill Development (200+ tournaments)**
- Once we have reliable stats, classify actual leak
- If Skill Ceiling: prescribe fundamentals curriculum
  - Preflop range charts (position-based opening ranges)
  - Pot odds and implied odds calculations
  - Basic bet sizing theory
  - Tournament structure awareness (blind levels, stack depth)
- Serve pre-solved spots from TexasSolver for common situations
- Weekly study goals: 3 hours/week minimum off-table

**Solver Integration:**
- Serve "Fundamentals Pack" — 50 pre-solved common spots
- Focus on preflop and flop decisions (where most EV is lost)
- No ICM yet — chip EV fundamentals first

**Progress Metrics:**
- Cash rate trending up over 50-tournament windows
- FT rate emerging (any FT finishes appearing?)
- Moving from "Small Sample" to a real classification

---

### 2. Too Aggressive (16.3% of users)
**Message:** "Your aggression is an asset, but it's uncalibrated. GTO will teach you WHEN to be aggressive."

**Phase 1 — Awareness**
- Show them their stats vs the aggressive winners in our database
- Key stat: "You and profitable aggressive players have nearly the same aggression (0.75 vs 0.72). The difference is entirely in WHICH spots you choose."
- Bust rate analysis: show them how many buy-ins they're burning pre-money

**Phase 2 — GTO Calibration**
- Preflop 3-bet/4-bet frequency analysis
  - "You're 3-betting 12% of hands. GTO says 8% from this position."
- Continuation bet frequency on different board textures
- Bluff-to-value ratios by street
- River overbluff detection

**Phase 3 — Table Image Exploitation**
- Once GTO baseline is solid, teach them to exploit their aggressive image
- When to value bet thinner (opponents call you light)
- When to slow down (opponents are trapping you)

**Solver Integration:**
- "Aggression Calibration Pack" — 100 pre-solved spots focused on:
  - 3-bet pots (where aggro players spew most)
  - Continuation bet spots on various textures
  - River bluff vs value decisions
  - Multiway pots (where aggression is most punished)
- Node-locked studies: "Here's what happens when you bluff 80% vs GTO's 33%"

**Progress Metrics:**
- Cash rate trending toward 15-20% (from sub-10%)
- EV per tournament moving from negative to breakeven
- Bluff-to-value ratio approaching solver frequencies

---

### 3. Too Passive + Min-Cash Machine (combined: ~14.5% of users)
**Message:** "You're playing not to lose. The money in tournaments is at the top. A min-cash is $500, first place is $5,500."

**Phase 1 — Mindset Reset**
- Show the math: "Your 87% min-cash rate means your average payout is $X. If you converted just 10% of those to FT finishes, your EV increases by Y%"
- Bankroll impact calculator: "Yes, you'll cash less often. Here's what happens to your bankroll over 100 tournaments at each aggression level."
- Variance simulator: show them the temporary CR dip they'll experience and that it's expected

**Phase 2 — Stack Building**
- Preflop: widen opening ranges in late position
- Postflop: increase c-bet frequency and sizing
- Middle stages: attack bubble players who are also playing passive
- The "8x stack rule": at min-cash, average stack is 8x starting. Target 10x+ to have FT equity.

**Phase 3 — Deep Run Conversion**
- Once FT rate improves, transition to short-handed study
- ICM awareness: when to apply pressure vs when to ladder

**Solver Integration:**
- "Stack Building Pack" — spots focused on:
  - Late position stealing
  - Defending blinds vs steals (they're overfolding)
  - Postflop aggression spots
  - Bubble play: when to shove, when to apply pressure
- Before/after comparison: "GTO says raise here. Your current play is folding 70% of the time."

**Progress Metrics:**
- Min-cash % decreasing (from 87% toward 60%)
- FT rate emerging
- Aggression coefficient moving from 0.20-0.25 toward 0.40-0.55
- Short-term CR DIP is expected and tracked — don't panic

---

### 4. Can't Close (6.9% of users)
**Message:** "You already have the hardest skill — getting to the final table. Now you need to learn a different game."

**Phase 1 — FT-Specific Education**
- ICM fundamentals: why a chip you lose is worth more than a chip you win
- Stack-to-payout mapping: at every FT decision, show the $ implications
- Short-handed ranges: 6-max, 4-handed, 3-handed, heads-up

**Phase 2 — Targeted Solver Study**
- Pre-solved FT spots with ICM adjustments
- Common stack distributions (chip leader, mid-stack, short stack at each FT stage)
- Pay jump awareness: when to tighten for a pay jump vs when to go for the win

**Phase 3 — Heads-Up Mastery**
- If they're finishing 3rd-4th consistently, they're likely losing HU or 3-handed
- HU-specific solver work
- Adjusting to specific opponent types at FT

**Solver Integration:**
- "Final Table Mastery Pack" — the highest-value solver content:
  - 9-handed FT, various stack distributions (20 scenarios)
  - 6-handed FT, bubble situations (15 scenarios)
  - 3-handed with ICM (10 scenarios)
  - Heads-up for the win (10 scenarios)
  - Each scenario: GTO play, common mistakes, $ cost of mistakes
- Node-locked: "Your opponent shoves 50% at the FT. Here's the optimal counter."

**Progress Metrics:**
- Top-3 conversion rate increasing (from <25% toward 40%+)
- 1st place rate specifically
- $ per FT increasing

---

### 5. No Final Tables (3.2% of users)
**Message:** "Multiple areas need work. Consider whether tournament poker is the right format for you."

- Assess if cash games might be a better fit
- If staying in tournaments: start with the Skill Ceiling curriculum
- Track which stage they bust (early, middle, late, bubble)
- Prescribe based on bust stage

---

## Recommendation Engine Logic

```
Input: user stats (CR, FT rate, T3C, aggression, min-cash %, field sizes, sample size)
                    |
                    v
           [Field Size Normalization]
                    |
                    v
              [Leak Classification]
                    |
         +----------+----------+
         |          |          |
    Too Agg    Can't Close   Passive/MC
         |          |          |
   GTO Calib   FT Mastery   Stack Build
   Pack        Pack          Pack
         |          |          |
         +----------+----------+
                    |
                    v
          [Stake Move Assessment]
          (run model on their stats)
                    |
                    v
         [Personalized Dashboard]
         - Current leak & severity
         - Recommended study pack
         - Stake recommendation
         - Progress chart
         - Next milestone
```

## Re-Assessment Cadence

- **Every 50 tournaments:** update stats, check if leak classification changed
- **Every 100 tournaments:** full re-assessment, update stake recommendation
- **Milestone alerts:** "Your FT rate just crossed 5% — you've moved from Min-Cash Machine to Slightly Profitable"
