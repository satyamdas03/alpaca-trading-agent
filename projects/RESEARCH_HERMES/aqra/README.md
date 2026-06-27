# AQRA — Autonomous Quant Research Agent

AQRA is a dual-lane conformal strategy discovery engine for systematic swing trading. It combines a fast discovery lane for feature/signal search with a slow certify lane for statistical validation, including conformal prediction and adversarial BEAR testing.

## Project structure

```
aqra/
├── src/aqra/          # Core Python package
│   ├── data/          # Data connectors (free tier only)
│   ├── features/       # Feature engineering
│   ├── signals/        # Signal generators
│   ├── backtest/       # Backtest engine
│   ├── conformal/      # Conformal prediction
│   ├── certify/        # Statistical certification
│   ├── bear/           # Adversarial testing (BEAR)
│   ├── registry/       # Strategy registry
│   ├── live/           # Paper/live execution (Phase 2+)
│   ├── dashboard/      # Web dashboard
│   └── memory/         # Agent memory
├── tests/             # pytest suite
├── data/              # Local data store (DuckDB)
├── notebooks/         # Research notebooks
└── docs/paper/        # Research paper drafts
```

## Setup

Requires Python 3.12+ and `uv`.

```bash
uv sync --extra dev
uv run pytest
```

## Environment

Copy `.env.example` to `.env` and fill in your API keys. Phase 1 uses only free data tiers.

## License

Research and educational use only. No real-money trading logic in Phase 1.
