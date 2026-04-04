# Poker Development Platform

A data-driven poker player development system that diagnoses leaks, prescribes fixes, recommends stake levels, and tracks progress over time.

**Live:** https://poker.alphabreak.vip

## What It Does

Most poker tools show you a profit graph. This one tells you **why** the graph looks the way it does and **how** to change it.

- **Leak Classification** — Upload your results or enter stats manually. The system classifies you into one of 7 leak categories (or identifies your strength) based on 100,000 synthetic player profiles calibrated to real tournament data.
- **Stake Move Model** — Should you move up, stay, or move down? 4-tier analysis ($300 / $600 / $1,000 / $1,800) using real payout data from 1,400+ tournaments at Wynn, Venetian, Orleans, and South Point.
- **Aggression Analysis** — Estimates your playstyle coefficient and how it impacts your EV at different stake levels. Based on the pro consensus that ~18% cash rate with optimal aggression maximizes long-term profit.
- **Field Normalization** — Adjusts your stats for field size. A "4th place" in a 100-person nightly is not the same as 4th in a 250-person festival.

## The Data

- **12,400+ tournaments** scraped from pokerdb.thehendonmob.com (Wynn, Venetian, Orleans, South Point)
- **37,000+ payout records** across 4 buy-in tiers
- **100,000 synthetic player profiles** with realistic population distribution (~80% losing, 2% pro)
- **7 validated leak categories** with fix recommendations

## Leak Categories

| Leak | % of Players | Description |
|------|-------------|-------------|
| Small Sample | 32% | <100 tournaments — can't evaluate yet |
| Skill Ceiling | 17% | Balanced style, not skilled enough |
| Too Aggressive | 16% | Busting too much, uncalibrated aggression |
| Min-Cash Machine | 9% | 89% of cashes are min-cashes |
| Can't Close | 7% | Makes final tables, <25% top-3 conversion |
| Too Passive | 6% | High cash rate but tiny stacks, 87% min-cash |
| No Final Tables | 3% | Cashes but never goes deep |

## Tech Stack

- **Backend:** Python / Flask / Gunicorn
- **Analytics:** NumPy, custom CFR-adjacent models
- **Infrastructure:** AWS EC2 (t3.medium) / k0s Kubernetes / Nginx / Let's Encrypt
- **Data:** PostgreSQL (tournament + payout data), CSV (synthetic profiles)
- **Solver:** TexasSolver (open source GTO solver, pre-computed spots)
- **Content Pipeline:** Whisper (transcription) → Claude (script cleanup) → ElevenLabs (voice clone) → YouTube API

## Project Structure

```
├── poker_app/              # Web application
│   ├── app.py              # Flask API + routes
│   └── templates/          # Frontend
├── stake_move_model.py     # 4-tier EV model with aggression + field normalization
├── leak_analysis.py        # Leak classification engine
├── generate_profiles.py    # 100K synthetic player generator
├── run_bulk_analysis.py    # Bulk analysis runner
├── leak_deep_dive.py       # Detailed leak comparisons
├── pipeline.py             # Content creation pipeline orchestrator
├── webapp.py               # Video pipeline web portal
├── watch.py                # Auto-process audio files
├── steps/                  # Pipeline modules
│   ├── transcribe.py       # Whisper speech-to-text
│   ├── cleanup.py          # Claude script cleanup
│   ├── voice_synth.py      # ElevenLabs voice synthesis
│   └── youtube_upload.py   # YouTube API upload
├── config/                 # Settings and credentials
├── deploy/                 # EC2 deployment scripts
├── k8s/                    # Kubernetes manifests
├── content/                # Scripts and content drafts
├── LEAK_ANALYSIS.md        # Full leak breakdown with stats
├── LEAK_RECOMMENDATIONS.md # Per-leak fix prescriptions
├── ICM_STRATEGY.md         # ICM solver integration strategy
├── CONTENT_STRATEGY.md     # YouTube content plan
├── MONETIZATION.md         # Business model and projections
└── ROADMAP.md              # Development roadmap
```

## Quick Start

### Run Locally
```bash
pip install flask numpy openpyxl
cd poker_app
python app.py
# Open http://localhost:5001
```

### Deploy to EC2
```bash
bash deploy/deploy_ec2.sh
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/analyze` | POST | Upload CSV for full analysis |
| `/api/quick-assess` | POST | Manual stat entry assessment |
| `/api/population` | GET | Population distribution stats |

## The Team

Built by Nicholas Major — tournament poker player, data scientist, and software engineer. Profitable from day one through a quantitative approach to the game.

## License

Proprietary. Not open source.
