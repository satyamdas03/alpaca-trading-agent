import pandas as pd
from src.signals.quality import quality_score
from src.signals.momentum import momentum_score
from src.signals.regime import classify_regime, adjust_weights, Regime
from src.signals.value import value_score
from src.signals.low_vol import low_vol_score
from src.signals.sentiment import sentiment_score

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
                         prev_fundamentals: dict | None = None,
                         current_price: float | None = None,
                         dark_pool_data: dict | None = None) -> dict:
        # Quality: neutral (0.5) when no fundamentals available
        q_raw = quality_score(fundamentals or {}, prev_fundamentals)
        q_score = q_raw / 9.0 if (fundamentals and q_raw > 0) else 0.5
        m_score = self._normalize_momentum(momentum_score(prices))
        v_score = value_score(fundamentals or {}, current_price)
        lv_score = low_vol_score(prices)
        s_score = sentiment_score(dark_pool_data or {})

        signals = {
            "quality": q_score,
            "momentum": m_score,
            "value": v_score,
            "low_vol": lv_score,
            "sentiment": s_score,
        }

        composite = sum(signals[k] * self.weights[k] for k in signals)
        signals["composite"] = composite
        signals["regime"] = self.regime.value
        return signals

    def _normalize_momentum(self, raw_momentum: float) -> float:
        return max(0.0, min(1.0, (raw_momentum + 0.5) / 1.0))