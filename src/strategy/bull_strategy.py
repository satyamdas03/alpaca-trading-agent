import pandas as pd
from src.signals.quality import quality_score
from src.signals.momentum import momentum_score
from src.signals.regime import classify_regime, adjust_weights, Regime

BASE_WEIGHTS = {
    "quality": 0.25,
    "momentum": 0.30,
    "value": 0.10,
    "low_vol": 0.15,
    "sentiment": 0.20,
}


class BullStrategy:
    def __init__(self, vix: float = 18.0, quality_threshold: int = 6,
                 momentum_top_n: int = 15, stop_loss_pct: float = 0.07):
        self.vix = vix
        self.quality_threshold = quality_threshold
        self.momentum_top_n = momentum_top_n
        self.stop_loss_pct = stop_loss_pct
        self.regime = classify_regime(vix)
        self.weights = adjust_weights(BASE_WEIGHTS, self.regime)

    def generate_signals(self, prices: pd.DataFrame, fundamentals: dict | None = None,
                         prev_fundamentals: dict | None = None) -> dict:
        q_score = quality_score(fundamentals or {}, prev_fundamentals) / 9.0
        m_score = self._normalize_momentum(momentum_score(prices))

        signals = {
            "quality": q_score,
            "momentum": m_score,
            "value": 0.5,
            "low_vol": 0.5,
            "sentiment": 0.5,
        }

        composite = sum(signals[k] * self.weights[k] for k in signals)
        signals["composite"] = composite
        signals["regime"] = self.regime.value
        return signals

    def _normalize_momentum(self, raw_momentum: float) -> float:
        return max(0.0, min(1.0, (raw_momentum + 0.5) / 1.0))

    def pybroker_exec_fn(self):
        def exec_fn(ctx):
            if not ctx.long_pos():
                signals = self.generate_signals(
                    pd.DataFrame({"close": ctx.close}),
                )
                if signals["composite"] > 0.55:
                    ctx.buy_shares = ctx.shares // 10
                    ctx.stop_loss_pct = self.stop_loss_pct
                    ctx.hold_bars = 21
        return exec_fn