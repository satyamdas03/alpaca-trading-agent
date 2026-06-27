import logging

from aqra.config import AQRAConfig
from aqra.constants import DEFAULT_MAX_DRAWDOWN_PCT

logger = logging.getLogger(__name__)


class DeploymentGate:
    def __init__(self, config: AQRAConfig):
        self.config = config
        self.daily_pnl_limit = -0.05 * config.paper_capital

    def can_trade_live(self) -> bool:
        return bool(self.config.alpaca_api_key and self.config.alpaca_secret_key)

    def check_safety(self, current_equity: float, day_pnl: float, open_positions: int) -> bool:
        if day_pnl < self.daily_pnl_limit:
            logger.error("Daily loss limit hit: %s", day_pnl)
            return False
        drawdown = (current_equity - self.config.paper_capital) / self.config.paper_capital
        if drawdown < -DEFAULT_MAX_DRAWDOWN_PCT:
            logger.error("Max drawdown hit: %s", drawdown)
            return False
        return True
