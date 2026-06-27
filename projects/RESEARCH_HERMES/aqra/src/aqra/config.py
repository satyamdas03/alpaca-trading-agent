import os
from dataclasses import dataclass

from aqra.constants import (
    DEFAULT_LANE_I_SPLIT,
    DEFAULT_LANE_S_SPLIT,
    DEFAULT_PAPER_CAPITAL,
)


@dataclass(frozen=True)
class AQRAConfig:
    paper_capital: float
    lane_s_split: float
    lane_i_split: float
    data_dir: str
    memory_dir: str
    alpaca_api_key: str | None
    alpaca_secret_key: str | None
    fred_api_key: str | None
    finnhub_api_key: str | None
    fmp_api_key: str | None
    polygon_api_key: str | None
    anthropic_api_key: str | None

    @property
    def lane_s_capital(self) -> float:
        return self.paper_capital * self.lane_s_split

    @property
    def lane_i_capital(self) -> float:
        return self.paper_capital * self.lane_i_split


def load_config() -> AQRAConfig:
    return AQRAConfig(
        paper_capital=float(os.getenv("AQRA_PAPER_CAPITAL", DEFAULT_PAPER_CAPITAL)),
        lane_s_split=float(os.getenv("AQRA_LANE_S_SPLIT", DEFAULT_LANE_S_SPLIT)),
        lane_i_split=float(os.getenv("AQRA_LANE_I_SPLIT", DEFAULT_LANE_I_SPLIT)),
        data_dir=os.getenv("AQRA_DATA_DIR", "data"),
        memory_dir=os.getenv("AQRA_MEMORY_DIR", "memory"),
        alpaca_api_key=os.getenv("ALPACA_API_KEY"),
        alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY"),
        fred_api_key=os.getenv("FRED_API_KEY"),
        finnhub_api_key=os.getenv("FINNHUB_API_KEY"),
        fmp_api_key=os.getenv("FMP_API_KEY"),
        polygon_api_key=os.getenv("POLYGON_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    )
