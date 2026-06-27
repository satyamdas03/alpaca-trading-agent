import numpy as np
from aqra.conformal.multiple_testing import benjamini_yekutieli


class ConformalValidator:
    def __init__(self, calib_predictions: np.ndarray, calib_true: np.ndarray, alpha: float = 0.10):
        self.alpha = alpha
        self.residuals = np.abs(calib_true - calib_predictions)
        self.q_hat = np.quantile(self.residuals, np.ceil((len(self.residuals) + 1) * (1 - alpha)) / len(self.residuals))

    def predict_interval(self, prediction: float) -> tuple[float, float]:
        return (prediction - self.q_hat, prediction + self.q_hat)

    def p_value(self, prediction: float, actual: float) -> float:
        """Conformal p-value for null: prediction and actual are exchangeable with zero edge."""
        score = abs(actual - prediction)
        return (np.sum(self.residuals >= score) + 1) / (len(self.residuals) + 1)

    def select_strategies(self, predictions: list[np.ndarray], actuals: list[np.ndarray]) -> list[bool]:
        pvals = []
        for pred, act in zip(predictions, actuals):
            p = self.p_value(float(pred.mean()), float(act.mean()))
            pvals.append(p)
        return benjamini_yekutieli(pvals, self.alpha)
