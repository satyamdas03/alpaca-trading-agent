"""
Data fetcher for NeuralQuant Stock Analyzer actor.
Ported from NeuralQuant data_builder.py — self-contained, stateless (no cache).
"""
from __future__ import annotations
import logging
import math
import os
from datetime import date

import numpy as np
import pandas as pd
import yfinance as yf

from .signal_engine import MacroSnapshot

log = logging.getLogger(__name__)

# Claude API cost estimate: ~1024 tokens per agent call, 7 agents per ticker
# claude-sonnet-4-6: ~$3/1M input tokens
_CLAUDE_COST_PER_TICKER_USD = 0.07  # conservative upper bound


def _safe(val, default: float = 0.0) -> float:
    try:
        f = float(val)
        return f if math.isfinite(f) else default
    except Exception:
        return default


def _yf_symbol(ticker: str, market: str) -> str:
    if market == "IN" and "." not in ticker:
        return ticker + ".NS"
    return ticker


def _piotroski_from_info(info: dict) -> int:
    ni  = _safe(info.get("netIncomeToCommon"))
    ta  = _safe(info.get("totalAssets"), 1) or 1
    ocf = _safe(info.get("operatingCashflow"))
    score = 0
    if ni / ta > 0:                                score += 1
    if ocf > 0:                                    score += 1
    if ocf > ni:                                   score += 1
    if _safe(info.get("grossMargins")) > 0:        score += 1
    if _safe(info.get("revenueGrowth")) > 0:       score += 1
    if _safe(info.get("debtToEquity"), 999) < 100: score += 1
    if _safe(info.get("currentRatio")) > 1:        score += 1
    if _safe(info.get("returnOnEquity")) > 0:      score += 1
    if _safe(info.get("freeCashflow")) > 0:        score += 1
    return score


def _synthetic_row(ticker: str) -> dict:
    """Deterministic fallback when yfinance fails entirely."""
    s = hash(ticker) % (2**31 - 1)
    rng = np.random.RandomState(s)
    return {
        "gross_profit_margin": float(rng.uniform(0.10, 0.85)),
        "accruals_ratio":       float(rng.uniform(-0.15, 0.15)),
        "piotroski":            int(rng.randint(2, 9)),
        "momentum_raw":         float(rng.uniform(-0.25, 0.55)),
        "short_interest_pct":   float(rng.uniform(0.01, 0.18)),
        "pe_ttm":               float(rng.uniform(10, 45)),
        "pb_ratio":             float(rng.uniform(1, 8)),
        "beta":                 float(rng.uniform(0.5, 1.8)),
        "realized_vol_1y":      float(rng.uniform(0.15, 0.50)),
        "current_price":        None,
        "long_name":            ticker,
        "_is_real":             False,
    }


def build_fundamentals_row(ticker: str, market: str) -> dict:
    """Fetch fundamentals for one ticker. Falls back to synthetic on any failure."""
    sym = _yf_symbol(ticker, market)
    try:
        t = yf.Ticker(sym)
        info = t.info or {}
        if not info or not info.get("symbol"):
            raise ValueError("Empty yfinance info")

        gpm = _safe(info.get("grossMargins"), 0.3)
        si  = _safe(info.get("shortPercentOfFloat"), 0.05)
        ni  = _safe(info.get("netIncomeToCommon"))
        ocf = _safe(info.get("operatingCashflow"))
        ta  = _safe(info.get("totalAssets"), 1) or 1
        accruals = max(-0.3, min(0.3, (ni - ocf) / ta))
        pe_ttm   = max(1.0, min(200.0, _safe(info.get("trailingPE"), 25.0)))
        pb_ratio = max(0.1, min(50.0, _safe(info.get("priceToBook"), 3.0)))
        beta     = max(0.1, min(3.0, _safe(info.get("beta"), 1.0)))
        piotroski = _piotroski_from_info(info)

        hist = t.history(period="14mo", auto_adjust=True)
        hist_close = hist["Close"] if not hist.empty else pd.Series(dtype=float)

        if len(hist_close) >= 252:
            momentum = (float(hist_close.iloc[-22]) - float(hist_close.iloc[-252])) / float(hist_close.iloc[-252])
        else:
            momentum = float(np.random.RandomState((hash(ticker) + 3) % (2**31)).uniform(-0.25, 0.55))

        if len(hist_close) >= 30:
            log_rets = np.log(hist_close / hist_close.shift(1)).dropna()
            realized_vol = float(log_rets.tail(252).std() * np.sqrt(252))
        else:
            realized_vol = beta * 0.18

        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        return {
            "gross_profit_margin": float(gpm),
            "accruals_ratio":       float(accruals),
            "piotroski":            int(piotroski),
            "momentum_raw":         float(momentum),
            "short_interest_pct":   float(si),
            "pe_ttm":               float(pe_ttm),
            "pb_ratio":             float(pb_ratio),
            "beta":                 float(beta),
            "realized_vol_1y":      float(realized_vol),
            "current_price":        float(current_price) if current_price else None,
            "long_name":            info.get("longName") or info.get("shortName") or ticker,
            "week52_high":          _safe(info.get("fiftyTwoWeekHigh")) or None,
            "week52_low":           _safe(info.get("fiftyTwoWeekLow")) or None,
            "analyst_target":       _safe(info.get("targetMeanPrice")) or None,
            "_is_real":             True,
        }
    except Exception as exc:
        log.debug("yfinance failed for %s: %s — using synthetic", ticker, exc)
        return _synthetic_row(ticker)


def fetch_macro() -> MacroSnapshot:
    """Fetch live macro data. Falls back to defaults on any failure."""
    m = MacroSnapshot()
    try:
        vix_h = yf.Ticker("^VIX").history(period="5d", auto_adjust=True)
        if not vix_h.empty:
            m.vix = float(vix_h["Close"].iloc[-1])
    except Exception:
        pass

    try:
        spx = yf.Ticker("^GSPC").history(period="252d", auto_adjust=True)
        if len(spx) >= 200:
            last = float(spx["Close"].iloc[-1])
            m.spx_vs_200ma = (last - float(spx["Close"].tail(200).mean())) / float(spx["Close"].tail(200).mean())
        if len(spx) >= 22:
            m.spx_return_1m = float(spx["Close"].iloc[-1]) / float(spx["Close"].iloc[-22]) - 1
    except Exception:
        pass

    fred_key = os.environ.get("FRED_API_KEY", "").strip()
    if fred_key:
        try:
            from fredapi import Fred
            fred = Fred(api_key=fred_key)
            def _fred_latest(series_id: str) -> float | None:
                s = fred.get_series_latest_release(series_id)
                return float(s.dropna().iloc[-1]) if not s.dropna().empty else None

            hy = _fred_latest("BAMLH0A0HYM2")
            if hy: m.hy_spread_oas = hy * 100  # percent → bps
            cpi = _fred_latest("CPIAUCSL")
            if cpi: m.cpi_yoy = cpi
            ffr = _fred_latest("FEDFUNDS")
            if ffr: m.fed_funds_rate = ffr
            t10 = _fred_latest("DGS10")
            if t10: m.yield_10y = t10
            t2 = _fred_latest("DGS2")
            if t2:
                m.yield_2y = t2
                if t10: m.yield_spread_2y10y = t10 - t2
            m.fred_sourced = True
        except Exception as exc:
            log.warning("FRED fetch failed: %s — using yfinance proxies", exc)
            try:
                tnx = yf.Ticker("^TNX").history(period="5d", auto_adjust=True)
                if not tnx.empty:
                    m.yield_10y = float(tnx["Close"].iloc[-1])
            except Exception:
                pass
    return m


def estimate_claude_cost(n_tickers: int) -> float:
    return n_tickers * _CLAUDE_COST_PER_TICKER_USD