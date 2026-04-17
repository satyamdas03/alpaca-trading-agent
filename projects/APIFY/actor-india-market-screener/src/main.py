"""India Market Screener — Apify Actor entry point."""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone

import pandas as pd
from apify import Actor

from .validators import validate_input, ValidationError
from .universe import get_universe
from .data_fetcher import build_fundamentals_row, fetch_macro
from .signal_engine import compute_composite_scores, recommendation_from_score

log = logging.getLogger(__name__)

_BATCH_SIZE = 5
_BATCH_DELAY_S = 2.5

_SORT_COLUMN = {
    "score": "score_1_10",
    "momentum": "momentum_percentile",
    "quality": "quality_percentile",
    "value": "value_percentile",
}


def _detect_market_for_ticker(ticker: str) -> str:
    return "IN" if (ticker.endswith(".NS") or ticker.endswith(".BO")) else "US"


async def main() -> None:
    async with Actor:
        raw_input = await Actor.get_input() or {}
        try:
            actor_input = validate_input(raw_input)
        except ValidationError as exc:
            await Actor.fail(status_message=f"Invalid input: {exc}")
            return

        market = actor_input["market"]
        min_score = actor_input["min_score"]
        sort_by = actor_input["sort_by"]
        top_n = actor_input["top_n"]

        tickers = get_universe(market)
        log.info("Screening %d tickers (market=%s)...", len(tickers), market)

        macro = fetch_macro()

        # Fetch fundamentals in batches
        fund_map: dict[str, dict] = {}
        for i in range(0, len(tickers), _BATCH_SIZE):
            batch = tickers[i:i + _BATCH_SIZE]
            for ticker in batch:
                m = _detect_market_for_ticker(ticker)
                fund_map[ticker] = build_fundamentals_row(ticker, m)
            if i + _BATCH_SIZE < len(tickers):
                await asyncio.sleep(_BATCH_DELAY_S)

        rows = []
        for ticker in tickers:
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

        df = compute_composite_scores(pd.DataFrame(rows), macro)

        # Filter and sort
        sort_col = _SORT_COLUMN.get(sort_by, "score_1_10")
        df_filtered = df[df["score_1_10"] >= min_score].sort_values(sort_col, ascending=False).head(top_n)

        results = []
        for _, row in df_filtered.iterrows():
            ticker = str(row["ticker"])
            fund = fund_map[ticker]
            results.append({
                "ticker": ticker,
                "company_name": fund.get("long_name") or ticker,
                "market": _detect_market_for_ticker(ticker),
                "ai_score": int(row["score_1_10"]),
                "recommendation": recommendation_from_score(int(row["score_1_10"])),
                "score_components": {
                    "quality":        round(float(row.get("quality_percentile", 0.5)), 3),
                    "momentum":       round(float(row.get("momentum_percentile", 0.5)), 3),
                    "value":          round(float(row.get("value_percentile", 0.5)), 3),
                    "low_vol":        round(float(row.get("low_vol_percentile", 0.5)), 3),
                    "short_interest": round(float(row.get("short_interest_percentile", 0.5)), 3),
                },
                "current_price": fund.get("current_price"),
                "data_source": "live" if fund.get("_is_real") else "synthetic_fallback",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

        if results:
            await Actor.push_data(results)
            # PPE billing: charge per run
            await Actor.charge(event_name="screen_run", count=1)
        log.info("Screener complete: %d stocks passed min_score=%.0f", len(results), min_score)


if __name__ == "__main__":
    asyncio.run(main())