# Apify Monetization — Design Spec
**Date:** 2026-04-16  
**Status:** Approved  
**Goal:** Publish 3 monetized Apify Actors today (Actor B) and this week (Actors A1, A2), leveraging existing NeuralQuant codebase and jlcsearch API.

---

## Overview

Three actors published to Apify Store under Pay Per Event (PPE) pricing:

| Actor | Nickname | Source | Publish target | Expected monthly |
|---|---|---|---|---|
| JLCPCB Parts Finder | Actor B | jlcsearch JSON API | Today | $100–300 |
| NeuralQuant Stock Analyzer | Actor A1 | NeuralQuant core engine | Day 2–3 | $500–2,000 |
| India Market Screener | Actor A2 | NeuralQuant score_builder | Day 3–4 | $200–800 |

Revenue share: **80% to developer**, 20% to Apify. Payouts via PayPal ($20 min) or wire ($100 min), days 15–22 monthly.

---

## Repository Structure

```
C:/Users/point/projects/APIFY/
├── docs/superpowers/specs/          ← this file
├── actor-jlcpcb-parts-finder/
│   ├── .actor/
│   │   └── actor.json               ← Apify metadata, input schema
│   ├── src/
│   │   ├── main.py                  ← entry point
│   │   └── validators.py            ← input sanitization
│   └── requirements.txt
├── actor-stock-analyzer/
│   ├── .actor/
│   │   └── actor.json
│   ├── src/
│   │   ├── main.py                  ← entry point + orchestration
│   │   ├── data_fetcher.py          ← yfinance + FRED (ported from NeuralQuant)
│   │   ├── score_builder.py         ← 5-factor signal engine (ported)
│   │   ├── debate_engine.py         ← 7-agent PARA-DEBATE (ported, optional)
│   │   └── validators.py
│   └── requirements.txt
└── actor-india-market-screener/
    ├── .actor/
    │   └── actor.json
    ├── src/
    │   ├── main.py
    │   ├── data_fetcher.py          ← shared logic with A1
    │   ├── score_builder.py
    │   └── validators.py
    └── requirements.txt
```

Each actor is **fully self-contained** — no dependency on NeuralQuant being deployed or running anywhere.

---

## Actor B — JLCPCB Parts Finder

### Purpose
Search JLCPCB's in-stock electronics components (resistors, capacitors, inductors, MOSFETs, ICs, LEDs) by electrical specs. Returns matching parts with stock counts and pricing. Targets electronics engineers, PCB designers, and makers automating BOM generation.

### Input Schema
```json
{
  "component_type": {
    "type": "string",
    "enum": ["resistor", "capacitor", "inductor", "led", "mosfet", "ic"],
    "description": "Type of electronic component to search"
  },
  "filters": {
    "type": "object",
    "description": "Spec filters (e.g. resistance, package, tolerance). Keys vary by component_type.",
    "properties": {
      "resistance": { "type": "string", "example": "1k" },
      "capacitance": { "type": "string", "example": "100n" },
      "package": { "type": "string", "example": "0402" },
      "tolerance": { "type": "string", "example": "1%" },
      "voltage": { "type": "string", "example": "50V" }
    }
  },
  "max_results": {
    "type": "integer",
    "default": 50,
    "minimum": 1,
    "maximum": 500
  }
}
```

### Data Flow
1. Validate `component_type` against strict enum allowlist
2. Validate each filter key/value against type-specific allowlists (no arbitrary strings reach the URL)
3. Construct URL: `https://jlcsearch.tscircuit.com/{component_type}/list.json?{validated_filters}`
4. Fetch with 10s timeout, exponential backoff, max 3 retries
5. Parse JSON response
6. Push each part as a dataset item

### Output Schema (per item)
```json
{
  "lcsc": 21190,
  "mfr": "0603WAF1001T5E",
  "package": "0603",
  "resistance_ohms": 1000,
  "tolerance_fraction": 0.01,
  "power_watts": 0.1,
  "stock": 31485061,
  "price_per_unit_usd": 0.000814
}
```

### Pricing (PPE)
- **$0.001 per result** returned
- 500 results = $0.50 to user → $0.40 to developer
- No run start fee (low friction for first-time users)

### Error Handling
- Unknown `component_type`: fail fast with clear message before any network call
- jlcsearch API down: retry 3× with backoff, then fail with descriptive error
- Empty results: succeed with empty dataset + info log (not an error)
- Network timeout: caught, logged without leaking internal URLs

---

## Actor A1 — NeuralQuant Stock Analyzer

### Purpose
Input one or more stock tickers; receive institutional-grade quantitative analysis. Two modes: `quant` (5-factor signal engine, no AI costs) and `full_ai` (quant + 7-agent PARA-DEBATE using Claude). Covers US (NYSE/NASDAQ) and India (NSE) markets. No comparable India-focused stock analysis actor exists on Apify Store.

### Input Schema
```json
{
  "tickers": {
    "type": "array",
    "items": { "type": "string" },
    "minItems": 1,
    "maxItems": 50,
    "description": "Stock ticker symbols. Use .NS suffix for NSE India (e.g. RELIANCE.NS, TCS.NS). US tickers need no suffix (e.g. NVDA, AAPL)."
  },
  "mode": {
    "type": "string",
    "enum": ["quant", "full_ai"],
    "default": "quant",
    "description": "quant = 5-factor signal engine only (fast, cheap). full_ai = quant + 7-agent AI debate (premium, uses Claude API)."
  },
  "max_spend_usd": {
    "type": "number",
    "default": 2.0,
    "description": "Safety cap on Claude API spend per run. Run aborts before exceeding this. Only relevant for full_ai mode."
  }
}
```

### Two-Mode Architecture

| | `quant` mode | `full_ai` mode |
|---|---|---|
| Claude calls | 0 | 7 per ticker |
| Cost to developer | ~$0.001/ticker | ~$0.04–0.07/ticker |
| PPE price | $0.05/ticker | $0.25/ticker |
| Net to developer | ~$0.039/ticker | ~$0.15/ticker |
| Latency | ~2s/ticker | ~15–25s/ticker |

### Data Flow
1. Validate all tickers: regex `^[A-Z0-9.]{1,20}$`, strip whitespace, deduplicate
2. Fetch FRED macro data once per run (HY spread, CPI, Fed Funds, 2Y/10Y yields) — cached across tickers
3. For each ticker (batched, 2s delay between batches of 5):
   a. Fetch yfinance data: price, OHLCV, fundamentals, short interest
   b. Compute 5-factor score via `score_builder`: Quality (Piotroski), Momentum (12-1M), Value (P/E + P/B), Low-Vol (realized vol), Short Interest
   c. If `full_ai`: launch 7 parallel Claude calls (MACRO, FUNDAMENTAL, TECHNICAL, SENTIMENT, GEOPOLITICAL, ADVERSARIAL, HEAD ANALYST) via `asyncio.gather`; abort if estimated spend would exceed `max_spend_usd`
4. Push result per ticker to Apify dataset

### Output Schema (per ticker)
```json
{
  "ticker": "RELIANCE.NS",
  "market": "India",
  "price": 1423.50,
  "ai_score": 8.2,
  "score_components": {
    "quality": 0.82,
    "momentum": 0.71,
    "value": 0.65,
    "low_volatility": 0.74,
    "short_interest": 0.91
  },
  "regime": "bull",
  "recommendation": "BUY",
  "debate_summary": "...",   // only in full_ai mode
  "agent_verdicts": {        // only in full_ai mode
    "macro": "BULLISH",
    "fundamental": "BULLISH",
    "technical": "NEUTRAL",
    "sentiment": "BULLISH",
    "geopolitical": "NEUTRAL",
    "adversarial": "BEARISH",
    "head_analyst": "BUY with conviction 7/10"
  },
  "fetched_at": "2026-04-16T10:30:00Z"
}
```

### Secrets Required (stored in Apify Actor secrets — never in code)
- `ANTHROPIC_API_KEY` — required for `full_ai` mode only
- `FRED_API_KEY` — required for macro data (free key from fred.stlouisfed.org)

### Security Controls
- Tickers validated with regex before passing to yfinance — no format string injection
- `ANTHROPIC_API_KEY` and `FRED_API_KEY` sourced from `os.environ` (set via Apify secrets UI), never logged or included in output
- Claude responses stripped of any metadata before writing to dataset
- `max_spend_usd` guard: estimated cost checked before each batch of Claude calls; hard abort if threshold would be exceeded
- Per-ticker errors caught individually — one bad ticker doesn't abort the run
- No user-supplied URLs, webhooks, or file paths accepted

---

## Actor A2 — India Market Screener

### Purpose
Screen the full NeuralQuant universe (50 NSE + 50 US stocks) by quantitative criteria. Returns ranked list. No Claude calls — pure quant signal engine. Fast and cheap. Targets Indian retail investors and quant researchers wanting a daily watchlist.

### Input Schema
```json
{
  "market": {
    "type": "string",
    "enum": ["India", "US", "both"],
    "default": "India"
  },
  "min_score": {
    "type": "number",
    "minimum": 0,
    "maximum": 10,
    "default": 6.0,
    "description": "Minimum AI score (0–10) to include in results"
  },
  "sort_by": {
    "type": "string",
    "enum": ["score", "momentum", "quality", "value"],
    "default": "score"
  },
  "top_n": {
    "type": "integer",
    "minimum": 1,
    "maximum": 100,
    "default": 20
  }
}
```

### Data Flow
1. Validate all inputs against schema
2. Load universe tickers (hardcoded list in source — not user-supplied)
3. Filter by `market`
4. Batch-fetch yfinance + FRED data (rate-limited)
5. Run `score_builder` on each ticker
6. Filter by `min_score`, sort by `sort_by`, take `top_n`
7. Push to dataset

### Pricing (PPE)
- **$1.00 flat per run** (run start event)
- Developer earns $0.80/run
- No per-result fee — screener always returns a bounded dataset

### Security Controls
- Universe ticker list is hardcoded in source, not user-controlled
- `FRED_API_KEY` via Apify secrets
- All input params validated against schema (Pydantic) before use
- yfinance errors per ticker caught and logged without halting run

---

## Cross-Cutting Security Architecture

| Threat | Mitigation |
|---|---|
| API key leakage | All secrets via `os.environ` populated by Apify secrets — never in source, logs, or dataset output |
| Input injection | All user strings validated against allowlists or strict regex before any use |
| Excessive Claude spend | `max_spend_usd` hard cap with pre-flight cost estimate per batch |
| External API abuse | 10s timeouts, exponential backoff (1s, 2s, 4s), max 3 retries on all HTTP calls |
| URL manipulation | No user-supplied URLs accepted in any actor; all URLs constructed from validated components |
| Data leakage | Output written only to Apify dataset — no user-supplied webhooks or external endpoints |
| Dependency vulnerabilities | Pin all dependency versions in `requirements.txt`; minimal dependency footprint |

---

## Monetization Summary

### PPE Pricing
| Actor | Pricing | Expected volume (month 1) | Expected gross |
|---|---|---|---|
| JLCPCB Parts Finder | $0.001/result | 50K results | $50 |
| Stock Analyzer (quant) | $0.05/ticker | 5K tickers | $250 |
| Stock Analyzer (full_ai) | $0.25/ticker | 1K tickers | $250 |
| India Screener | $1.00/run | 200 runs | $200 |
| **Total gross** | | | **~$750** |
| **Developer net (80%)** | | | **~$600** |

Month 3 target (with SEO traction): $2,000–4,000/month net.

### SEO Strategy
- Actor name = exact search phrase (e.g. "India Stock Market Screener", "JLCPCB Parts Search")
- README first paragraph contains primary keyword
- Both Apify Store description fields filled
- Promote on: r/IndianStockMarket, r/webscraping, r/electronics, Product Hunt

### Affiliate Revenue (parallel)
- Enroll in Apify affiliate program: 20–30% recurring commission, $2,500 cap per referral
- Promote via actor READMEs and any content written about the actors

---

## Build Sequence

1. **Actor B** (today, ~3 hrs): JLCPCB Parts Finder — fastest path to first dollar
2. **Actor A1** (day 2–3, ~8 hrs): Stock Analyzer — port score_builder + data_fetcher from NeuralQuant, add debate_engine wrapper
3. **Actor A2** (day 3–4, ~4 hrs): India Market Screener — reuse A1 modules, add universe scan logic
4. **SEO + promotion** (day 4–5): Optimize all READMEs, submit to Product Hunt, post on relevant subreddits
