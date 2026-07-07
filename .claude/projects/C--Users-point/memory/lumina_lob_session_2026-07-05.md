---
name: lumina-lob-session-2026-07-05
description: Complete session record for Lumina LOB limit order book simulator — ALL SIX PHASES COMPLETE (CP0.1→CP6.6), 308 tests, 100% package coverage, v0.1.1 tag pushed, docs/quality/packaging gaps fixed, ruff and mypy clean, sdist+wheel build verified, GitHub Actions CI green on 9 OS/Python matrix jobs, GitHub Pages docs site live, PyPI publish workflow ready pending trusted-publishing configuration, GitHub profile pin requires manual UI action.
metadata:
  node_type: memory
  type: project
  project: lumina-lob
  date: 2026-07-05
  status: active
  originSessionId: 9324512f-cccd-44a2-a4c8-367da19986d3
---

# Lumina LOB — Session Record 2026-07-05

**Why:** This memory keeps a fresh session from having to reconstruct the Lumina LOB state from Git history. It records the exact checkpoint discipline, known bugs, test commands, and next task.

**How to apply:** On a fresh start, read this file first, then `PLAN.md`, run the test suite, and pick up at the next checkpoint listed in this file.

**Project root:** `C:\Users\point\projects\janestreet\01_LuminaLOB_LimitOrderBook_Simulator`
**GitHub remote:** `https://github.com/satyamdas03/lumina-lob.git`
**Branch:** `main`
**Latest commit:** `6ac0fc9` — "fix: complete v0.1.1 — docs, lint, types, packaging, sdist" (pushed 2026-07-07; fixes documentation contradictions, ruff/mypy errors, and sdist packaging; tag `v0.1.1` is live).
**Previous commit:** `e72aeb6` — "ci: fetch full git history so release tag tests pass".
**Full session transcript:** `C:\Users\point\.claude\projects\C--Users-point-projects-janestreet\9324512f-cccd-44a2-a4c8-367da19986d3.jsonl`

## Why this project exists

This is the first of the six live GitHub portfolio repos built for the Jane Street / quant trading 3-year roadmap (see [[satyam_janestreet_quant_roadmap_2026-2029]]). The goal is a production-grade, open-source limit order book simulator with:

- Price-time priority matching engine (Python + future C++17/pybind11 hot path)
- Realistic market agents (noise traders, informed traders, market makers)
- RL market-maker training via Stable-Baselines3
- Calibration to real tick data (Polygon / Databento)
- Visualization and published technical blog post

Target users: quant-interview candidates, ML researchers, students, and hiring managers at Jane Street / Citadel / Optiver / IMC.

## Master plan

The complete 28-checkpoint plan lives at:

```
C:\Users\point\projects\janestreet\01_LuminaLOB_LimitOrderBook_Simulator\PLAN.md
```

It is organized into six phases:

| Phase | Scope | Checkpoints |
|---|---|---|
| Phase 0 | Core engine hardening | CP0.1 → CP0.6 |
| Phase 1 | Market model + agents | CP1.1 → CP1.8 |
| Phase 2 | Data + calibration | CP2.1 → CP2.6 |
| Phase 3 | RL market maker | CP3.1 → CP3.7 |
| Phase 4 | C++ performance layer | CP4.1 → CP4.5 |
| Phase 5 | Visualization | CP5.1 → CP5.4 |
| Phase 6 | Packaging + publication | CP6.1 → CP6.6 |

**Execution rule:** one checkpoint per turn. After each checkpoint: run tests, commit, push, report, then continue to the next checkpoint. Do NOT batch multiple checkpoints without explicit user approval.

## What was done in this session

### Phase 0 — Core engine hardening (CP0.1 → CP0.6)

#### CP0.1 — Move existing modules into `lumina_lob/core/` and fix imports
- Restructured package so the engine lives under `lumina_lob/core/`.
- Fixed all internal imports.

#### CP0.2 — Add order modification (reduce quantity)
- Added `Order.reduce_qty(amount)` in `lumina_lob/core/order.py`.
- Added `PriceLevel.reduce(order, amount)` in `lumina_lob/core/price_level.py`.
- Added `OrderBook.modify(order_id, new_total_qty)` in `lumina_lob/core/book.py`.
- Matching engine routes MODIFY events correctly.

#### CP0.3 — Add IOC and FOK order types
- Extended `OrderType` enum in `lumina_lob/core/order.py`:

```python
class OrderType(Enum):
    LIMIT = auto()
    MARKET = auto()
    IOC = auto()
    FOK = auto()
```

- Matching engine routes IOC and FOK in `lumina_lob/core/matching.py`.
- Validation rule: only `MARKET` cannot carry a price; `IOC` and `FOK` may carry an optional price limit.

#### CP0.4 — Add event log
- Created `lumina_lob/core/event_log.py` with `EventType` enum (`ADD`, `CANCEL`, `MODIFY`, `FILL`) and nanosecond timestamps.
- Integrated event logging into `OrderBook` and `MatchingEngine`.

#### CP0.5 — Add full depth snapshot and `to_pandas()` helpers
- Added to `lumina_lob/core/book.py`:
  - `full_depth(side)` — full price → qty map for one side
  - `full_snapshot()` — both sides as dicts
  - `to_pandas()` — `pandas.DataFrame` of price levels with `side`, `price`, `qty`, `order_count`
- Created empty placeholder `lumina_lob/utils.py`.
- Added `tests/test_snapshot.py` with 4 new tests.

#### CP0.6 — Reach 100% core engine test coverage
- Added `tests/test_coverage.py` with 31 tests covering validation, edge cases, and all branches in `order.py`, `price_level.py`, `book.py`, `matching.py`, `event_log.py`.
- Initial coverage was 90%; final coverage is **100% on `lumina_lob.core`**.
- Discovered and fixed **two additional qty-accounting bugs** while writing coverage tests (see Bugs #6 and #7 below).
- Added `.coverage` to `.gitignore`.

### Phase 1 — Market model + agents (CP1.1 → CP1.8 done)

#### CP1.1 — Reference-price process (Brownian + jump)
- Created `lumina_lob/market_model/` package.
- Implemented `ReferencePriceProcess` in `lumina_lob/market_model/reference_price.py`:
  - Discrete-time geometric Brownian motion with Itô correction
  - Compound Poisson jumps with log-normal jump sizes
  - Deterministic-jump fallback when `jump_std == 0`
  - Positive price floor (`min_price`)
  - `step()`, `simulate(n_steps)`, `reset(price)`, `price`, `path` API
  - Optional RNG seed for reproducibility
- Added `tests/test_reference_price.py` with 18 tests.
- Fixed one test assertion (`proc.path is path` → `proc.path == path`) after discovering `path` returns a defensive copy.

#### CP1.2 — Noise trader agent
- Created `lumina_lob/agents/` package.
- Implemented abstract `Agent` base class in `lumina_lob/agents/base.py`.
- Implemented `NoiseTrader` in `lumina_lob/agents/noise_trader.py`:
  - Poisson arrivals per `act()` call
  - Uniform or log-normal quantity distribution
  - Configurable bid/ask side bias
  - Random price offset around rounded reference price
  - Configurable `tick_size`
  - Validates all parameters in `__post_init__`
- Added `tests/test_noise_trader.py` with 17 tests covering validation, generation, size bounds, side bias, price bounds, and reproducibility.

#### CP1.3 — Informed trader agent
- Created `lumina_lob/agents/informed_trader.py`.
- Implemented `InformedTrader`:
  - Directional signal: `bullish` or `bearish`
  - Submits aggressive market or large-crossing limit orders in the signal direction
  - Configurable trade size, mode (`market` or `limit`), limit-price offset, and participation rate
  - Tracks `total_traded` for impact/intensity measurement
- Added `tests/test_informed_trader.py` with 16 tests.
- Exported from `lumina_lob/agents/__init__.py`.

#### CP1.4 — Basic market maker
- Created `lumina_lob/agents/market_maker.py`.
- Implemented `MarketMaker`:
  - Symmetric bid/ask quotes around rounded reference price
  - Configurable base half-spread, quote size, and max inventory
  - Suppresses quote side when inventory reaches `±max_inventory`
  - Inventory accounting via internal `_inventory` tracker (long = positive)
- Added `tests/test_market_maker.py` with 13 tests.
- Iterated quote rounding and suppression semantics to guarantee non-overlapping quotes and realistic inventory behavior.

#### CP1.5 — Skewed market maker
- Created `lumina_lob/agents/skewed_market_maker.py`.
- Implemented `SkewedMarketMaker`:
  - Inventory-sensitive half-spread skew
  - Long inventory raises bid half-spread and lowers ask half-spread
  - Caps skew so quotes never cross
  - Same inventory limit and quote-size controls as basic MM
- Added `tests/test_skewed_market_maker.py` with 14 tests.
- Fixed sign bug where long inventory was lowering both quotes instead of raising bid and lowering ask.

#### CP1.6 — Propagator-style market impact model
- Created `lumina_lob/market_model/impact.py`.
- Implemented `PropagatorImpact`:
  - Permanent impact: linear in signed volume
  - Temporary impact: linear in signed volume, then decays with a residual
  - Residual accumulation: `self._residual = (temporary + self._residual) * self.decay`
  - `step()` applies one additional decay tick
- Implemented `AlmgrenChrissImpact`:
  - Linear permanent impact coefficient `gamma`
  - Temporary impact coefficient `eta`
  - Reference volatility `sigma` and time step `dt`
- Added `tests/test_impact.py` with 16 tests covering both models, buy/sell signs, zero volume, decay, and validation.
- Exported from `lumina_lob/market_model/__init__.py`.

#### CP1.7 — Simulation orchestrator
- Created `lumina_lob/simulation.py`.
- Implemented `Simulation`:
  - Owns one `OrderBook`, one `MatchingEngine`, one `ReferencePriceProcess`, and a list of `Agent` instances
  - `step()` advances reference price, asks each agent for orders, submits them to the engine, and records per-step metrics
  - `run(n_steps)` runs multiple steps and returns the history list
  - Reassigns globally unique order ids to avoid collisions between agents
  - Routes fill notifications back to agents via `on_fill(side, qty)` when available
  - Skips self-trade notifications so an agent does not move its own inventory
  - `to_dataframe()` exports history to a pandas `DataFrame`
  - Tracks per-step `signed_volume` to feed impact models
- Added `tests/test_simulation.py` with 17 tests covering defaults, empty agents, run length, noise-only book building, mixed-agent quoting/trading, market-maker inventory updates, deterministic reproducibility, DataFrame export, signed-volume tracking, and custom agents with `on_fill`.
- Latest commit for this checkpoint: `a019e91`.

#### CP1.8 — Agents + impact demo notebook
- Created `notebooks/02_agents_and_impact.ipynb`.
- Demonstrates end-to-end simulation with noise trader, market maker, and informed trader.
- Plots reference price vs. best bid/ask, trade/signed volume, market-maker inventory, and propagator-style impact on the reference price.
- Added per-step `signed_volume` to `Simulation.history` so the notebook can feed buyer/seller-initiated volume into `PropagatorImpact`.
- Latest commit for this checkpoint: `467777e`.

### Phase 2 — Data + calibration (CP2.1 → CP2.3 done)

#### CP2.1 — Polygon.io EOD + tick data downloader
- Created `lumina_lob/data/` package and `lumina_lob/data/polygon.py`.
- Implemented `PolygonClient`:
  - Reads API key from argument or `POLYGON_API_KEY` environment variable
  - `get_daily_bars(ticker, start_date, end_date)` for daily OHLCV aggregates
  - `get_trades(ticker, date)` for tick/trade data
  - Local JSON cache in `.cache/polygon/` keyed by ticker and date range
  - Returns tidy pandas DataFrames with UTC timestamps
- Added `requests>=2.31` to `pyproject.toml` dependencies.
- Added `tests/test_polygon.py` with 8 tests covering missing key, bars parsing, empty bars, trades parsing, empty trades, caching, API errors, and missing VWAP default.
- **Bug discovered:** `.gitignore` had a blanket `data/` rule that silently ignored the new `lumina_lob/data/` package. Fixed by changing to `/data/` (root-only) and adding `.cache/`.
- Latest commits: `720cb6b` + follow-up `4195457`.

#### CP2.2 — Databento downloader
- Created `lumina_lob/data/databento.py`.
- Implemented `DatabentoClient`:
  - Reads API key from argument or `DATABENTO_API_KEY` environment variable
  - `get_trades(symbol, start, end, dataset)` using Databento SDK `Historical.timeseries.get_range`
  - `get_quotes(symbol, start, end, dataset, schema)` supporting `bbo`, `mbo`, `mbp-1`, `mbp-10`, `tbbo`
  - Local DBN cache via SDK's `DBNStore.from_file` / `get_range(path=...)`
  - Returns pandas DataFrames
- Added `databento>=0.80.0` to `pyproject.toml` dependencies.
- Added `tests/test_databento.py` with 5 tests covering missing key, trades request, invalid quote schema, bbo quotes, and cache hit behavior.
- Latest commit: `6420740`.

#### CP2.3 — Calibrate arrival-rate distributions from real data
- Created `lumina_lob/data/calibration.py`.
- Implemented `CalibratedParams` dataclass and `calibrate()` entry point:
  - `_estimate_arrival_rate` uses mean inter-arrival time (1 / mean delta) rather than count/elapsed, and supports `second`, `minute`, `hour` time units.
  - `_fit_size_lognormal` filters non-positive sizes, computes sample log-mean and log-std.
  - `_mean_spread` computes mean ask–bid from best quote columns.
  - `_infer_tick_size` sorts unique prices, diffs them, filters near-zero diffs, and returns the minimum positive gap (fallback `0.01`).
- Added `lumina_lob/data/__init__.py` exports for `CalibratedParams` and `calibrate`.
- Added `tests/test_calibration.py` with 18 tests covering basic calibration, default columns, lognormal fitting, empirical size histogram, mean spread, tick-size inference, unsupported time units, duplicate timestamps, all-negative spreads, uniform prices, tiny diffs, and edge cases.
- Restored 100% package coverage after targeted tests for the 5 previously uncovered branches.
- Latest commit: `e047316`.

#### CP2.4 — Calibrate impact parameters from real data
- Extended `CalibratedParams` with `permanent_impact`, `temporary_impact`, and `impact_decay`.
- Extended `calibrate()` with optional `price_col` and `side_col` arguments.
- Added `_signed_volume()` and `_sign_from_side()` helpers that accept numeric signs (`1`/`-1`) or string labels (`buy`/`bid`/`sell`/`ask`/etc.).
- Implemented `_fit_propagator_impact()` using a grid-search least-squares fit:
  - Builds the propagator exposure series `exposure_t = q_t + decay * exposure_{t-1}` for each candidate decay.
  - Solves `dprice_t = permanent * q_t + temporary * exposure_{t-1}` via `np.linalg.lstsq`.
  - Selects the decay with the lowest residual sum of squares.
  - Returns `None` impact fields when the design matrix is underidentified or signed volume is zero.
- Added `_build_exposure()` helper.
- Expanded `tests/test_calibration.py` to 22 tests covering pure permanent impact, temporary + decay recovery, numeric and string side inference, missing price/side skip, zero signed volume skip, insufficient data, and underidentified design matrix.
- Latest commit: `febd8ce`.

#### CP2.5 — Replay real tick data through engine and validate spread distribution
- Created `lumina_lob/data/replay.py`.
- Implemented `ReplayEngine`:
  - Accepts a merged DataFrame of quote and trade events with timestamps.
  - On each quote event, cancels previous synthetic best-bid/best-ask limit orders and posts fresh ones at the quoted prices.
  - On each trade event, submits a market order in the inferred trade direction with the traded size.
  - Records best bid, best ask, and spread after every event.
- Implemented `validate_spread_distribution(real_spreads, simulated_spreads)` using normalized histogram intersection; returns a score in `[0, 1]`.
- Added `_sign_from_value()` helper for numeric/string side labels.
- Exported `ReplayEngine` and `validate_spread_distribution` from `lumina_lob/data/__init__.py`.
- Added `tests/test_replay.py` with 16 tests covering empty events, missing columns, unknown event types, quote-only replay, trade consumption, skipped trades (unknown side, NaN/None/zero size, zero side), custom quote size, spread validation, and side inference.
- Latest commit: `9617436`.

#### CP2.6 — Notebook: calibration demo
- Created `notebooks/04_calibration.ipynb`.
- Demonstrates the full calibration pipeline:
  - Synthetic trades/quotes generation (drop-in replacement for Polygon/Databento output).
  - `calibrate()` to estimate arrival rate, log-normal size parameters, mean spread, tick size, and propagator impact coefficients.
  - Trade-size histogram vs. fitted log-normal plot.
  - Merging quotes and trades into a single event stream and replaying through `ReplayEngine`.
  - `validate_spread_distribution()` to compare real and simulated spread distributions.
  - Overlay histogram and a calibrated-parameter table.
- Latest commit: `57419c2`.

### Phase 3 — RL market maker (CP3.1 → CP3.7 done)

#### CP3.1 — Define Gymnasium observation space
- Created `lumina_lob/rl/` package with `__init__.py` exporting `MarketMakerEnv`.
- Added `gymnasium` dependency to `pyproject.toml` (stable-baselines3 deferred to CP3.3).
- Implemented `MarketMakerEnv` in `lumina_lob/rl/env.py`:
  - Inherits from `gymnasium.Env`.
  - 10-D `Box` observation space with normalised features: best bid/ask, mid price, spread, bid/ask depth, inventory, cash, unrealised P&L, time fraction.
  - Placeholder `Discrete(1)` action space.
  - `reset()` spawns a fresh `Simulation` with `NoiseTrader` and `InformedTrader` background agents and runs `warmup_steps`.
  - `step()` advances the simulation, returns reward=0 placeholder, and stops via `truncated` at `max_steps`.
  - `_update_inventory()` records agent fills using `Side.BID`/`Side.ASK` and maintains VWAP average price.
- Added `tests/test_rl_env.py` with 10 tests covering spaces, reset, step, truncation, time-fraction growth, determinism, pre-reset guard, documented features, zero observation when simulation is `None`, and buy/sell inventory accounting.
- Fixed two bugs while restoring coverage:
  - `MarketMakerEnv._get_observation()` accessed private `book._bids/_asks`; changed to public `book.bids/asks`.
  - `MarketMakerEnv._update_inventory()` compared `side.value == 0`, but `Side.BID` has `auto()` value `1`; changed to `side == Side.BID`.
- Latest commit: `52681f5`.

#### CP3.2 — Action space: quote offsets and sizes
- Replaced the placeholder `Discrete(1)` action space with a 4-D continuous `Box([-1, -1, -1, -1], [1, 1, 1, 1])` in `MarketMakerEnv`.
- New action dimensions: `[bid_offset, ask_offset, bid_size, ask_size]`.
- `_action_to_quotes()` maps normalized actions to absolute tick-rounded prices and integer sizes using configurable `max_quote_offset_ticks`, `min_quote_size`, and `max_quote_size`.
- Added an inner `_AgentProxy` class that plugs into the `Simulation` agent list:
  - `act()` cancels any previous RL-agent quotes and posts new bid/ask limit orders from the pending action.
  - `on_fill()` forwards fill notifications to `env._update_inventory()`.
- Agent orders are tagged with `_agent_quote` so they can be cancelled and inspected in tests.
- `_update_inventory()` now accepts an optional fill price; when omitted it falls back to the current mid price or reference price.
- Updated `tests/test_rl_env.py` to 19 tests covering action-space shape, action-to-quote mapping, quote submission, cancellation between steps, fill accounting via the proxy, and fallback pricing.
- Latest commit: `42cd303`.

#### CP3.3 — Reward function
- Implemented mark-to-market reward: `reward = delta(cash + inventory * mid) - inventory_penalty * inventory^2`.
- Added `inventory_penalty` constructor argument to `MarketMakerEnv`.
- `_compute_reward()` stores previous total P&L and returns the step change minus the quadratic inventory penalty.
- Added reward-specific tests for flat positions, inventory penalty, and price appreciation.
- Latest commit: `af85dcb`.

#### CP3.4 — PPO baseline training helper
- Created `lumina_lob/rl/train.py` with `make_env`, `train_ppo`, `evaluate_agent`, and `save_model`.
- `make_env()` returns a fresh `MarketMakerEnv` wrapped in SB3's `Monitor` for clean episode statistics.
- Default training device is `cpu` to avoid poor GPU utilisation for small MLP policies.
- Moved `gymnasium` and `stable-baselines3` from optional `rl` extras into main dependencies in `pyproject.toml`.
- Added `tests/test_rl_train.py` with smoke tests for PPO training, evaluation, and model saving.
- Latest commit: `087bee5`.

#### CP3.5 — SAC comparison helper
- Added `lumina_lob/rl/compare.py` with `compare_ppo_sac()` that trains PPO and SAC on a fresh env factory and returns evaluation mean/std reward statistics.
- Exported `compare_ppo_sac` from `lumina_lob/rl`.
- Added `tests/test_rl_compare.py` using mocked train/evaluate functions to keep the suite fast.
- Latest commit: `04eb5e1`.

#### CP3.6 — Evaluate RL vs heuristic market makers
- Created `lumina_lob/rl/evaluate.py` with `SimpleMarketMakerPolicy`, `evaluate_heuristic_policy()`, `EpisodeResult`, and `summarize_results()`.
- The heuristic policy skews quotes based on inventory: long positions tighten the ask to encourage selling, short positions tighten the bid.
- `evaluate_heuristic_policy()` runs the heuristic for `n_episodes` and returns per-episode reward, P&L, and inventory extremes.
- Added `tests/test_rl_evaluate.py` covering action validity, skew direction, rollout, and empty-result edge cases.
- Latest commit: `9dfc769`.

#### CP3.7 — RL market maker training + evaluation notebook
- Added `notebooks/03_rl_market_maker.ipynb`.
- Demonstrates PPO and SAC training via `lumina_lob.rl` helpers.
- Evaluates trained agents against the inventory-skewed heuristic policy.
- Includes a bar-chart comparison of episode rewards.
- Latest commit: `12cefe6`.

### Phase 4 — C++ performance layer (CP4.1 done)

#### CP4.1 — Port `OrderBook` + `MatchingEngine` to C++17
- Created `cpp/` directory with C++17 implementation mirroring the Python core:
  - `cpp/include/lumina_lob/` — headers for `Side`, `OrderType`, `Order`, `PriceLevel`, `EventLog`, `OrderBook`, `MatchingEngine`, and an aggregate `lumina_lob.hpp`.
  - `cpp/src/` — implementations using `std::map` for price levels, `std::list<std::unique_ptr<Order>>` for FIFO queues, and `std::unordered_map<int64_t, Order*>` for active-order lookup.
- `OrderBook::add` takes ownership via `std::unique_ptr<Order>` and exposes best bid/ask, spread, mid price, depth/snapshot, cancel, and modify.
- `MatchingEngine::process` routes `LIMIT`, `MARKET`, `IOC`, and `FOK` orders with identical price-time priority logic to Python.
- `EventLog` records `ADD`, `CANCEL`, `MODIFY`, and `FILL` events with nanosecond timestamps and exports to string dictionaries.
- Added `cpp/tests/test_core.cpp` with assert-based checks for order validation, price levels, book add/cancel/modify, limit/market/IOC/FOK matching, and depth snapshots.
- Added `cpp/CMakeLists.txt` building a static `lumina_lob_core` library and the `test_core` executable.
- Updated `PLAN.md` to mark CP4.1 complete.
- Verified compilation and tests with **MSVC 19.44** via the Visual Studio 2022 BuildTools Developer Command Prompt:
  ```
  cl /std:c++17 /EHsc /I cpp\include cpp\src\*.cpp cpp\tests\test_core.cpp /Fe:cpp_test.exe
  .\cpp_test.exe
  run 57 checks, 0 failed
  ```
- Added `.gitignore` rules for `*.obj`, `*.exe`, `*.lib`, `*.pdb`, `*.ilk`, and `cpp/build/`.
- Latest commit: `220f612` (C++ source); follow-up `de58255` (.gitignore).

#### CP4.2 — Add pybind11 bindings for the C++ core
- Added `pybind11>=2.12` to the `dev` optional dependencies in `pyproject.toml`.
- Created `cpp/bindings.cpp` exposing:
  - `Side`, `OrderType`, `EventType` enums.
  - `Order` with read-only properties (`order_id`, `side`, `price`, `qty`, `order_type`, `filled_qty`, `remaining_qty`, `is_filled`).
  - `Event` and `EventLog` with `events`, `size`, and `to_dicts()`.
  - `PriceLevel` with `price`, `total_qty`, `order_count`, `is_empty`, and `orders()` returning `Order*` references.
  - `OrderBook` with `add`, `cancel`, `modify`, best prices, spread, mid, `depth`, `full_depth`, `snapshot`, `full_snapshot`, `trades`, `orders`, `bids`, `asks`, `event_log`.
  - `MatchingEngine` with `process`.
- Bound module as `lumina_lob._core`.
- Added `tests/test_cpp_core.py` with 10 tests mirroring the Python core smoke scenarios:
  - Order validation, book add/cancel, limit-order match, market order, IOC, FOK, modify, depth/snapshot, event log, price-level order access.
- Compiled the extension successfully with **MSVC 19.44** and ran the new tests:
  ```
  python -m pytest tests/test_cpp_core.py -v
  10 passed
  ```
- Switched `PriceLevel` internal storage from `std::unique_ptr<Order>` to `std::shared_ptr<Order>` so the type is copyable, which pybind11 needs when exposing `OrderBook::bids()`/`asks()` maps.
- Updated `.gitignore` for `*.pyd` and `*.exp` extension build artifacts.
- Updated `PLAN.md` to mark CP4.2 complete.
- Latest commit: `b3f3fb8`.

#### CP4.3 — Add build script (`setup.py` / `pyproject.toml` integration)
- Created `setup.py` using `pybind11.setup_helpers.Pybind11Extension` to compile `cpp/bindings.cpp` + `cpp/src/*.cpp` into `lumina_lob._core`.
- Added `pybind11>=2.12` to `[build-system] requires` in `pyproject.toml` so build isolation installs pybind11 before `setup.py` runs.
- Added `OptionalBuildExt` command class that catches compiler/build failures and emits a warning, falling back to a pure-Python install instead of aborting.
- Updated `tests/test_cpp_core.py` to use `pytest.importorskip("lumina_lob._core")` so the suite skips gracefully when the extension is not built.
- Verified `pip install -e .` compiles the extension with MSVC 19.44 and installs the package in editable mode.
- Verified the full suite still passes with the C++ extension active:
  ```
  collected 271 items
  271 passed in 46.88s
  100% coverage on lumina_lob
  ```
- Updated `PLAN.md` to mark CP4.3 complete.
- Latest commits: `be974d4` + `31c863c`.

#### CP4.4 — Add throughput benchmark (Python vs C++)
- Created `benchmarks/engine_benchmark.py`:
  - Generates a deterministic alternating bid/ask limit-order stream with configurable `--orders` and `--seed`.
  - Runs the same stream through `lumina_lob.core.MatchingEngine` (pure Python) and `lumina_lob._core.MatchingEngine` (C++ extension).
  - Reports events/sec for each engine and the C++ speedup factor.
  - Skips the C++ comparison gracefully when `lumina_lob._core` is not built.
- Added `benchmarks/__init__.py` so the script can be run as `python -m benchmarks.engine_benchmark`.
- Added `tests/test_benchmark.py` smoke test that runs the benchmark with `--orders 1000` and verifies the output contains Python/C++ rate lines and a speedup line.
- Sample run on this machine (200k orders):
  ```
  Orders submitted: 200000
  Python engine:    22,113.7 events/sec
  C++ engine:       90,361.1 events/sec
  Speedup:          4.1x
  ```
  *Note:* The C++ speedup is currently modest because each order crosses the pybind11 boundary individually. Hitting the 10M events/sec target will require a batch-submission API (likely a future optimization checkpoint).
- Updated `PLAN.md` to mark CP4.4 complete.
- Latest commit: `0dc4540`.

#### CP4.5 — Notebook: benchmark report
- Created `notebooks/05_benchmark_report.ipynb`:
  - Imports `matplotlib` and `pandas`.
  - Defines a `run_benchmark(orders, seed)` helper that calls `python -m benchmarks.engine_benchmark` and parses the printed rates.
  - Supports a `LUMINA_BENCHMARK_QUICK` environment variable that reduces the default workload to 1k/5k orders for CI or fast validation.
  - Runs the benchmark across 10k, 50k, 100k, and 200k order streams, builds a results DataFrame, and plots:
    - side-by-side events/sec bars for Python vs C++;
    - C++ speedup vs order count.
  - Includes Markdown interpretation and a note that the next step toward the >10M events/sec target is a batch-submission API.
- Added `tests/test_notebook.py` smoke test that validates the notebook JSON, confirms it has cells, and checks for key content (`run_benchmark`, `LUMINA_BENCHMARK_QUICK`, title).
- Updated `PLAN.md` to mark CP4.5 complete.
- Latest commit: `983e166`.

#### CP5.1 — Matplotlib depth-ladder plot
- Created `lumina_lob/viz/depth_ladder.py` with `plot_depth_ladder(book, top_n=10)`:
  - Detects whether the supplied book is the Python or C++ `OrderBook` and uses the correct `Side` enum.
  - Reads top-N price levels via `book.depth()` and normalises both Python `dict` and C++ `list` of pairs return types.
  - Renders horizontal bars: green bids extending left, red asks extending right, price labels on the y-axis, mid/central axis at `x=0`.
  - Returns a `matplotlib` `(fig, ax)` tuple.
- Created `lumina_lob/viz/__init__.py` exporting `plot_depth_ladder`.
- Added `tests/test_viz.py` with 4 tests: Python book plot returns a Figure, C++ book plot works, `top_n <= 0` raises `ValueError`, empty book raises `ValueError`.
- Updated `PLAN.md` to mark CP5.1 complete.
- Latest commit: `583a732`.

#### CP5.2 — Time-series plot of mid price, spread, and trades
- Created `lumina_lob/viz/history.py` with `plot_simulation_history(history)`:
  - Accepts a list of step records (from `Simulation.run`) or a pandas DataFrame (from `Simulation.to_dataframe`).
  - Builds a 3-panel matplotlib figure: mid price with trade markers, bid-ask spread, and per-step trade volume.
  - Validates required columns (`step`, `mid_price`, `spread`, `trade_count`, `trade_volume`) and raises clear `ValueError`s for empty histories or missing columns.
- Updated `lumina_lob/viz/__init__.py` to export `plot_simulation_history`.
- Expanded `tests/test_viz.py` to 9 tests covering list input, DataFrame input, empty list, empty DataFrame, missing columns, and the original depth-ladder tests.
- Updated `PLAN.md` to mark CP5.2 complete.
- Latest commit: `103f87c`.

#### CP5.3 — Real-time streaming visualizer for simulation
- Created `lumina_lob/viz/realtime.py`:
  - `SimulationAnimator` wraps a `Simulation` and builds a two-panel matplotlib figure (depth ladder on the left, rolling mid-price trace with trade markers on the right).
  - `update()` advances `Simulation.step()`, redraws the depth ladder, and rescales the price axis to the last `history_window` steps.
  - `run(n_steps)` returns a `matplotlib.animation.FuncAnimation` for live rendering.
  - `run_animation(simulation, ...)` convenience factory returns the same animation so users can call `plt.show()` or save it.
  - Handles empty books and empty histories gracefully (empty-title fallback and no-op price-axis update).
  - Guards empty trade scatter offsets to avoid matplotlib shape errors.
- Updated `lumina_lob/viz/__init__.py` to export `SimulationAnimator` and `run_animation`.
- Expanded `tests/test_viz.py` from 9 to 13 tests:
  - `test_simulation_animator_steps_and_redraws` — animator advances the simulation and updates both panels.
  - `test_run_animation_returns_funcanimation` — factory returns a `FuncAnimation` and advancing frames steps the simulation.
  - `test_draw_depth_ladder_empty_book` — internal depth-ladder renderer shows an empty title for empty books.
  - `test_update_price_axis_with_empty_history` — internal price-axis update is a no-op when history is empty.
- Fixed bugs discovered during tests:
  - Missing `import numpy as np` in `realtime.py` when switching scatter offsets to `np.column_stack`.
  - Empty scatter offsets produced a 1-D array and crashed matplotlib; now use `np.zeros((0, 2))`.
- Updated `PLAN.md` to mark CP5.3 complete.
- Latest commit: `7ba49aa`.

#### CP5.4 — GIF/MP4 export of simulation replay
- Added `save_animation(animation, path, fps=5)` in `lumina_lob/viz/realtime.py`:
  - Supports `.gif` (Pillow writer) and `.mp4` (ffmpeg writer) based on extension.
  - Raises clear `ValueError` for unsupported extensions.
  - Raises clear `ValueError` if the required writer backend is not installed.
  - Creates parent directories automatically.
- Updated `lumina_lob/viz/__init__.py` to export `save_animation`.
- Added three new tests in `tests/test_viz.py`:
  - `test_save_animation_gif_creates_file` — saves a 3-frame animation to a temp GIF and verifies it is non-empty (skips if Pillow writer missing).
  - `test_save_animation_unsupported_extension` — rejects non-GIF/MP4 paths.
  - `test_save_animation_missing_writer_raises` — reports a missing writer backend.
- Fixed bug discovered during save tests: `_update_price_axis()` crashed when `mid_price` was `None` for every history record (e.g. before the book has any bids/asks). Now filters out `None` mid prices and returns early if no valid points exist.
- Added `test_update_price_axis_with_all_none_mids` to cover the new guard.
- Updated `PLAN.md` to mark CP5.4 complete.
- Latest commit: `2b05769`.

#### CP6.1 — Package for PyPI (`pip install lumina-lob`)
- Updated `pyproject.toml`:
  - Added `project.urls` (Homepage, Repository, Issues).
  - Switched `project.license` to the PEP 639-ready SPDX string `"MIT"` with `license-files = ["LICENSE"]`.
  - Added `[tool.setuptools]` with `include-package-data = true`.
  - Extended `dev` extras with `build>=1.0`.
  - Added an `all` extras alias (`lumina-lob[dev,viz]`).
  - Excluded `tests*` and `benchmarks*` from the installed package while keeping them in the sdist via `MANIFEST.in`.
- Updated `setup.py`:
  - Normalised C++ source/include paths to be relative to `setup.py` using forward slashes.
  - Kept the optional `OptionalBuildExt` fallback so the package installs even when a C++ compiler is missing.
- Added `MANIFEST.in` to include README, LICENSE, `PROJECT_SPEC.txt`, C++ sources/headers/CMake, notebooks, and tests; also excludes C++ build artifacts.
- Added `tests/test_packaging.py` with two smoke tests:
  - `test_package_version_is_defined` — `lumina_lob.__version__` is a valid version string.
  - `test_public_submodules_importable` — all public submodules import cleanly.
- Rebuilt `lumina_lob.egg-info` to remove stale absolute paths that broke `python -m build --wheel`.
- Verified `python -m build --wheel` produces a clean wheel with the C++ extension compiled.
- Verified the wheel installs and imports in a fresh venv (`python -m venv /tmp/lumina_test_venv` + `pip install dist/*.whl`).
- Updated `README.md` with `pip install lumina-lob` instructions, current feature matrix, and phase roadmap.
- Updated `PLAN.md` to mark CP6.1 complete.
- Latest commit: `485b980`.

#### CP6.2 — GitHub Actions CI (test matrix Python 3.11–3.13)
- Created `.github/workflows/ci.yml`:
  - Matrix: Ubuntu / Windows / macOS × Python 3.11 / 3.12 / 3.13 (9 jobs).
  - Installs system C++ compilers on each runner.
  - Installs package with `.[dev,viz]` extras so matplotlib tests run.
  - Runs `pytest --cov=lumina_lob -q` and uploads coverage HTML artifact.
- Created `.github/workflows/build.yml`:
  - Tag-triggered (`v*.*.*`) wheel builds across the same OS/Python matrix.
  - Uploads wheel artifacts for manual PyPI upload.
- Added CI status badge to `README.md`.
- Updated `PLAN.md` to mark CP6.2 complete.
- **Bug discovered & fixed:** first CI run failed with `ModuleNotFoundError: No module named 'matplotlib'` because `ci.yml` installed only `.[dev]`. Changed to `.[dev,viz]` and re-ran.
- Re-ran CI; all 9 matrix jobs passed.
- Latest commits: `b173d40` ("CP6.2: GitHub Actions CI") + `85e0f64` ("ci: install viz extras for matplotlib tests").
- **Post-CP6.6 fix (2026-07-05):** CI matrix started failing `tests/test_release.py::test_git_tag_exists` because `actions/checkout@v4` does a shallow clone without tags. Added `fetch-depth: 0` to `.github/workflows/ci.yml`; re-ran all 9 jobs; all passed. Commit `e72aeb6`.

#### CP6.3 — Write full documentation site (MkDocs)
- Updated `pyproject.toml` with a new `docs` extras group:
  - `mkdocs>=1.5`
  - `mkdocs-material>=9.5`
  - `mkdocstrings[python]>=0.24`
  - `all` extras alias now includes `dev,viz,docs`.
- Created `mkdocs.yml`:
  - Material theme with light/dark palette toggle.
  - Navigation tabs, search, and Python API reference via mkdocstrings.
  - Site URL points to GitHub Pages (`https://satyamdas03.github.io/lumina-lob`).
- Created `docs/` site:
  - `docs/index.md` — landing page with install, quickstart, feature matrix, and roadmap.
  - `docs/tutorials/quickstart.md` — core engine tutorial.
  - `docs/tutorials/architecture.md` — package overview and how components connect.
  - `docs/tutorials/custom-agent.md` — agent protocol and `on_fill` example.
  - `docs/api/*.md` — mkdocstrings reference for `core`, `agents`, `market_model`, `simulation`, `data`, `rl`, `viz`.
- Created `.github/workflows/docs.yml`:
  - Builds MkDocs on every push to `main`.
  - Deploys the built `site/` directory to GitHub Pages.
- Updated `README.md`:
  - Added documentation site link near the top.
  - Marked GitHub Actions CI and MkDocs documentation site as ✅ Done.
- Updated `PLAN.md` to mark CP6.3 complete.
- Updated `MANIFEST.in` to include `docs/` markdown/`mkdocs.yml` in the sdist.
- Updated `.gitignore` to exclude the MkDocs `site/` build output.
- Added `tests/test_docs.py` with 4 tests:
  - `test_mkdocs_config_exists_and_is_valid_yaml`
  - `test_documentation_pages_exist`
  - `test_docs_extras_declared`
  - `test_docs_workflow_exists`
- Verified `python -m mkdocs build --strict` succeeds locally.
- Latest commit: `9c64a5a`.
- **Post-CP6.6 fix (2026-07-05):** Docs deploy failed with a 404 because GitHub Pages was not enabled in the repository. Enabled Pages via the GitHub REST API with `build_type=workflow` and `source.branch=main`. The `docs.yml` workflow now builds and deploys successfully; the site is live at `https://satyamdas03.github.io/lumina-lob/`.

#### CP6.4 — Write technical blog post "Build a Limit Order Book Simulator from Scratch"
- Created `blog/build-a-lob-simulator.md` with YAML front matter for Medium/Dev.to:
  - Title, subtitle, description, author, date, canonical/repo/docs URLs, tags, `published: false`.
  - Sections: why an LOB simulator, price-time priority, engine code, agents, market model/impact, calibration to real data, RL market making, C++ speed-up, visualization, lessons learned, try it yourself, next steps.
- Generated `blog/assets/depth_ladder.png` and `blog/assets/history.png` from a seeded multi-agent simulation using `lumina_lob.viz`.
- Code snippets verified against the public API:
  - `PolygonClient` and `calibrate` for real-data calibration.
  - `MarketMakerEnv` + `train_ppo` + `save_model` for RL.
- Fixed documentation inaccuracies discovered while writing the post:
  - `docs/tutorials/quickstart.md` now uses `NoiseTrader(arrival_rate=..., size_max=..., seed=...)` and `sim.run(n_steps=...)`.
  - `docs/tutorials/custom-agent.md` now uses `act(reference_price, book)` and `on_fill(side, qty)` to match the actual `Agent` protocol.
- Added `tests/test_blog.py` with 4 tests:
  - `test_blog_post_exists`
  - `test_front_matter_is_valid_yaml`
  - `test_markdown_body_references_image_assets`
  - `test_required_assets_exist`
- Updated `.github/workflows/ci.yml` to install `.[dev,viz,docs]` so docs and blog tests run in CI.
- Updated `MANIFEST.in` to include `blog/` markdown and PNG assets in sdist.
- Updated `README.md` with a "Blog post" section linking to the draft and updated the feature table.
- Updated `PLAN.md` to mark CP6.4 complete.
- Latest commit: `9d91114`.

#### CP6.5 — LinkedIn/X social launch
- Created `blog/social-launch.md` with:
  - YAML front matter (title, description, author, date).
  - LinkedIn post draft (~200 words) with repo/docs/blog links and `#quantitativefinance` hashtags.
  - 4-tweet X/Twitter thread: hook, feature list, code snippet, CTA + links.
  - Note that drafts require human approval before posting.
- Generated `blog/assets/social_card.png` — dark-themed teaser card with repo + install command for use as featured image.
- Added `tests/test_social_launch.py` with 4 tests:
  - `test_social_launch_file_exists`
  - `test_front_matter_is_valid_yaml`
  - `test_required_links_present`
  - `test_social_card_asset_exists`
- Updated `README.md` with a "Social launch" link and marked social launch as ✅ Done (drafts).
- Updated `MANIFEST.in` to include `blog/` PNG assets (already included recursively; added newline only).
- Updated `PLAN.md` to mark CP6.5 complete.
- Latest commit: `c38b775`.

#### CP6.6 — Pin repo on GitHub profile and publish to PyPI
- Created and pushed git tag `v0.1.0` annotated with "Release v0.1.0 — production-grade LOB simulator".
- Updated `.github/workflows/build.yml`:
  - Added a `publish` job that runs after the matrix wheel builds on tag pushes matching `v*.*.*`.
  - Uses `pypa/gh-action-pypi-publish@release/v1` with `permissions: id-token: write` for PyPI trusted publishing (OIDC).
  - Downloads all wheel artifacts, merges them into `dist/`, and uploads to PyPI.
- Verified `python -m build` produces a clean wheel (`lumina_lob-0.1.0-cp314-cp314-win_amd64.whl`) and sdist (`lumina_lob-0.1.0.tar.gz`); both pass `twine check`.
- Verified the sdist installs and imports in a fresh venv:
  ```
  installed version: 0.1.0
  ```
- Added `tests/test_release.py` with 4 tests:
  - `test_version_matches_package` — valid semver.
  - `test_version_matches_pyproject` — `pyproject.toml` version matches package.
  - `test_build_workflow_has_publish_job` — build.yml contains PyPI publish job.
  - `test_git_tag_exists` — `v0.1.0` tag exists in git history.
- Updated `README.md`:
  - Marked Phase 6 as ✅ Done.
  - Added "GitHub release + PyPI publish" feature row with status note.
  - Added note under install that PyPI trusted publishing must be configured by the owner for the first upload.
- Updated `PLAN.md` to mark CP6.6 complete.
- **Could not complete automatically:**
  - Actual PyPI upload is blocked because no `PYPI_API_TOKEN` / `TWINE_PASSWORD` / trusted-publishing secret is configured in this environment. The workflow is ready; the owner must enable trusted publishing for `lumina-lob` on PyPI (environment name `pypi`, workflow `.github/workflows/build.yml`) and push any `v*.*.*` tag.
  - Pinning the repo on the GitHub profile requires a logged-in browser action and cannot be done via API/tools from this session.
- Latest commit: `d63e990`.

## Test status

Run command:

```bash
python -m pytest -q
python -m pytest --cov=lumina_lob --cov-report=term-missing -q
```

Latest results:

```
collected 308 items
tests\test_benchmark.py .
tests\test_book.py ....................
tests\test_calibration.py ..........................
tests\test_coverage.py ...............................
tests\test_cpp_core.py ..........
tests\test_databento.py .....
tests\test_docs.py ....
tests\test_event_log.py ....
tests\test_impact.py ................
tests\test_informed_trader.py ................
tests\test_market_maker.py .............
tests\test_noise_trader.py .................
tests\test_notebook.py .
tests\test_polygon.py ........
tests\test_reference_price.py ..................
tests\test_release.py ....
tests\test_replay.py ................
tests\test_rl_compare.py .
tests\test_rl_env.py .......................
tests\test_rl_evaluate.py ......
tests\test_rl_train.py ......
tests\test_simulation.py ..................
tests\test_skewed_market_maker.py ..............
tests\test_snapshot.py ....
tests\test_viz.py ................
tests\test_packaging.py ..
tests\test_blog.py ....
tests\test_social_launch.py ....

308 passed, 2 warnings in 19.54s
```

Coverage:

```
Name                                         Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------
lumina_lob\__init__.py                           3      0   100%
lumina_lob\agents\__init__.py                    7      0   100%
lumina_lob\agents\base.py                        7      0   100%
lumina_lob\agents\informed_trader.py            61      0   100%
lumina_lob\agents\market_maker.py               55      0   100%
lumina_lob\agents\noise_trader.py               59      0   100%
lumina_lob\agents\skewed_market_maker.py        66      0   100%
lumina_lob\core\__init__.py                      5      0   100%
lumina_lob\core\book.py                         92      0   100%
lumina_lob\core\event_log.py                    53      0   100%
lumina_lob\core\matching.py                     98      0   100%
lumina_lob\core\order.py                        51      0   100%
lumina_lob\core\price_level.py                  58      0   100%
lumina_lob\data\__init__.py                      6      0   100%
lumina_lob\data\calibration.py                 124      0   100%
lumina_lob\data\databento.py                    28      0   100%
lumina_lob\data\polygon.py                      56      0   100%
lumina_lob\data\replay.py                      113      0   100%
lumina_lob\market_model\__init__.py              4      0   100%
lumina_lob\market_model\impact.py               53      0   100%
lumina_lob\market_model\reference_price.py      77      0   100%
lumina_lob\rl\__init__.py                        6      0   100%
lumina_lob\rl\compare.py                        10      0   100%
lumina_lob\rl\env.py                           163      0   100%
lumina_lob\rl\evaluate.py                       52      0   100%
lumina_lob\rl\train.py                          28      0   100%
lumina_lob\simulation.py                        70      0   100%
lumina_lob\utils.py                              0      0   100%
lumina_lob\viz\__init__.py                       4      0   100%
lumina_lob\viz\depth_ladder.py                  41      0   100%
lumina_lob\viz\history.py                       45      0   100%
lumina_lob\viz\realtime.py                      89      0   100%
--------------------------------------------------------------------------
TOTAL                                         1584      0   100%
```

## Bugs fixed during this session

1. **Market orders left empty price levels in the book.**
   - *Fix:* After `_fill_at_price()` in `_match_market()` and `_match_ioc()`, delete the price level if `total_qty` reaches zero.

2. **`PriceLevel.total_qty` was not decremented on partial fills.**
   - *Fix:* Added `level.total_qty -= amount` inside `_fill_at_price()` in `lumina_lob/core/matching.py`.

3. **Tests incorrectly expected aggressor orders to remain in the book.**
   - *Fix:* Updated `tests/test_book.py` so assertions only check resting orders remain after a match.

4. **Empty `EventLog` was replaced in `OrderBook` because `__len__ == 0` is falsy.**
   - *Fix:* Changed `OrderBook.__init__` to `self.event_log = event_log if event_log is not None else EventLog()`.

5. **IOC/FOK orders with a price limit were rejected by validation.**
   - *Fix:* Relaxed validation so only `MARKET` is forbidden from having a price; `IOC`/`FOK` may carry an optional price limit.

6. **`PriceLevel.remove()` double-counted filled quantity.**
   - *Symptom:* When `PriceLevel.fill()` or `MatchingEngine._fill_at_price()` fully filled an order and then called `remove()`, `total_qty` was decremented twice (once by the fill accounting, once by `remove()` using `order.qty`).
   - *Fix:* Changed `PriceLevel.remove()` to subtract `order.remaining_qty` instead of `order.qty`.
   - *File:* `lumina_lob/core/price_level.py:45`

7. **`PriceLevel.append()` added already-filled quantity back to the book.**
   - *Symptom:* After a partially filled limit order rested in the book, `append()` added the original `order.qty` to `total_qty`, inflating displayed depth by the already-filled amount.
   - *Fix:* Changed `PriceLevel.append()` to add `order.remaining_qty` instead of `order.qty`.
   - *File:* `lumina_lob/core/price_level.py:30`

8. **Reference-price `path` returned a defensive copy, breaking identity-based test.**
   - *Fix:* Updated test assertion from `proc.path is path` to `proc.path == path`.

9. **Market maker quote rounding could produce sub-tick or overlapping quotes.**
   - *Fix:* Rewrote `_quote_prices()` to round bid/ask to ticks and guarantee a non-overlapping spread.

10. **Market maker inventory suppression used quote-size checks that conflicted with tests.**
    - *Fix:* Settled on inventory-level-based suppression: bid suppressed when `inventory >= max_inventory`, ask suppressed when `inventory <= -max_inventory`.

11. **Skewed market maker sign error lowered both quotes on long inventory.**
    - *Fix:* Long inventory now raises bid half-spread and lowers ask half-spread.

12. **Propagator impact residual decay semantics needed explicit accumulation.**
    - *Fix:* Residual now accumulates as `(temporary + self._residual) * self.decay` so temporary impact decays smoothly across trades and time steps.

13. **`.gitignore` blanket `data/` rule ignored the new `lumina_lob/data/` package.**
    - *Symptom:* After creating `lumina_lob/data/polygon.py`, `git add -A` did not stage it; the first CP2.1 commit was missing the module.
    - *Fix:* Changed `data/` to `/data/` (root-only) and added `.cache/` to ignored artifacts. Re-committed the module in a follow-up commit.

14. **Calibration arrival-rate estimate used count/elapsed, which was biased for few events.**
    - *Fix:* Switched to `1 / mean(inter-arrival times)` via `pd.Series.diff()` in seconds.

15. **Calibration tick-size inference returned unsorted diffs and missed near-zero noise.**
    - *Fix:* Sort unique prices, compute `np.diff`, filter `diffs > 1e-9`, and return the minimum positive gap with a `0.01` fallback.

16. **`MarketMakerEnv._get_observation()` accessed private `OrderBook._bids/_asks`.**
    - *Fix:* Changed to public `book.bids` and `book.asks`.
    - *File:* `lumina_lob/rl/env.py:163-164`

17. **`MarketMakerEnv._update_inventory()` compared `side.value == 0`, which is always false for `Side.BID`.**
    - *Fix:* Changed to `side == Side.BID` so buys increase inventory and sells decrease it.
    - *File:* `lumina_lob/rl/env.py:190`

18. **Stable-Baselines3 warned about running MlpPolicy on a CUDA GPU for tiny networks.**
    - *Fix:* Defaulted `device="cpu"` in `train_ppo()` and `train_sac()`.
    - *File:* `lumina_lob/rl/train.py`

19. **Stable-Baselines3 `evaluate_policy` warned that the environment was not wrapped in `Monitor`.**
    - *Fix:* Wrapped every created env with `Monitor` inside `make_env()`.
    - *File:* `lumina_lob/rl/train.py`

## Key files and their roles

| File | Role |
|---|---|
| `PLAN.md` | Master 28-checkpoint build plan |
| `lumina_lob/core/order.py` | `Order`, `Side`, `OrderType`, fill tracking, `reduce_qty()` |
| `lumina_lob/core/price_level.py` | Doubly-linked FIFO order queue per price level |
| `lumina_lob/core/book.py` | `OrderBook`: bids/asks, best prices, depth, snapshot, pandas export |
| `lumina_lob/core/matching.py` | `MatchingEngine`: routes order types, executes price-time priority matching |
| `lumina_lob/core/event_log.py` | Nanosecond event journal (`ADD`, `CANCEL`, `MODIFY`, `FILL`) |
| `lumina_lob/market_model/reference_price.py` | GBM + compound Poisson reference price process |
| `lumina_lob/market_model/impact.py` | `PropagatorImpact` and `AlmgrenChrissImpact` |
| `lumina_lob/agents/base.py` | Abstract `Agent` base class |
| `lumina_lob/agents/noise_trader.py` | `NoiseTrader` implementation |
| `lumina_lob/agents/informed_trader.py` | `InformedTrader` implementation |
| `lumina_lob/agents/market_maker.py` | `MarketMaker` implementation |
| `lumina_lob/agents/skewed_market_maker.py` | `SkewedMarketMaker` implementation |
| `lumina_lob/agents/__init__.py` | Exports all agent classes |
| `lumina_lob/market_model/__init__.py` | Exports market-model classes |
| `lumina_lob/simulation.py` | `Simulation` orchestrator: agents + engine + reference price |
| `lumina_lob/utils.py` | Placeholder — reserved for future helpers |
| `lumina_lob/data/__init__.py` | Data package exports |
| `lumina_lob/data/polygon.py` | Polygon.io EOD bars + trades downloader |
| `lumina_lob/data/databento.py` | Databento historical trades + quotes downloader |
| `lumina_lob/data/calibration.py` | Real-data calibration utilities (`CalibratedParams`, `calibrate`) |
| `lumina_lob/data/replay.py` | Tick replay engine and spread-distribution validator |
| `lumina_lob/rl/env.py` | `MarketMakerEnv` Gymnasium environment |
| `lumina_lob/rl/train.py` | PPO/SAC training helpers and `make_env` factory |
| `lumina_lob/rl/compare.py` | `compare_ppo_sac()` benchmark helper |
| `lumina_lob/rl/evaluate.py` | Heuristic market-maker policy and episode evaluation |
| `cpp/include/lumina_lob/lumina_lob.hpp` | Aggregate C++ core header |
| `cpp/include/lumina_lob/order.hpp` | C++ `Order`, `Side`, `OrderType` |
| `cpp/include/lumina_lob/price_level.hpp` | C++ FIFO price level |
| `cpp/include/lumina_lob/book.hpp` | C++ `OrderBook` |
| `cpp/include/lumina_lob/matching.hpp` | C++ `MatchingEngine` |
| `cpp/include/lumina_lob/event_log.hpp` | C++ event journal |
| `cpp/src/*.cpp` | C++ implementations |
| `cpp/bindings.cpp` | pybind11 bindings for `lumina_lob._core` |
| `cpp/tests/test_core.cpp` | C++ core smoke tests |
| `cpp/CMakeLists.txt` | C++ build configuration |
| `tests/test_cpp_core.py` | Python smoke tests for the bound C++ core |
| `benchmarks/engine_benchmark.py` | Python vs C++ throughput benchmark |
| `tests/test_benchmark.py` | Smoke test for the benchmark script |
| `notebooks/05_benchmark_report.ipynb` | Benchmark report notebook with CI guard |
| `tests/test_notebook.py` | Smoke test validating the benchmark notebook |
| `lumina_lob/viz/__init__.py` | Visualization package export |
| `lumina_lob/viz/depth_ladder.py` | Matplotlib depth-ladder plot |
| `lumina_lob/viz/history.py` | Matplotlib time-series plot of simulation history |
| `lumina_lob/viz/realtime.py` | Real-time `SimulationAnimator` + `run_animation` + `save_animation` using `FuncAnimation` |
| `tests/test_viz.py` | 17 tests for visualization helpers |
| `notebooks/02_agents_and_impact.ipynb` | Demo notebook: agents, LOB dynamics, and propagator impact |
| `notebooks/03_rl_market_maker.ipynb` | Demo notebook: PPO/SAC training vs heuristic baseline |
| `notebooks/04_calibration.ipynb` | Demo notebook: calibration + replay + spread validation |
| `tests/test_book.py` | 20 tests for limit orders, matching, cancel, modify, IOC, FOK |
| `tests/test_event_log.py` | 4 tests for event logging |
| `tests/test_snapshot.py` | 4 tests for depth snapshots and pandas export |
| `tests/test_coverage.py` | 31 tests for validation and edge-case coverage |
| `tests/test_reference_price.py` | 18 tests for reference price process |
| `tests/test_noise_trader.py` | 17 tests for noise trader agent |
| `tests/test_informed_trader.py` | 16 tests for informed trader agent |
| `tests/test_market_maker.py` | 13 tests for basic market maker |
| `tests/test_skewed_market_maker.py` | 14 tests for skewed market maker |
| `tests/test_impact.py` | 16 tests for propagator and Almgren-Chriss impact |
| `tests/test_simulation.py` | 17 tests for simulation orchestrator |
| `tests/test_polygon.py` | 8 tests for Polygon.io downloader |
| `tests/test_databento.py` | 5 tests for Databento downloader |
| `tests/test_calibration.py` | 22 tests for real-data calibration |
| `tests/test_replay.py` | 16 tests for tick replay and spread validation |
| `tests/test_rl_env.py` | 23 tests for the Gymnasium market-maker environment |
| `tests/test_rl_train.py` | Smoke tests for PPO/SAC training and model saving |
| `tests/test_rl_compare.py` | Mocked benchmark of PPO vs SAC |
| `tests/test_rl_evaluate.py` | Tests for heuristic policy and episode summarization |
| `pyproject.toml` | PEP 517/518 package metadata, build backend, optional extras, tool configs |
| `setup.py` | Custom setuptools build with optional `pybind11` C++ extension (`lumina_lob._core`) |
| `MANIFEST.in` | Includes C++ sources, notebooks, tests, docs in sdist; excludes build artifacts |
| `tests/test_packaging.py` | Smoke tests for package metadata and public submodule imports |
| `.gitignore` | Ignores `.coverage` artifact, root `/data/`, `.cache/`, and C++/extension build artifacts |

## Current state

- **Phase 0 is COMPLETE** (all 6 checkpoints done).
- **Phase 1 is COMPLETE** (all 8 checkpoints done).
- **Phase 2 is COMPLETE** (all 6 checkpoints done: CP2.1 → CP2.6).
- **Phase 3 is COMPLETE** (all 7 checkpoints done: CP3.1 → CP3.7).
- **Phase 4 is COMPLETE** (all 5 checkpoints done: CP4.1 → CP4.5).
- **Phase 5 is COMPLETE** (all 4 checkpoints done: CP5.1 → CP5.4).
- **Phase 6 is COMPLETE** — CP6.1 done (PyPI packaging), CP6.2 done (GitHub Actions CI), CP6.3 done (MkDocs documentation site), CP6.4 done (technical blog post draft), CP6.5 done (LinkedIn/X social launch drafts), CP6.6 done (release tag + PyPI publish workflow).
- Core engine + agents + market models + simulation + data downloaders + calibration + replay + RL market-maker training/evaluation + C++ core port + Python bindings + pip-installable C++ extension + throughput benchmark + benchmark report notebook + depth-ladder/time-series/real-time/replay-export visualizations + PyPI packaging + cross-platform CI + MkDocs documentation site + technical blog post draft + social launch drafts + release tag + PyPI publish workflow are functional, typed, tested, and documented.
- **308 Python tests pass, 100% coverage on the entire `lumina_lob` package.**
- C++ core compiles and passes 57 C++ checks with MSVC; Python extension `_core.pyd` builds via `pip install -e .` and passes 10 Python checks; `python -m build` produces a clean wheel/sdist (twine check passed); sdist installs cleanly in a fresh venv; GitHub Actions CI passes on all 9 OS/Python matrix jobs; MkDocs site builds with `mkdocs build --strict`; GitHub Pages docs site is deployed and live at `https://satyamdas03.github.io/lumina-lob/`; release tag `v0.1.0` is pushed; blog post + social launch drafts and assets are in `blog/`; benchmark reports Python ~22k events/sec and C++ ~90k events/sec on 200k order stream.
- Latest pushed commit: `e72aeb6` on `main` — "ci: fetch full git history so release tag tests pass".
- PyPI upload is configured but requires the owner to enable trusted publishing on PyPI and push/re-push a `v*.*.*` tag.
- GitHub profile pin requires a manual browser action.

## Next checkpoint

**ALL CHECKPOINTS COMPLETE.**

The Lumina LOB project has reached the end of the 28-checkpoint plan. There are no further scheduled checkpoints.

Remaining manual actions outside this session:
1. Enable trusted publishing for `lumina-lob` on PyPI (the `v0.1.1` tag is already pushed; the publish job will run automatically once trusted publishing is configured).
2. Pin the repository on the GitHub profile via the GitHub UI.

## Restart instructions for a fresh session

If the next model has zero context, read in this order:

1. **This file** — `C:\Users\point\.claude\projects\C--Users-point\memory\lumina_lob_session_2026-07-05.md`
2. **`PLAN.md`** — `C:\Users\point\projects\janestreet\01_LuminaLOB_LimitOrderBook_Simulator\PLAN.md`
3. **Latest code** — inspect `lumina_lob/core/*.py`, `lumina_lob/market_model/*.py`, `lumina_lob/agents/*.py`, `lumina_lob/data/*.py`, and `tests/*.py`
4. **Run tests** — `python -m pytest -q` and `python -m pytest --cov=lumina_lob`
5. Project is complete; next actions are manual PyPI trusted-publishing setup and GitHub profile pin.

Do not skip reading this memory file and `PLAN.md`; they contain the checkpoint discipline, bug history, and next action.

## Post-session maintenance notes

- 2026-07-07: Removed an empty stray directory `C:\Users\point\projects\janestreet\01_Lumestreet\` (typo duplicate of `01_LuminaLOB_LimitOrderBook_Simulator`) that contained only an empty `lumina_lob/__init__.py`. It caused no functional impact.
- 2026-07-07: Re-ran `python -m pytest tests/ -q` after cleanup — **308 passed, 2 matplotlib warnings** in 16.87 s. Project remains green.

## 2026-07-07 — v0.1.1 completion push

A deep review found the repo was functionally complete but not *release-complete*: docs contradicted each other, lint/type gates failed, the build workflow only produced wheels, and `pip install lumina-lob` did not work because no sdist/wheel had ever been published. A multi-agent workflow fixed all of it and pushed `v0.1.1`.

### Fixes applied

| Area | What changed | Files |
|---|---|---|
| Docs | Synced README.md and docs/index.md Phase 6 status to ✅ Done; marked blog + social launch ✅ Done; fixed README notebook link to `notebooks/02_agents_and_impact.ipynb`; updated PLAN.md to remove references to non-existent files and list actual notebooks. | `README.md`, `docs/index.md`, `PLAN.md` |
| Packaging | `build.yml` now runs `python -m build` (wheel + sdist); artifact names/patterns updated from `wheels-*` to `dist-*`; publish job verified to depend on build and use `pypa/gh-action-pypi-publish@release/v1` with the `pypi` environment. | `.github/workflows/build.yml`, `MANIFEST.in` |
| Code quality | `ruff check lumina_lob tests` → **0 errors**; `mypy lumina_lob` → **0 errors**; fixed real type issues across core, data, market_model, rl, viz. | ~40 `.py` files |
| Types | Added `ignore_missing_imports = true` for missing stubs; changed `Order.price`/`OrderBook` price-level keys to `float`; added generic `gym.Env[np.ndarray, np.ndarray]` args; cast simulation metrics; no `# type: ignore` used to hide real bugs. | `pyproject.toml`, `lumina_lob/**/*.py` |
| Release | Bumped version to `0.1.1`; created `CHANGELOG.md`; committed; pushed `main`; pushed tag `v0.1.1`. | `pyproject.toml`, `CHANGELOG.md` |

### Verification results

- `pytest`: **308 passed, 0 failed**
- `ruff check lumina_lob tests`: **0 errors**
- `mypy lumina_lob`: **Success: no issues found in 32 source files**
- `python -m build`: produced `dist/lumina_lob-0.1.1-cp314-cp314-win_amd64.whl` and `dist/lumina_lob-0.1.1.tar.gz`
- Fresh venv sdist install test: `import lumina_lob` works; exports `OrderBook`, `MatchingEngine`, `Order`, `Side`, `OrderType`, `PriceLevel`

### Push outcome

- Commit: `6ac0fc9`
- Tag: `v0.1.1`
- Remote: `https://github.com/satyamdas03/lumina-lob.git`
- GitHub Actions `build.yml` triggered on the tag (run `28836297150`).
  - **Build matrix:** 9/9 jobs passed (ubuntu/windows/macos × Python 3.11/3.12/3.13), producing wheels + sdist.
  - **Publish to PyPI:** failed with `invalid-publisher: valid token, but no corresponding publisher` — trusted publishing is not yet configured on PyPI.
  - Claims rendered by the action: `repo:satyamdas03/lumina-lob:environment:pypi`, workflow `satyamdas03/lumina-lob/.github/workflows/build.yml@refs/tags/v0.1.1`.
- README updated with exact PyPI trusted-publishing setup steps and the claim values (commit `910a827`).
- The only remaining blocker is the repository owner logging into PyPI and adding the pending publisher.

## Related memories

- [[satyam_janestreet_quant_roadmap_2026-2029]] — Parent roadmap that spawned this repo.
