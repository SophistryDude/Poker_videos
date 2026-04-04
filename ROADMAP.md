# Roadmap

## Phase 0: Foundation (COMPLETE)
*Data pipeline, models, and proof of concept*

- [x] Scrape tournament data from Hendon Mob (Wynn, Venetian, Orleans, South Point)
- [x] Build payout models for 4 tiers ($300 / $600 / $1,000 / $1,800)
- [x] 4-tier stake move model with aggression coefficients
- [x] Field size normalization
- [x] 100K synthetic player profiles with realistic population distribution
- [x] Leak classification engine (7 categories)
- [x] Bulk analysis and validation against real player group (7 players)
- [x] Leak deep dive analysis (Too Aggressive, Too Passive vs Min-Cash, Can't Close)
- [x] Content creation pipeline (Whisper → Claude → ElevenLabs → YouTube)
- [x] Strategy docs (ICM, content, monetization, leak recommendations)
- [x] Clone TexasSolver, verify working

## Phase 1: MVP Launch
*Get the free tier in front of users, start content*

### Web App (Free Tier)
- [x] Flask app with CSV import and manual entry
- [x] Leak classification + percentile ranking
- [x] EV projection across 4 stake tiers
- [x] Deploy to EC2 (k0s) with HTTPS at poker.alphabreak.vip
- [ ] User accounts (email/password or Google OAuth)
- [ ] Save and retrieve past assessments
- [ ] Dashboard with profit graph from uploaded results
- [ ] Mobile-responsive UI polish
- [ ] CSV import compatibility testing (Poker Bankroll Tracker, Poker Analytics, Poker Income)
- [ ] Sample size confidence intervals ("your CR is 27% ± 4%")
- [ ] Shareable results page (link to share your classification)

### Content
- [ ] Record 30 min voice training audio
- [ ] Clone voice on ElevenLabs
- [ ] First 5 videos published:
  - "80% of poker players are losing — here's the math"
  - "The 7 leaks killing your poker game"
  - "I analyzed 100,000 players to find out when you should move up"
  - "The min-cash trap: why cashing feels good but costs you money"
  - "I built a poker AI — here's what it found" (dev diary)
- [ ] Set up YouTube channel, TikTok, Twitter/X
- [ ] Reddit r/poker launch post with real data findings

### Data
- [ ] Complete payout scraping for $0-$300 tier (replace estimated payouts with real data)
- [ ] Validate $0-$300 payout model against scraped data
- [ ] Add entries/field size data to tournament records where available

## Phase 2: Pro Tier ($14.99/mo)
*Solver study packs, personalized plans, progress tracking*

### Solver Integration
- [ ] Build Python wrapper for TexasSolver console solver
- [ ] Pre-solve 50 common spots organized by leak category:
  - Fundamentals Pack (Skill Ceiling): 15 preflop + flop spots
  - Aggression Calibration Pack (Too Aggressive): 15 3-bet and c-bet spots
  - Stack Building Pack (Too Passive): 10 stealing + bubble spots
  - Final Table Mastery Pack (Can't Close): 10 short-handed + ICM spots
- [ ] Solver output parser — extract key frequencies and display in readable format
- [ ] "Your play vs GTO" comparison tool
- [ ] Spot-of-the-week: auto-generate a study spot based on user's leak

### ICM (Phase 1 approach: post-processing)
- [ ] Implement ICM calculator (port from aidanf/SimpleICM or poker-apprentice)
- [ ] Post-process solver output with ICM risk adjustments
- [ ] Bubble factor calculator
- [ ] FT equity calculator (input stacks + payouts → see your equity)

### User Features
- [ ] Personalized study plan based on leak classification
- [ ] Progress tracking: re-assess every 50 tournaments
- [ ] Milestone alerts ("Your FT rate just crossed 5%")
- [ ] Compare with friends (group leaderboard)
- [ ] Advanced stats: EV by position, by stage, by venue
- [ ] Export PDF reports (for coaching)

### Payment
- [ ] Stripe integration
- [ ] Free trial (7 days)
- [ ] Pro subscription ($14.99/mo)

## Phase 3: Elite Tier ($39.99/mo)
*Custom solves, advanced ICM, API access*

### Custom Solver
- [ ] User inputs custom spots (board, stacks, ranges, bet sizes)
- [ ] Queue system for solver jobs (run on dedicated compute)
- [ ] Node locking: input opponent tendencies, get exploitative adjustments
- [ ] Solver result caching (avoid re-solving identical spots)

### Advanced ICM (Phase 2 approach: modified input ranges)
- [ ] ICM-adjusted preflop ranges (feed into solver)
- [ ] Pre-solved FT library: 50 scenarios covering 9-handed → heads-up
- [ ] Stack distribution templates from real FT data
- [ ] "What would GTO do here?" for any FT scenario

### Infrastructure
- [ ] Dedicated compute instance for solver jobs (c5.xlarge or GPU)
- [ ] Job queue (Redis/Celery)
- [ ] PostgreSQL for user data (migrate from in-memory)
- [ ] API access for Elite users

### Content (ongoing)
- [ ] 2-3 videos/week cadence
- [ ] Solver breakdown series (weekly hand analysis using the platform)
- [ ] Case study series (anonymized user transformations)
- [ ] Guest content with other poker creators

## Phase 4: Scale
*Native ICM, mobile app, partnerships*

### Solver (Phase 3 approach: fork for native ICM)
- [ ] Evaluate TexasSolver vs b-inary/postflop-solver for ICM fork
- [ ] Modify terminal node payoffs to use ICM equity
- [ ] Handle non-zero-sum convergence
- [ ] Or: build custom solver from scratch if licensing is cleaner

### Mobile
- [ ] React Native or Flutter app
- [ ] Quick entry at the table (log results between hands)
- [ ] Push notifications for study reminders and milestone alerts
- [ ] Offline mode for tournament venues with bad WiFi

### Partnerships
- [ ] Poker room partnerships (Wynn, Venetian — offer tool to their players)
- [ ] Training site cross-promotion
- [ ] Poker media partnerships (Card Player, PokerNews)
- [ ] Affiliate program for poker creators

### Growth
- [ ] Localization (Spanish, Portuguese for LatAm poker markets)
- [ ] Online poker support (PokerStars, GGPoker hand history import)
- [ ] Cash game module (separate model, different mechanics)
- [ ] AI coaching (Claude-powered hand review using solver + leak context)

---

## Key Metrics to Track

| Metric | Phase 1 Target | Phase 2 Target | Phase 3 Target |
|--------|---------------|---------------|---------------|
| YouTube subscribers | 5,000 | 25,000 | 100,000 |
| Free users | 2,000 | 10,000 | 50,000 |
| Pro subscribers | — | 1,000 | 5,000 |
| Elite subscribers | — | 300 | 1,500 |
| MRR | $0 | $17,000 | $135,000 |
| Pre-solved spots | 0 | 50 | 200 |
| Tournaments in DB | 12,400 | 15,000 | 25,000 |

## Decision Log

| Date | Decision | Reasoning |
|------|----------|-----------|
| 2026-04-04 | Step-based CR degradation over convergence model | Convergence model made weak players look too viable. Step-based matches validated real player results. |
| 2026-04-04 | Manual aggression for real players, estimated for synthetic | FT-to-cash ratio unreliable in small fields. Manual aggression from domain expert (Nicholas) is ground truth. |
| 2026-04-04 | Merge Too Passive + Min-Cash Machine for teaching | Same outcome (87-89% min-cash), different causes. Same fix, different messaging. |
| 2026-04-04 | ~80% losing player distribution | Pro consensus + structural math (87.5% lose each tournament). Previous 42% was unrealistically optimistic. |
| 2026-04-04 | Deploy on existing EC2 vs new instance | <100 users, ~500MB RAM needed. Existing t3.medium has 4GB free. Migrate when justified. |
| 2026-04-04 | TexasSolver over building custom | Open source, tested, faster than PioSolver on turn/river. No ICM but we'll add via post-processing initially. |
| 2026-04-04 | $0-$300 payout model: 22x first / 2x min-cash (estimated) | Scraper still running for real data. Estimate is from domain expertise. Will update when data arrives. |
