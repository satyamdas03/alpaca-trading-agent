from aqra.signals.base import SignalCandidate, Lane


class LaneSSignalLibrary:
    def generate(self) -> list[SignalCandidate]:
        return [
            SignalCandidate(
                id="S_MOM_12_1", lane=Lane.STRUCTURAL, name="12-1 Momentum",
                formula="rank(mom_12_1)", params={"holding_period": 21},
                rationale="Jegadeesh-Titman cross-sectional momentum"
            ),
            SignalCandidate(
                id="S_VALUE", lane=Lane.STRUCTURAL, name="Value Composite",
                formula="rank(pe_rank + pb_rank)", params={"holding_period": 21},
                rationale="Fama-French value premium"
            ),
            SignalCandidate(
                id="S_QUALITY", lane=Lane.STRUCTURAL, name="Quality",
                formula="rank(quality_score)", params={"holding_period": 21},
                rationale="Piotroski/gross-margin quality factor"
            ),
        ]
