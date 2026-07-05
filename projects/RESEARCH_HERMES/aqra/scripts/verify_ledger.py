"""CLI: export and verify a Proof-of-Trial ledger (Honest Agent Protocol, M4).

Usage examples:
  # Export the ledger from a DuckDB run to a hash-chained JSON-line file
  python scripts/verify_ledger.py --db runs/aqra.db --export ledger.jsonl

  # Verify an exported ledger (read certified set from metadata)
  python scripts/verify_ledger.py --verify ledger.jsonl

  # Verify against a specific list of certified trial IDs
  python scripts/verify_ledger.py --verify ledger.jsonl --claimed certified.json
"""

import argparse
import json
from pathlib import Path

from aqra.db import AQRADatabase
from aqra.generate.ledger import TrialsLedger
from aqra.verify.proof_of_trial import ProofOfTrialVerifier, LedgerExporter


def main() -> None:
    ap = argparse.ArgumentParser(description="Proof-of-Trial ledger exporter/verifier")
    ap.add_argument("--db", type=Path, help="Path to DuckDB database")
    ap.add_argument("--export", type=Path, help="Output JSON-line ledger path")
    ap.add_argument("--verify", type=Path, help="Ledger file to verify")
    ap.add_argument("--claimed", type=Path, help="JSON list of claimed certified trial IDs")
    ap.add_argument("--alpha", type=float, default=0.20)
    ap.add_argument("--online", action="store_true",
                    help="Use online-BY correction instead of batch BY")
    args = ap.parse_args()

    if args.export:
        if not args.db:
            ap.error("--db required with --export")
        db = AQRADatabase(str(args.db))
        try:
            ledger = TrialsLedger(db)
            exporter = LedgerExporter(ledger)
            exporter.export(args.export, alpha=args.alpha, online=args.online)
            print(f"Exported {args.export}")
        finally:
            db.close()

    if args.verify:
        verifier = ProofOfTrialVerifier(args.verify)
        claimed = None
        if args.claimed:
            claimed = set(json.loads(Path(args.claimed).read_text(encoding="utf-8")))
        report = verifier.verify(claimed_certified=claimed,
                                 alpha=args.alpha if args.alpha != 0.20 else None,
                                 online=args.online if args.online else None)
        print(report.summary())


if __name__ == "__main__":
    main()
