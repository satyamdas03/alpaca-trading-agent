import json
import logging
from datetime import datetime

from aqra.certify.dossier import CertifiedDossier
from aqra.db import AQRADatabase

logger = logging.getLogger(__name__)


class StrategyRegistry:
    def __init__(self, db: AQRADatabase):
        self.db = db

    def register(self, dossier: CertifiedDossier):
        if dossier.status != "CERTIFIED":
            logger.info("Not registering rejected strategy %s", dossier.candidate.id)
            return
        self.db.conn.execute("""
            INSERT OR REPLACE INTO strategy_registry (id, lane, name, signal_code, certified_at, status, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            dossier.candidate.id,
            dossier.candidate.lane.value,
            dossier.candidate.name,
            dossier.candidate.formula,
            dossier.certified_at,
            dossier.status,
            json.dumps({"metrics": dossier.metrics, "p_value": dossier.p_value, "coverage": dossier.coverage}),
        ])

    def active_strategies(self) -> list[tuple]:
        # Reconstruct dossiers from DB rows (simplified)
        rows = self.db.conn.execute("SELECT * FROM strategy_registry WHERE status='CERTIFIED'").fetchall()
        return rows
