from dataclasses import dataclass


@dataclass
class BEARReview:
    passed: bool
    look_ahead_bias: bool
    data_mining: bool
    lane_misclassification: bool
    economic_rationale: bool
    robustness: bool
    summary: str
