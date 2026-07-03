"""LLM candidate generator: the agent proposes, the statistics dispose.

The model sees the DSL grammar, the feature catalog, and TRAIN-window-only
feedback on past trials (via TrialsLedger.train_feedback).  It never sees
validation- or test-window results, so the held-out data cannot leak back
into generation.  Every proposal — valid or not — is registered in the
trials ledger before anything is evaluated.
"""

import json
import logging
import re
import time

from aqra.generate.ledger import TrialsLedger
from aqra.signals.dsl import (
    BINARY_OPS, DSL_VERSION, MAX_DEPTH, MAX_NODES, MAX_WINDOW, TS_OPS,
    UNARY_OPS, DSLCandidate, features_for_lane, validate,
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are the signal-generation module of AQRA, a quantitative
research agent.  Propose cross-sectional equity trading signals as JSON ASTs
in a constrained DSL.  Every proposal you make is registered in a trials
ledger and pays its share of a Benjamini-Yekutieli multiple-testing
correction, so propose deliberately: each weak idea you emit makes the
statistical bar higher for all of them.

DSL grammar (JSON):
  {{"feature": "<name>"}}                               leaf
  {{"op": "<u>", "arg": AST}}          u in {unary}
  {{"op": "<t>", "arg": AST, "window": W}}   t in {ts}, 1 <= W <= {max_window}
  {{"op": "<b>", "left": AST, "right": AST}}  b in {binary}

Limits: depth <= {max_depth}, nodes <= {max_nodes}.
Available features (lane {lane}): {features}

Semantics: rank/zscore are cross-sectional within a date; ts_* operators look
strictly backward per ticker; higher signal value = long, lower = short in a
dollar-neutral portfolio, {holding} trading-day holding period, 10bps costs
on turnover.

Respond ONLY with a JSON array of exactly {n} objects, each:
  {{"ast": <AST>, "rationale": "<one-sentence economic hypothesis>"}}
"""

FEEDBACK_PREFIX = """Past trials (TRAIN-window stats only — validation results
are withheld by design):
"""


class LLMGenerator:
    """Generates DSL candidates via the Anthropic API (or a mock)."""

    def __init__(self, db, lane: str = "S", client=None,
                 model: str = DEFAULT_MODEL, holding_period: int = 21,
                 max_retries: int = 3):
        self.db = db
        self.lane = lane
        self.client = client  # None => mock mode
        self.model = model
        self.holding_period = holding_period
        self.max_retries = max_retries
        self.ledger = TrialsLedger(db)

    # ---------------- prompt construction ----------------

    def _system_prompt(self, n: int) -> str:
        return SYSTEM_PROMPT.format(
            unary=sorted(UNARY_OPS), ts=sorted(TS_OPS), binary=sorted(BINARY_OPS),
            max_window=MAX_WINDOW, max_depth=MAX_DEPTH, max_nodes=MAX_NODES,
            lane=self.lane, features=sorted(features_for_lane(self.lane)),
            holding=self.holding_period, n=n,
        )

    def _user_prompt(self) -> str:
        feedback = self.ledger.train_feedback(self.lane)
        if not feedback:
            return "No past trials yet. Propose your candidates."
        return FEEDBACK_PREFIX + json.dumps(feedback, indent=1)

    # ---------------- LLM call ----------------

    def _call_llm(self, n: int) -> str:
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=self._system_prompt(n),
                    messages=[{"role": "user", "content": self._user_prompt()}],
                )
                return response.content[0].text
            except Exception as e:  # API errors: timeout, 429, 5xx
                last_err = e
                wait = 2 ** attempt
                logger.warning("LLM call failed (attempt %d/%d): %s — backing off %ds",
                               attempt + 1, self.max_retries, e, wait)
                time.sleep(wait)
        raise RuntimeError(f"LLM generation failed after {self.max_retries} attempts") from last_err

    @staticmethod
    def _parse_proposals(text: str) -> list[dict]:
        """Extract the JSON array from the response; [] on garbage."""
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            return []
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []
        return [d for d in data if isinstance(d, dict) and "ast" in d]

    # ---------------- mock mode ----------------

    def _mock_proposals(self, n: int) -> list[dict]:
        """Deterministic template proposals for tests and dry runs."""
        feats = sorted(features_for_lane(self.lane))
        templates = [
            {"ast": {"op": "rank", "arg": {"feature": feats[0]}},
             "rationale": f"mock: rank of {feats[0]}"},
            {"ast": {"op": "sub",
                     "left": {"op": "rank", "arg": {"feature": feats[0]}},
                     "right": {"op": "rank", "arg": {"feature": feats[-1]}}},
             "rationale": f"mock: {feats[0]} minus {feats[-1]} rank spread"},
            {"ast": {"op": "zscore",
                     "arg": {"op": "ts_mean", "arg": {"feature": feats[min(1, len(feats) - 1)]},
                             "window": 21}},
             "rationale": "mock: one-month smoothed zscore"},
            {"ast": {"op": "neg",
                     "arg": {"op": "delta", "arg": {"feature": feats[0]}, "window": 5}},
             "rationale": "mock: one-week reversal of the leading feature"},
        ]
        return templates[:n]

    # ---------------- public API ----------------

    def propose(self, n: int = 4) -> list[DSLCandidate]:
        """Generate, register, and validate n candidates.

        EVERY parsed proposal is registered before validation; invalid ones
        are marked REJECTED_INVALID and still burden the FDR correction.
        Returns only the valid candidates, ready for evaluation.
        """
        if self.client is None:
            raw = self._mock_proposals(n)
        else:
            raw = self._parse_proposals(self._call_llm(n))
            if not raw:
                logger.warning("LLM returned no parseable proposals")
                return []

        features = features_for_lane(self.lane)
        valid: list[DSLCandidate] = []
        for item in raw[:n]:
            cand = DSLCandidate(
                trial_id=self.ledger.new_trial_id(),
                lane=self.lane,
                ast=item.get("ast"),
                rationale=str(item.get("rationale", ""))[:500],
                source="mock" if self.client is None else "llm",
            )
            errors = (["ast missing"] if cand.ast is None
                      else validate(cand.ast, features))
            if errors:
                # Register-then-reject: the failed attempt stays on the books.
                try:
                    self.ledger.register(cand)
                    self.ledger.mark_invalid(cand.trial_id, errors)
                except Exception:
                    logger.exception("failed to ledger invalid candidate")
                logger.warning("rejected invalid candidate: %s", errors)
                continue
            self.ledger.register(cand)
            valid.append(cand)
        return valid
