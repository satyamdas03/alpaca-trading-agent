#!/usr/bin/env python3
"""Convert MCP tool-result JSON files into parquet for backtesting.

Reads the raw JSON from mcp__alpaca__get_stock_bars calls,
concatenates chunks per ticker, deduplicates, and saves as parquet.
"""

import json
import sys
from pathlib import Path

import pandas as pd


def convert(tool_results_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    ticker_frames: dict[str, list[pd.DataFrame]] = {}

    for f in sorted(tool_results_dir.glob("call_*.txt")):
        try:
            with open(f) as fh:
                d = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue

        bars_dict = d.get("bars", {})
        for ticker, bars in bars_dict.items():
            if not bars:
                continue
            df = pd.DataFrame(bars)
            col_map = {"t": "date", "o": "open", "h": "high", "l": "low",
                        "c": "close", "v": "volume"}
            df = df.rename(columns=col_map)
            keep = ["date", "open", "high", "low", "close", "volume"]
            df = df[[c for c in keep if c in df.columns]]
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            ticker_frames.setdefault(ticker, []).append(df)

    for ticker, frames in ticker_frames.items():
        combined = pd.concat(frames, ignore_index=True)
        if "date" in combined.columns:
            combined = combined.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
        else:
            combined = combined.drop_duplicates().reset_index(drop=True)

        out_path = output_dir / f"{ticker}.parquet"
        combined.to_parquet(out_path, index=False)
        print(f"  {ticker}: {len(combined)} bars -> {out_path}")


if __name__ == "__main__":
    results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "C:/Users/point/.claude/projects/C--Users-point-projects-alpacaIntegrationWithClaudeCode/"
        "b2095d23-cd92-4a87-aacd-d3bee37a5861/tool-results/"
    )
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/historical")
    convert(results_dir, out_dir)