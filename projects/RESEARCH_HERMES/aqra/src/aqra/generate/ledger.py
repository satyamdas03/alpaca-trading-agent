"""Trials ledger: the honest-accounting backbone of the generation loop.

Every candidate is registered BEFORE evaluation, so the multiple-testing
correction (Benjamini-Yekutieli) runs over every trial ever attempted —
including the ones that failed validation or evaluation — never over the
survivors alone.  This is the paper's headline discipline: you cannot
un-try a hypothesis.
"""

import json
import uuid
from datetime import datetime, timezone

from aqra.conformal.multiple_testing import benjamini_yekutieli
from aqra.signals.dsl import DSLCandidate

# Trial lifecycle. Terminal failure states keep p_value NULL and count in the
# denominator of any per-run selection anyway (they were attempts).
STATUS_REGISTERED = "REGISTERED"
STATUS_REJECTED_INVALID = "REJECTED_INVALID"   # failed DSL validation
STATUS_REJECTED_EVAL = "REJECTED_EVAL"          # backtest/eval raised or empty
STATUS_EVALUATED = "EVALUATED"                  # has metrics + p-value


class TrialsLedger:
    """DuckDB-backed append-mostly record of every generation trial."""

    def __init__(self, db):
        self.db = db
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS trials_ledger (
                trial_id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                source TEXT,
                lane TEXT,
                dsl_version TEXT,
                ast_json TEXT,
                formula TEXT,
                rationale TEXT,
                status TEXT,
                p_value DOUBLE,
                sharpe DOUBLE,
                ic DOUBLE,
                metrics_json TEXT,
                train_sharpe DOUBLE,
                train_ic DOUBLE
            )
        """)

    def new_trial_id(self) -> str:
        return uuid.uuid4().hex

    def register(self, cand: DSLCandidate) -> str:
        """Register a candidate before any evaluation. Returns trial_id."""
        try:
            rendered = cand.formula
        except Exception:  # malformed AST still gets ledgered
            rendered = "<unrenderable>"
        self.db.conn.execute(
            """INSERT INTO trials_ledger
               (trial_id, created_at, source, lane, dsl_version, ast_json,
                formula, rationale, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [cand.trial_id, datetime.now(timezone.utc), cand.source, cand.lane,
             cand.dsl_version, json.dumps(cand.ast), rendered,
             cand.rationale, STATUS_REGISTERED],
        )
        return cand.trial_id

    def _require_registered(self, trial_id: str):
        row = self.db.conn.execute(
            "SELECT status FROM trials_ledger WHERE trial_id = ?", [trial_id]
        ).fetchone()
        if row is None:
            raise ValueError(
                f"trial {trial_id} was never registered — evaluation before "
                "registration violates the ledger discipline"
            )

    def mark_invalid(self, trial_id: str, errors: list[str]):
        self._require_registered(trial_id)
        self.db.conn.execute(
            "UPDATE trials_ledger SET status = ?, metrics_json = ? WHERE trial_id = ?",
            [STATUS_REJECTED_INVALID, json.dumps({"errors": errors}), trial_id],
        )

    def mark_eval_failed(self, trial_id: str, reason: str):
        self._require_registered(trial_id)
        self.db.conn.execute(
            "UPDATE trials_ledger SET status = ?, metrics_json = ? WHERE trial_id = ?",
            [STATUS_REJECTED_EVAL, json.dumps({"reason": reason}), trial_id],
        )

    def record_result(self, trial_id: str, metrics: dict, p_value: float,
                      train_sharpe: float | None = None,
                      train_ic: float | None = None):
        self._require_registered(trial_id)
        clean = {k: v for k, v in metrics.items() if k != "equity_curve"}
        self.db.conn.execute(
            """UPDATE trials_ledger
               SET status = ?, p_value = ?, sharpe = ?, ic = ?,
                   metrics_json = ?, train_sharpe = ?, train_ic = ?
               WHERE trial_id = ?""",
            [STATUS_EVALUATED, p_value, clean.get("sharpe"), clean.get("ic"),
             json.dumps(clean, default=float), train_sharpe, train_ic, trial_id],
        )

    def select_fdr(self, alpha: float = 0.20) -> list[dict]:
        """BY-FDR over the FULL ledger.

        Failed trials enter with p=1.0 — an attempt that produced nothing is
        still an attempt, and it must pay its share of the correction.
        """
        rows = self.db.conn.execute(
            """SELECT trial_id, status, p_value FROM trials_ledger
               WHERE status != ? ORDER BY created_at""",
            [STATUS_REGISTERED],
        ).fetchall()
        if not rows:
            return []
        pvals = [r[2] if (r[1] == STATUS_EVALUATED and r[2] is not None) else 1.0
                 for r in rows]
        selected = benjamini_yekutieli(pvals, alpha=alpha)
        out = []
        for (trial_id, status, p), sel in zip(rows, selected):
            if sel:
                out.append({"trial_id": trial_id, "p_value": p})
        return out

    def train_feedback(self, lane: str, limit: int = 30) -> list[dict]:
        """Feedback for the generator: TRAIN-window stats only.

        Deliberately excludes validation/test-window numbers so the LLM can
        never overfit to the held-out data through the feedback channel.
        """
        rows = self.db.conn.execute(
            """SELECT formula, status, train_sharpe, train_ic
               FROM trials_ledger WHERE lane = ? AND status != ?
               ORDER BY created_at DESC LIMIT ?""",
            [lane, STATUS_REGISTERED, limit],
        ).fetchall()
        return [
            {"formula": f, "status": s,
             "train_sharpe": None if ts is None else round(ts, 3),
             "train_ic": None if ti is None else round(ti, 4)}
            for f, s, ts, ti in rows
        ]

    def counts(self) -> dict:
        rows = self.db.conn.execute(
            "SELECT status, COUNT(*) FROM trials_ledger GROUP BY status"
        ).fetchall()
        return {status: n for status, n in rows}
