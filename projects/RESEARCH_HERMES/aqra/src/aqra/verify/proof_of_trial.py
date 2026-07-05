"""Proof-of-Trial: hash-chained ledger export + independent verifier.

The ledger discipline says every candidate is registered BEFORE evaluation,
and the FDR correction runs over every registered trial.  A third party
should be able to recompute that correction from a published transcript
without trusting the agent that produced it.

This module provides:
  - A hash-chained JSON-line ledger format (`TrialEntry`, `LedgerExporter`).
  - An independent verifier (`ProofOfTrialVerifier`) that checks chain
    integrity and recomputes BY-FDR / online-BY selections.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from aqra.conformal.multiple_testing import (
    benjamini_yekutieli,
    e_bh_rejections,
    online_by_rejections,
    online_e_bh_rejections,
)
from aqra.generate.ledger import (
    STATUS_EVALUATED,
    STATUS_REJECTED_EVAL,
    STATUS_REJECTED_INVALID,
    TrialsLedger,
)

GENESIS_HASH = "0" * 64


@dataclass
class TrialEntry:
    """One tamper-evident record in the published ledger."""

    trial_id: str
    created_at: str  # ISO-8601 UTC
    previous_hash: str
    dsl_version: str
    lane: str
    status: str
    p_value: float | None
    e_value: float | None = None
    formula: str | None = None
    rationale: str | None = None
    source: str | None = None
    metrics_json: str = "{}"
    this_hash: str | None = None

    def canonical_dict(self) -> dict:
        """Fields that enter the hash (excluding this_hash itself)."""
        return {
            "trial_id": self.trial_id,
            "created_at": self.created_at,
            "previous_hash": self.previous_hash,
            "dsl_version": self.dsl_version,
            "lane": self.lane,
            "status": self.status,
            "p_value": self.p_value,
            "e_value": self.e_value,
            "formula": self.formula,
            "rationale": self.rationale,
            "source": self.source,
            "metrics_json": self.metrics_json,
        }

    def compute_hash(self) -> str:
        payload = json.dumps(self.canonical_dict(), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def seal(self) -> "TrialEntry":
        """Set this_hash from canonical fields; idempotent."""
        self.this_hash = self.compute_hash()
        return self

    def to_dict(self) -> dict:
        d = self.canonical_dict()
        d["this_hash"] = self.this_hash or self.compute_hash()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "TrialEntry":
        return cls(
            trial_id=d["trial_id"],
            created_at=d["created_at"],
            previous_hash=d["previous_hash"],
            dsl_version=d["dsl_version"],
            lane=d["lane"],
            status=d["status"],
            p_value=d.get("p_value"),
            e_value=d.get("e_value"),
            formula=d.get("formula"),
            rationale=d.get("rationale"),
            source=d.get("source"),
            metrics_json=d.get("metrics_json", "{}"),
            this_hash=d.get("this_hash"),
        )


@dataclass
class VerificationReport:
    """Result of an independent audit."""

    valid: bool
    n_trials: int
    n_evaluated: int
    hash_chain_ok: bool
    certified_claimed: set[str] = field(default_factory=set)
    certified_recomputed: set[str] = field(default_factory=set)
    discrepancies: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "Proof-of-Trial verification report",
            f"  valid            : {self.valid}",
            f"  hash chain OK    : {self.hash_chain_ok}",
            f"  trials audited   : {self.n_trials}",
            f"  evaluated trials : {self.n_evaluated}",
            f"  claimed certs    : {len(self.certified_claimed)}",
            f"  recomputed certs : {len(self.certified_recomputed)}",
        ]
        if self.discrepancies:
            lines.append("  discrepancies:")
            for d in self.discrepancies[:10]:
                lines.append(f"    - {d}")
            if len(self.discrepancies) > 10:
                lines.append(f"    ... and {len(self.discrepancies) - 10} more")
        return "\n".join(lines)


class LedgerExporter:
    """Export a DuckDB-backed `TrialsLedger` to a hash-chained JSON-line file."""

    def __init__(self, ledger: TrialsLedger):
        self.ledger = ledger

    def export(self, path: Path | str, alpha: float = 0.20,
               online: bool = False, use_e: bool = False) -> Path:
        """Write a JSON-line ledger plus recomputed certifications.

        Each line is one JSON object. The last metadata line contains the
        FDR level, the certified set, and the correction method used.
        """
        path = Path(path)
        rows = self.ledger.db.conn.execute(
            """SELECT trial_id, created_at, dsl_version, lane, status,
                      p_value, e_value, formula, rationale, source, metrics_json
               FROM trials_ledger
               ORDER BY created_at"""
        ).fetchall()

        entries: list[TrialEntry] = []
        prev_hash = GENESIS_HASH
        for row in rows:
            (trial_id, created_at, dsl_version, lane, status,
             p_value, e_value, formula, rationale, source, metrics_json) = row
            # created_at may be a datetime object or ISO string
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            entry = TrialEntry(
                trial_id=trial_id,
                created_at=created_at or datetime.now(timezone.utc).isoformat(),
                previous_hash=prev_hash,
                dsl_version=dsl_version or "",
                lane=lane or "",
                status=status,
                p_value=p_value,
                e_value=e_value,
                formula=formula,
                rationale=rationale,
                source=source,
                metrics_json=metrics_json or "{}",
            ).seal()
            entries.append(entry)
            prev_hash = entry.this_hash

        # Recompute certifications from the exported p-values or e-values.
        pvals, evals, ids = [], [], []
        for e in entries:
            if e.status == STATUS_EVALUATED:
                pvals.append(e.p_value if e.p_value is not None else 1.0)
                evals.append(e.e_value if e.e_value is not None else 0.0)
                ids.append(e.trial_id)
            else:
                # Failed/invalid trials still count in the ledger but are
                # not certifiable.
                pvals.append(1.0)
                evals.append(0.0)
                ids.append(e.trial_id)

        if use_e:
            if online:
                selected = online_e_bh_rejections(evals, alpha)
                method = "online_e_bh"
            else:
                selected = e_bh_rejections(evals, alpha)
                method = "e_bh"
        else:
            if online:
                selected = online_by_rejections(pvals, alpha)
                method = "online_by"
            else:
                selected = benjamini_yekutieli(pvals, alpha)
                method = "benjamini_yekutieli"
        certified = {tid for tid, sel in zip(ids, selected) if sel}

        with path.open("w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e.to_dict(), default=str) + "\n")
            meta = {
                "_meta": True,
                "alpha": alpha,
                "method": method,
                "use_e": use_e,
                "n_trials": len(entries),
                "certified": sorted(certified),
                "genesis_hash": GENESIS_HASH,
                "tail_hash": prev_hash if entries else GENESIS_HASH,
            }
            f.write(json.dumps(meta, default=str) + "\n")
        return path


class ProofOfTrialVerifier:
    """Independent checker for a published JSON-line ledger."""

    def __init__(self, ledger_path: Path | str):
        self.path = Path(ledger_path)
        self.entries: list[TrialEntry] = []
        self.meta: dict = {}
        self._load()

    def _load(self) -> None:
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if obj.get("_meta"):
                self.meta = obj
            else:
                self.entries.append(TrialEntry.from_dict(obj))

    def verify(self, claimed_certified: Iterable[str] | None = None,
               alpha: float | None = None,
               online: bool | None = None,
               use_e: bool | None = None) -> VerificationReport:
        """Verify chain integrity and optionally recompute FDR selections.

        If `claimed_certified` is None, the verifier reads the certified set
        from the ledger metadata and checks that it equals the recomputed set.
        """
        report = VerificationReport(valid=True, n_trials=len(self.entries),
                                     n_evaluated=0, hash_chain_ok=True)
        report.certified_claimed = set(claimed_certified) if claimed_certified is not None else set(self.meta.get("certified", []))
        alpha = alpha if alpha is not None else self.meta.get("alpha", 0.20)
        method = self.meta.get("method")
        if use_e is None:
            use_e = method in ("e_bh", "online_e_bh")
        if online is None:
            online = method in ("online_by", "online_e_bh")

        prev_hash = GENESIS_HASH
        for i, e in enumerate(self.entries):
            if e.previous_hash != prev_hash:
                report.hash_chain_ok = False
                report.discrepancies.append(
                    f"trial {e.trial_id}: previous_hash {e.previous_hash} "
                    f"!= expected {prev_hash}"
                )
            recomputed = e.compute_hash()
            if e.this_hash != recomputed:
                report.hash_chain_ok = False
                report.discrepancies.append(
                    f"trial {e.trial_id}: this_hash mismatch (tampered?)"
                )
            prev_hash = e.this_hash or recomputed

        # Recompute FDR from the ledger.
        pvals, evals, ids = [], [], []
        for e in self.entries:
            if e.status == STATUS_EVALUATED:
                pvals.append(e.p_value if e.p_value is not None else 1.0)
                evals.append(e.e_value if e.e_value is not None else 0.0)
                ids.append(e.trial_id)
                report.n_evaluated += 1
            else:
                pvals.append(1.0)
                evals.append(0.0)
                ids.append(e.trial_id)

        if use_e:
            if online:
                selected = online_e_bh_rejections(evals, alpha)
            else:
                selected = e_bh_rejections(evals, alpha)
        else:
            if online:
                selected = online_by_rejections(pvals, alpha)
            else:
                selected = benjamini_yekutieli(pvals, alpha)
        report.certified_recomputed = {tid for tid, sel in zip(ids, selected) if sel}

        missing = report.certified_claimed - report.certified_recomputed
        extra = report.certified_recomputed - report.certified_claimed
        if missing:
            report.discrepancies.append(
                f"claimed certifications not reproduced by FDR correction: "
                f"{sorted(missing)[:5]}"
            )
        if extra:
            report.discrepancies.append(
                f"recomputed certifications not claimed by agent: "
                f"{sorted(extra)[:5]}"
            )

        report.valid = report.hash_chain_ok and not report.discrepancies
        return report
