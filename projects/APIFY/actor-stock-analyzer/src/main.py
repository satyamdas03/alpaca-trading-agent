"""NeuralQuant Stock Analyzer — Apify Actor entry point."""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone

import pandas as pd
from apify import Actor

from .validators import validate_input, ValidationError
from .data_fetcher import build_fundamentals_row, fetch_macro, estimate_claude_cost
from .signal_engine import compute_composite_scores, recommendation_from_score, MacroSnapshot
from .debate_engine import run_debate, build_macro_context

log = logging.getLogger(__name__)

_BATCH_SIZE = 5
_BATCH_DELAY_S = 2.0


def detect_market(ticker: str) -> str:
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        return "IN"
    return "US"


def build_output_row(
    signal_row,
    fund: dict,
    market: str,
    macro: MacroSnapshot,
    debate,
) -> dict:
    """Build clean output dict. No private keys (_*) pass through."""
    out: dict = {
        "ticker": str(signal_row["ticker"]),
        "market": market,
        "company_name": fund.get("long_name") or str(signal_row["ticker"]),
        "current_price": fund.get("current_price"),
        "ai_score": int(signal_row["score_1_10"]),
        "composite_score_raw": round(float(signal_row["composite_score"]), 4),
        "recommendation": recommendation_from_score(int(signal_row["score_1_10"])),
        "score_components": {
            "quality":       round(float(signal_row.get("quality_percentile", 0.5)), 3),
            "momentum":      round(float(signal_row.get("momentum_percentile", 0.5)), 3),
            "value":         round(float(signal_row.get("value_percentile", 0.5)), 3),
            "low_vol":       round(float(signal_row.get("low_vol_percentile", 0.5)), 3),
            "short_interest":round(float(signal_row.get("short_interest_percentile", 0.5)), 3),
        },
        "macro_regime": {
            "vix": round(macro.vix, 2),
            "fred_sourced": macro.fred_sourced,
        },
        "data_source": "live" if fund.get("_is_real") else "synthetic_fallback",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    if debate is not None:
        out["debate_verdict"] = debate.verdict
        out["investment_thesis"] = debate.investment_thesis
        out["bull_case"] = debate.bull_case
        out["bear_case"] = debate.bear_case
        out["risk_factors"] = debate.risk_factors
        out["consensus_score"] = debate.consensus_score
        out["agent_outputs"] = [
            {"agent": a.agent, "stance": a.stance, "conviction": a.conviction,
             "thesis": a.thesis, "key_points": a.key_points}
            for a in debate.agent_outputs
        ]
    return out


async def main() -> None:
    async with Actor:
        raw_input = await Actor.get_input() or {}
        try:
            actor_input = validate_input(raw_input)
        except ValidationError as exc:
            await Actor.fail(status_message=f"Invalid input: {exc}")
            return

        tickers = actor_input["tickers"]
        mode = actor_input["mode"]
        max_spend_usd = actor_input["max_spend_usd"]

        # Verify API key for full_ai mode
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if mode == "full_ai" and not anthropic_key:
            await Actor.fail(status_message="ANTHROPIC_API_KEY secret not set. Required for full_ai mode.")
            return

        # Cost gate
        if mode == "full_ai":
            estimated = estimate_claude_cost(len(tickers))
            if estimated > max_spend_usd:
                await Actor.fail(
                    status_message=f"Estimated Claude cost ${estimated:.2f} exceeds max_spend_usd ${max_spend_usd:.2f}. "
                                   f"Reduce ticker count or increase max_spend_usd."
                )
                return

        log.info("Fetching macro data...")
        macro = fetch_macro()

        # Fetch fundamentals in batches
        log.info("Fetching fundamentals for %d tickers...", len(tickers))
        fund_map: dict[str, dict] = {}
        for i in range(0, len(tickers), _BATCH_SIZE):
            batch = tickers[i:i + _BATCH_SIZE]
            for ticker in batch:
                market = detect_market(ticker)
                fund_map[ticker] = build_fundamentals_row(ticker, market)
            if i + _BATCH_SIZE < len(tickers):
                await asyncio.sleep(_BATCH_DELAY_S)

        # Build fundamentals DataFrame
        rows = []
        for ticker in tickers:
            market = detect_market(ticker)
            f = fund_map[ticker]
            rows.append({
                "ticker": ticker,
                "gross_profit_margin": f.get("gross_profit_margin", 0.3),
                "accruals_ratio":       f.get("accruals_ratio", 0.0),
                "piotroski":            f.get("piotroski", 4),
                "momentum_raw":         f.get("momentum_raw", 0.0),
                "short_interest_pct":   f.get("short_interest_pct", 0.05),
                "pe_ttm":               f.get("pe_ttm", 25.0),
                "pb_ratio":             f.get("pb_ratio", 3.0),
                "realized_vol_1y":      f.get("realized_vol_1y", 0.25),
            })
        fundamentals_df = pd.DataFrame(rows)
        scored_df = compute_composite_scores(fundamentals_df, macro)

        # Build context for debate (if needed)
        macro_ctx = build_macro_context(macro)

        results = []
        for _, signal_row in scored_df.iterrows():
            ticker = str(signal_row["ticker"])
            market = detect_market(ticker)
            fund = fund_map[ticker]

            debate_result = None
            if mode == "full_ai":
                context = {
                    **macro_ctx,
                    "market": market,
                    "composite_score": round(float(signal_row["composite_score"]), 4),
                    "score_1_10": int(signal_row["score_1_10"]),
                    "quality_percentile": round(float(signal_row.get("quality_percentile", 0.5)), 3),
                    "momentum_percentile": round(float(signal_row.get("momentum_percentile", 0.5)), 3),
                    "short_interest_percentile": round(float(signal_row.get("short_interest_percentile", 0.5)), 3),
                    **{k: v for k, v in fund.items() if not k.startswith("_")},
                }
                try:
                    debate_result = await run_debate(ticker, context, anthropic_key)
                except Exception as exc:
                    log.error("Debate failed for %s: %s", ticker, exc)

            output_row = build_output_row(signal_row, fund, market, macro, debate_result)
            results.append(output_row)

        if results:
            await Actor.push_data(results)
            log.info("Pushed %d results.", len(results))


if __name__ == "__main__":
    asyncio.run(main())