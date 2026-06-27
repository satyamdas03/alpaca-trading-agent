from enum import Enum
from pathlib import Path


class Lane(Enum):
    STRUCTURAL = "S"
    INFORMATIONAL = "I"


# Lane defaults
DEFAULT_LANE_S_SPLIT = 0.65
DEFAULT_LANE_I_SPLIT = 0.35
DEFAULT_PAPER_CAPITAL = 10_000.0
DEFAULT_MAX_DRAWDOWN_PCT = 0.20
DEFAULT_LANE_I_TURNOVER_CAP = 10.0  # 1000% annualized

# Certification thresholds
CONFORMAL_COVERAGE_TARGET = 0.90
FDR_TARGET = 0.20
MIN_LANE_S_STRATEGIES = 2
MIN_LANE_I_STRATEGIES = 2
MAX_CROSS_LANE_CORR = 0.5

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DIR = PROJECT_ROOT / "memory"
