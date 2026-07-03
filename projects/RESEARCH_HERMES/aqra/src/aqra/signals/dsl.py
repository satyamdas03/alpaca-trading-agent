"""Constrained signal DSL: whitelisted-primitive JSON AST over PIT features.

The generation layer (ICAIF spec Amendment A1) may only express signals in
this grammar, so lookahead is impossible by construction: leaves are
point-in-time features, time-series operators reach strictly backward, and
cross-sectional operators act within a single date.

AST node forms:
    {"feature": "<name>"}                              leaf
    {"op": "<unary>", "arg": AST}                      rank|zscore|neg|abs|sign
    {"op": "<ts>", "arg": AST, "window": int}          ts_mean|ts_std|delta|lag
    {"op": "<binary>", "left": AST, "right": AST}      add|sub|mul|div|min|max

Limits: depth <= MAX_DEPTH, nodes <= MAX_NODES, window in [1, 252].
"""

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd

DSL_VERSION = "1.0"

LANE_S_FEATURES = frozenset({
    "mom_12_1", "pe_rank", "pb_rank", "quality_score",
    "low_vol_score", "insider_score",
})
LANE_I_FEATURES = frozenset({
    "overnight_gap", "volume_zscore", "news_sentiment_zscore",
    "earnings_surprise", "insider_event_score",
})

UNARY_OPS = frozenset({"rank", "zscore", "neg", "abs", "sign"})
TS_OPS = frozenset({"ts_mean", "ts_std", "delta", "lag"})
BINARY_OPS = frozenset({"add", "sub", "mul", "div", "min", "max"})

MAX_DEPTH = 6
MAX_NODES = 25
MAX_WINDOW = 252


def _walk(node, depth=1):
    """Yield (node, depth) for every node; raises on non-dict nodes."""
    yield node, depth
    if not isinstance(node, dict):
        return
    if "arg" in node:
        yield from _walk(node["arg"], depth + 1)
    if "left" in node:
        yield from _walk(node["left"], depth + 1)
    if "right" in node:
        yield from _walk(node["right"], depth + 1)


def validate(ast, features: frozenset) -> list[str]:
    """Return a list of grammar violations; empty list means valid."""
    errors: list[str] = []
    try:
        nodes = list(_walk(ast))
    except (TypeError, RecursionError):
        return ["ast is not a finite dict tree"]
    if len(nodes) > MAX_NODES:
        errors.append(f"too many nodes ({len(nodes)} > {MAX_NODES})")
    for node, depth in nodes:
        if depth > MAX_DEPTH:
            errors.append(f"depth {depth} exceeds {MAX_DEPTH}")
            break
    for node, _ in nodes:
        if not isinstance(node, dict):
            errors.append(f"node {node!r} is not an object")
            continue
        if "feature" in node:
            if node["feature"] not in features:
                errors.append(f"feature {node['feature']!r} not whitelisted")
            extra = set(node) - {"feature"}
            if extra:
                errors.append(f"leaf has extra keys {sorted(extra)}")
        elif "op" in node:
            op = node["op"]
            if op in UNARY_OPS:
                if set(node) != {"op", "arg"}:
                    errors.append(f"{op} needs exactly keys op,arg")
            elif op in TS_OPS:
                if set(node) != {"op", "arg", "window"}:
                    errors.append(f"{op} needs exactly keys op,arg,window")
                else:
                    w = node["window"]
                    if not isinstance(w, int) or not (1 <= w <= MAX_WINDOW):
                        errors.append(f"{op} window {w!r} outside [1,{MAX_WINDOW}]")
            elif op in BINARY_OPS:
                if set(node) != {"op", "left", "right"}:
                    errors.append(f"{op} needs exactly keys op,left,right")
            else:
                errors.append(f"op {op!r} not whitelisted")
        else:
            errors.append(f"node with keys {sorted(node)} is neither leaf nor op")
    return errors


def formula(ast) -> str:
    """Human-readable rendering of the AST."""
    if "feature" in ast:
        return ast["feature"]
    op = ast["op"]
    if op in UNARY_OPS:
        return f"{op}({formula(ast['arg'])})"
    if op in TS_OPS:
        return f"{op}({formula(ast['arg'])}, {ast['window']})"
    return f"{op}({formula(ast['left'])}, {formula(ast['right'])})"


def _eval_panel(node, panels: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Evaluate AST on date x ticker panels.

    Cross-sectional ops act along axis=1 (within a date); time-series ops
    act along axis=0 per ticker and reach strictly backward (rolling/shift),
    which preserves the PIT property of the leaves.
    """
    if "feature" in node:
        return panels[node["feature"]]
    op = node["op"]
    if op in UNARY_OPS:
        x = _eval_panel(node["arg"], panels)
        if op == "rank":
            return x.rank(axis=1, pct=True)
        if op == "zscore":
            mu = x.mean(axis=1)
            sd = x.std(axis=1).replace(0, np.nan)
            return x.sub(mu, axis=0).div(sd, axis=0)
        if op == "neg":
            return -x
        if op == "abs":
            return x.abs()
        return np.sign(x)
    if op in TS_OPS:
        x = _eval_panel(node["arg"], panels)
        w = node["window"]
        if op == "ts_mean":
            return x.rolling(w, min_periods=w).mean()
        if op == "ts_std":
            return x.rolling(w, min_periods=w).std()
        if op == "delta":
            return x.diff(w)
        return x.shift(w)
    left = _eval_panel(node["left"], panels)
    right = _eval_panel(node["right"], panels)
    left, right = left.align(right, join="outer")
    if op == "add":
        return left + right
    if op == "sub":
        return left - right
    if op == "mul":
        return left * right
    if op == "div":
        return left / right.replace(0, np.nan)
    if op == "min":
        return np.minimum(left, right)
    return np.maximum(left, right)


def evaluate(ast, df: pd.DataFrame, features: frozenset) -> pd.Series:
    """Evaluate a validated AST on a long frame (ticker, date, features...).

    Returns the signal as a Series aligned to df's index.  Raises ValueError
    on an invalid AST — callers must validate first and treat this as a bug.
    """
    errors = validate(ast, features)
    if errors:
        raise ValueError(f"invalid DSL ast: {errors}")
    used = sorted({n["feature"] for n, _ in _walk(ast) if "feature" in n})
    panels = {
        f: df.pivot_table(index="date", columns="ticker", values=f)
        for f in used
    }
    out = _eval_panel(ast, panels)
    long = out.stack(future_stack=True).rename("signal").reset_index()
    long.columns = ["date", "ticker", "signal"]
    merged = df[["ticker", "date"]].merge(long, on=["ticker", "date"], how="left")
    return pd.Series(merged["signal"].to_numpy(), index=df.index)


@dataclass
class DSLCandidate:
    """A generated signal candidate expressed in the DSL."""
    trial_id: str
    lane: str  # "S" or "I"
    ast: dict
    rationale: str
    source: str = "llm"
    dsl_version: str = DSL_VERSION

    @property
    def formula(self) -> str:
        return formula(self.ast)

    def to_json(self) -> str:
        return json.dumps({
            "trial_id": self.trial_id, "lane": self.lane, "ast": self.ast,
            "rationale": self.rationale, "source": self.source,
            "dsl_version": self.dsl_version,
        })

    @classmethod
    def from_json(cls, s: str) -> "DSLCandidate":
        return cls(**json.loads(s))


def features_for_lane(lane: str) -> frozenset:
    return LANE_S_FEATURES if lane == "S" else LANE_I_FEATURES
