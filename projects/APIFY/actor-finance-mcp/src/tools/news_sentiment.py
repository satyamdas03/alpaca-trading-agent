"""News sentiment tool — financial news with basic sentiment scoring."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)

# Simple keyword-based sentiment (no ML dependency)
POSITIVE_WORDS = frozenset({
    "surge", "soar", "rally", "beat", "exceed", "upgrade", "bullish", "growth",
    "profit", "gain", "record", "strong", "positive", "outperform", "raise",
    "buy", "opportunity", "breakthrough", "innovation", "dividend", "expansion",
    "recovery", "boom", "upside", "confident", "optimistic", "milestone",
})

NEGATIVE_WORDS = frozenset({
    "crash", "plunge", "drop", "miss", "downgrade", "bearish", "decline",
    "loss", "cut", "warning", "risk", "fear", "concern", "weak", "negative",
    "underperform", "lower", "sell", "layoff", "debt", "default", "recession",
    "inflation", "crisis", "collapse", "downturn", "slump", "tariff", "lawsuit",
})


def fetch_news_sentiment(tickers: list[str], query: str = "", limit: int = 20) -> list[dict[str, Any]]:
    """Fetch financial news with sentiment scoring for given tickers."""
    tickers = tickers[:limit]
    now = datetime.now(timezone.utc).isoformat()
    results = []

    for ticker in tickers:
        try:
            news_items = _get_news(ticker, limit)

            # Add sentiment scoring
            for item in news_items:
                title = item.get("title", "")
                sentiment = _score_sentiment(title)
                item["sentiment"] = sentiment["label"]
                item["sentiment_score"] = sentiment["score"]
                item["sentiment_confidence"] = sentiment["confidence"]

            avg_sentiment = _avg_sentiment(news_items)

            results.append({
                "tool": "news_sentiment",
                "ticker": ticker,
                "data": {
                    "news_count": len(news_items),
                    "average_sentiment": avg_sentiment,
                    "articles": news_items,
                },
                "source": "yfinance",
                "fetched_at": now,
                "cache_ttl": 600,
            })
        except Exception as e:
            logger.warning(f"News sentiment failed for {ticker}: {e}")
            results.append({
                "tool": "news_sentiment",
                "ticker": ticker,
                "data": {"error": f"News unavailable for {ticker}: {str(e)}"},
                "source": "error",
                "fetched_at": now,
                "cache_ttl": 300,
            })

    return results


def _get_news(ticker: str, limit: int) -> list[dict[str, Any]]:
    """Fetch news from yfinance."""
    try:
        t = yf.Ticker(ticker)
        raw_news = t.news

        if not raw_news:
            return []

        articles = []
        for item in raw_news[:limit]:
            article = {
                "title": item.get("title", ""),
                "publisher": item.get("publisher", ""),
                "link": item.get("link", ""),
                "published": item.get("providerPublishTime", ""),
                "type": item.get("type", ""),
            }

            # Try to extract summary
            if "summary" in item:
                article["summary"] = item["summary"][:500]
            elif "title" in item:
                article["summary"] = ""

            # Related tickers
            if "relatedTickers" in item:
                article["related_tickers"] = item["relatedTickers"]

            articles.append(article)

        return articles

    except Exception as e:
        logger.warning(f"yfinance news fetch failed for {ticker}: {e}")
        return []


def _score_sentiment(text: str) -> dict[str, Any]:
    """Simple keyword-based sentiment scoring."""
    if not text:
        return {"label": "neutral", "score": 0.0, "confidence": "low"}

    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    pos_hits = len(words & POSITIVE_WORDS)
    neg_hits = len(words & NEGATIVE_WORDS)
    total_hits = pos_hits + neg_hits

    if total_hits == 0:
        return {"label": "neutral", "score": 0.0, "confidence": "low"}

    score = (pos_hits - neg_hits) / total_hits  # -1 to 1

    if score > 0.2:
        label = "positive"
    elif score < -0.2:
        label = "negative"
    else:
        label = "neutral"

    confidence = "medium" if total_hits >= 2 else "low"

    return {"label": label, "score": round(score, 2), "confidence": confidence}


def _avg_sentiment(articles: list[dict]) -> dict[str, Any]:
    """Calculate average sentiment across articles."""
    if not articles:
        return {"label": "neutral", "score": 0.0, "count": 0}

    scores = [a.get("sentiment_score", 0) for a in articles]
    avg = sum(scores) / len(scores) if scores else 0

    if avg > 0.1:
        label = "positive"
    elif avg < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {"label": label, "score": round(avg, 2), "count": len(articles)}