: "# AQRA — Autonomous Quant Research Agent"
description: "README for AQRA, a dual-lane autonomous quant research system with conformal certification, adversarial BEAR review, and Alpaca paper trading."

---

# AQRA — Autonomous Quant Research Agent

AQRA is a dual-lane, theorem-backed autonomous quantitative-research system. It discovers equity-trading strategies, validates them with conformal prediction and false-discovery-rate control, subjects them to an adversarial BEAR review chamber, and deploys the survivors to Alpaca paper trading.

- **Lane S (Structural alpha):** slow-moving factors such as momentum, value, and quality.
- **Lane I (Informational alpha):** fast signals such as overnight gaps, volume spikes, and sentiment shocks.
- **Conformal certification:** per-lane prediction intervals and Benjamini–Yekutieli FDR control.
- **BEAR chamber:** adversarial review for look-ahead bias, data mining, lane misclassification, and economic rationale.
- **Live deployment gate:** paper-only trading with daily loss limits and max-drawdown safety rules.

## Project structure

```
aqra/
├── src/aqra/          # Core Python package
│   ├── data/          # Free-tier data connectors (yfinance, FRED, EDGAR, etc.)
│   ├── features/      # Lane S / Lane I feature builders + PITGuard
│   ├── signals/       # Signal candidate libraries
│   ├── backtest/      # Walk-forward backtest engine
│   ├── conformal/     # Conformal prediction + BY FDR
│   ├── certify/       # Lane certifiers and certified dossiers
│   ├── bear/          # Adversarial review chamber
│   ├── registry/      # Strategy registry + regime-aware allocator
│   ├── live/          # Alpaca paper client, deployment gate, monitor
│   ├── memory/        # Git-tracked agent memory
│   ├── dashboard/     # Web dashboard (Phase 2)
│   └── cli.py         # Typer command-line interface
├── tests/             # pytest suite
├── notebooks/         # Research notebooks
├── docs/paper/        # Research paper drafts
├── data/              # Local DuckDB store
└── memory/            # Agent memory logs
```

## Setup

Requires Python 3.12+ and `uv`.

```bash
cd aqra
uv sync --extra dev
uv run python -m pytest tests/ -v
```

Copy `.env.example` to `.env` and fill in any keys you want to use. Phase 1 runs entirely on free-tier data and Alpaca paper trading; live deployment is blocked without keys.

## Running AQRA

```bash
# Ingest S&P 500 OHLCV and build feature tables
make ingest

# Discover and certify strategies
make certify

# Deploy to Alpaca paper trading (dry-run)
make deploy-dry

# Monitor live performance and retire broken strategies
make monitor
```

Or directly via the CLI:

```bash
uv run aqra ingest --start 2020-01-01 --end 2024-12-31
uv run aqra certify
uv run aqra deploy --dry-run
uv run aqra monitor
```

## Research paper

A skeleton paper is in `docs/paper/aqra_paper_skeleton.md`.

## License

Research and educational use only. Phase 1 does not trade real money.
