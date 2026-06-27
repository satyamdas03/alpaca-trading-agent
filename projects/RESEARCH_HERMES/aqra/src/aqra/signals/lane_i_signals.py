from aqra.signals.base import SignalCandidate, Lane


class LaneISignalLibrary:
    def generate(self) -> list[SignalCandidate]:
        return [
            SignalCandidate(
                id="I_GAP", lane=Lane.INFORMATIONAL, name="Overnight Gap",
                formula="rank(overnight_gap)", params={"holding_period": 1},
                rationale="Short-term reversal/continuation of overnight gaps"
            ),
            SignalCandidate(
                id="I_VOLUME", lane=Lane.INFORMATIONAL, name="Volume Spike",
                formula="rank(volume_zscore)", params={"holding_period": 1},
                rationale="Unusual volume predicts price pressure"
            ),
            SignalCandidate(
                id="I_SENTIMENT", lane=Lane.INFORMATIONAL, name="Sentiment Shock",
                formula="rank(news_sentiment_zscore)", params={"holding_period": 1},
                rationale="News sentiment anomaly"
            ),
        ]
