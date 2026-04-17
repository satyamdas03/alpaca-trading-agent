"""
7-agent PARA-DEBATE engine ported from NeuralQuant.
Uses Anthropic Claude API. API key read from ANTHROPIC_API_KEY env var (Apify secret).
"""
from __future__ import annotations
import asyncio
import logging
import os
import re
from dataclasses import dataclass, field

import anthropic

from .signal_engine import MacroSnapshot

log = logging.getLogger(__name__)
MODEL = "claude-sonnet-4-6-20251101"
MAX_TOKENS = 1024

AGENT_NAMES = ["MACRO", "FUNDAMENTAL", "TECHNICAL", "SENTIMENT", "GEOPOLITICAL", "ADVERSARIAL"]
STANCE_SCORE = {"BULL": 1.0, "NEUTRAL": 0.5, "BEAR": 0.0}
CONVICTION_MULT = {"HIGH": 1.0, "MEDIUM": 0.7, "LOW": 0.4}


@dataclass
class AgentResult:
    agent: str
    stance: str   # BULL | BEAR | NEUTRAL
    conviction: str  # HIGH | MEDIUM | LOW
    thesis: str
    key_points: list[str] = field(default_factory=list)


@dataclass
class DebateResult:
    ticker: str
    verdict: str           # STRONG BUY | BUY | HOLD | SELL | STRONG SELL
    investment_thesis: str
    bull_case: str
    bear_case: str
    risk_factors: list[str]
    agent_outputs: list[AgentResult]
    consensus_score: float


def parse_agent_output(raw: str, agent_name: str) -> AgentResult:
    """Parse structured LLM output. Returns neutral fallback on parse failure."""
    try:
        stance_m = re.search(r"STANCE:\s*(BULL|BEAR|NEUTRAL)", raw, re.I)
        conviction_m = re.search(r"CONVICTION:\s*(HIGH|MEDIUM|LOW)", raw, re.I)
        thesis_m = re.search(r"THESIS:\s*(.+?)(?=KEY_POINTS:|\Z)", raw, re.I | re.S)
        points_m = re.search(r"KEY_POINTS:(.*)", raw, re.I | re.S)

        stance = stance_m.group(1).upper() if stance_m else "NEUTRAL"
        if stance not in ("BULL", "BEAR", "NEUTRAL"):
            stance = "NEUTRAL"
        conviction = conviction_m.group(1).upper() if conviction_m else "LOW"
        thesis = thesis_m.group(1).strip()[:500] if thesis_m else raw[:200]

        key_points: list[str] = []
        if points_m:
            key_points = [
                re.sub(r"^[-*•\d.]\s*", "", p.strip()).strip()
                for p in points_m.group(1).strip().splitlines()
                if p.strip() and p.strip() not in ("-", "*", "•")
            ][:5]

        # Enforce adversarial constraint
        if agent_name == "ADVERSARIAL" and stance == "BULL":
            stance = "BEAR"

        return AgentResult(agent=agent_name, stance=stance, conviction=conviction,
                           thesis=thesis, key_points=key_points)
    except Exception:
        return AgentResult(agent=agent_name, stance="NEUTRAL", conviction="LOW",
                           thesis=f"{agent_name} analysis unavailable.",
                           key_points=["Insufficient data."])


def build_macro_context(macro: MacroSnapshot) -> dict:
    return {
        "vix": round(macro.vix, 2),
        "ism_pmi": round(macro.ism_pmi, 1),
        "hy_spread_oas": round(macro.hy_spread_oas, 0),
        "spx_return_1m": round(macro.spx_return_1m * 100, 2),
        "spx_vs_200ma": round(macro.spx_vs_200ma * 100, 2),
        "yield_spread_2y10y": round(macro.yield_spread_2y10y, 3),
        "yield_10y": round(macro.yield_10y, 2),
        "yield_2y": round(macro.yield_2y, 2),
        "cpi_yoy": round(macro.cpi_yoy, 1),
        "fed_funds_rate": round(macro.fed_funds_rate, 2),
    }


_SYSTEM_PROMPTS = {
    "MACRO": """You are the MACRO analyst on an investment committee. Assess the macroeconomic environment for the given stock.
Use ONLY the exact figures in the user message. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences citing provided data]
KEY_POINTS:
- [cite specific numbers]
- [cite specific numbers]
- [cite specific numbers]""",

    "FUNDAMENTAL": """You are the FUNDAMENTAL analyst. Assess financial quality, valuation, and earnings trajectory.
Use ONLY the exact figures provided. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences citing provided data]
KEY_POINTS:
- [cite specific numbers]
- [cite specific numbers]
- [cite specific numbers]""",

    "TECHNICAL": """You are the TECHNICAL analyst. Assess price momentum, trend strength, and volatility.
Use ONLY the exact figures provided. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences citing provided data]
KEY_POINTS:
- [cite specific numbers]
- [cite specific numbers]
- [cite specific numbers]""",

    "SENTIMENT": """You are the SENTIMENT analyst. Assess short interest, analyst consensus, and market sentiment.
Use ONLY the exact figures provided. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences citing provided data]
KEY_POINTS:
- [cite specific numbers]
- [cite specific numbers]
- [cite specific numbers]""",

    "GEOPOLITICAL": """You are the GEOPOLITICAL analyst. Assess geopolitical, regulatory, and macro risk for the stock's sector and country.
Use ONLY the exact figures provided. Respond strictly:
STANCE: [BULL|BEAR|NEUTRAL]
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences]
KEY_POINTS:
- [key risk 1]
- [key risk 2]
- [key risk 3]""",

    "ADVERSARIAL": """You are the ADVERSARIAL analyst. Your mandate is ALWAYS BEAR — find every reason to be bearish.
You MUST output STANCE: BEAR regardless of the data. Be the devil's advocate.
STANCE: BEAR
CONVICTION: [HIGH|MEDIUM|LOW]
THESIS: [2-3 sentences on downside risks]
KEY_POINTS:
- [bear case point 1]
- [bear case point 2]
- [bear case point 3]""",
}

_HEAD_SYSTEM = """You are the HEAD ANALYST synthesising a PARA-DEBATE investment committee.
VERDICT must be one of: STRONG BUY, BUY, HOLD, SELL, STRONG SELL.
Respond strictly:
VERDICT: [STRONG BUY|BUY|HOLD|SELL|STRONG SELL]
INVESTMENT_THESIS: [4-6 sentences]
BULL_CASE: [2-3 sentences]
BEAR_CASE: [2-3 sentences]
RISK_FACTORS:
- [risk 1]
- [risk 2]
- [risk 3]"""


def _build_user_message(agent: str, ticker: str, context: dict) -> str:
    macro_block = "\n".join(f"- {k}: {v}" for k, v in context.items()
                            if k in ("vix", "ism_pmi", "hy_spread_oas", "yield_10y",
                                     "cpi_yoy", "fed_funds_rate", "spx_return_1m",
                                     "yield_spread_2y10y"))
    fund_block = "\n".join(f"- {k}: {v}" for k, v in context.items()
                           if k in ("piotroski", "gross_profit_margin", "pe_ttm",
                                    "pb_ratio", "accruals_ratio", "quality_percentile",
                                    "composite_score"))
    tech_block = "\n".join(f"- {k}: {v}" for k, v in context.items()
                           if k in ("momentum_percentile", "low_vol_percentile",
                                    "realized_vol_1y", "beta", "score_1_10"))
    sent_block = "\n".join(f"- {k}: {v}" for k, v in context.items()
                           if k in ("short_interest_pct", "short_interest_percentile",
                                    "analyst_target", "current_price"))

    return f"""Analyse {ticker} ({context.get('market', 'US')} market).

MACRO DATA:
{macro_block}

FUNDAMENTAL DATA:
{fund_block}

TECHNICAL DATA:
{tech_block}

SENTIMENT DATA:
{sent_block}

Provide your {agent} stance on {ticker}."""


def _call_agent(client: anthropic.Anthropic, agent_name: str, ticker: str, context: dict) -> AgentResult:
    """Synchronous Claude call for one agent."""
    try:
        msg = _build_user_message(agent_name, ticker, context)
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=_SYSTEM_PROMPTS[agent_name],
            messages=[{"role": "user", "content": msg}],
        )
        return parse_agent_output(response.content[0].text, agent_name)
    except Exception as exc:
        log.warning("%s agent failed for %s: %s", agent_name, ticker, exc)
        return AgentResult(agent=agent_name, stance="NEUTRAL", conviction="LOW",
                           thesis=f"{agent_name} unavailable.", key_points=["Error."])


def _parse_head_synthesis(raw: str) -> dict:
    verdict_m = re.search(r"VERDICT:\s*(STRONG BUY|BUY|HOLD|SELL|STRONG SELL)", raw, re.I)
    verdict = verdict_m.group(1).upper() if verdict_m else "HOLD"

    def _extract(key: str) -> str:
        m = re.search(rf"{key}:\s*(.+?)(?=\n[A-Z_]+:|\Z)", raw, re.I | re.S)
        return m.group(1).strip()[:1000] if m else ""

    risks_m = re.search(r"RISK_FACTORS:(.*)", raw, re.I | re.S)
    risks = []
    if risks_m:
        risks = [re.sub(r"^[-*•\d.]\s*", "", r.strip()).strip()
                 for r in risks_m.group(1).strip().splitlines()
                 if r.strip() and r.strip() not in ("-", "*", "•")][:5]

    return {
        "verdict": verdict,
        "investment_thesis": _extract("INVESTMENT_THESIS"),
        "bull_case": _extract("BULL_CASE"),
        "bear_case": _extract("BEAR_CASE"),
        "risk_factors": risks,
    }


async def run_debate(ticker: str, context: dict, api_key: str) -> DebateResult:
    """Run full 7-agent PARA-DEBATE for one ticker."""
    client = anthropic.Anthropic(api_key=api_key)

    # 5 specialists in parallel
    specialist_results = await asyncio.gather(
        *[asyncio.to_thread(_call_agent, client, name, ticker, context)
          for name in ["MACRO", "FUNDAMENTAL", "TECHNICAL", "SENTIMENT", "GEOPOLITICAL"]],
        return_exceptions=True,
    )
    outputs: list[AgentResult] = []
    for r, name in zip(specialist_results, ["MACRO", "FUNDAMENTAL", "TECHNICAL", "SENTIMENT", "GEOPOLITICAL"]):
        if isinstance(r, AgentResult):
            outputs.append(r)
        else:
            outputs.append(AgentResult(agent=name, stance="NEUTRAL", conviction="LOW",
                                       thesis="Unavailable.", key_points=[]))

    # Adversarial (sequential — needs bull thesis)
    bull_thesis = "; ".join(o.thesis for o in outputs if o.stance == "BULL") or "Mixed signals."
    adv_context = {**context, "bull_thesis": bull_thesis}
    adversarial = await asyncio.to_thread(_call_agent, client, "ADVERSARIAL", ticker, adv_context)
    outputs.append(adversarial)

    # Consensus (specialists only, adversarial excluded)
    consensus = sum(
        STANCE_SCORE[o.stance] * CONVICTION_MULT[o.conviction]
        for o in outputs[:-1]
    ) / len(outputs[:-1])

    # HEAD ANALYST synthesis
    summaries = "\n\n".join(
        f"[{o.agent}] {o.stance} ({o.conviction})\n{o.thesis}\n" +
        "\n".join(f"  - {p}" for p in o.key_points)
        for o in outputs
    )
    head_msg = f"Synthesise the PARA-DEBATE for {ticker} (AI score: {context.get('composite_score', 'N/A')}).\n\nANALYST PANEL:\n{summaries}"
    try:
        head_resp = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS * 2,
            system=_HEAD_SYSTEM,
            messages=[{"role": "user", "content": head_msg}],
        )
        synthesis = _parse_head_synthesis(head_resp.content[0].text)
    except Exception as exc:
        log.error("HEAD_ANALYST failed for %s: %s", ticker, exc)
        synthesis = {"verdict": "HOLD", "investment_thesis": "Analysis unavailable.",
                     "bull_case": "", "bear_case": "", "risk_factors": []}

    return DebateResult(
        ticker=ticker,
        verdict=synthesis["verdict"],
        investment_thesis=synthesis["investment_thesis"],
        bull_case=synthesis["bull_case"],
        bear_case=synthesis["bear_case"],
        risk_factors=synthesis["risk_factors"],
        agent_outputs=outputs,
        consensus_score=round(consensus, 3),
    )