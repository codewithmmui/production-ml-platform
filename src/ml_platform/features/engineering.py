import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


def engineer_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    tenure = result["tenure_months"].clip(lower=1)
    result["avg_spend_per_month"] = result["total_spend"] / tenure
    result["ticket_rate"] = result["support_tickets"] / tenure
    result["engagement_score"] = (
        result["usage_score"] * 0.7 + (result["login_frequency"].clip(0, 30) / 30) * 0.3
    )
    result["payment_risk_score"] = result["payment_failures"] / (tenure + 1)
    result["inactive_customer_flag"] = (result["days_since_last_login"] >= 30).astype(int)
    result["high_value_customer"] = (result["monthly_spend"] >= 100).astype(int)
    return result


class FeatureEngineer(TransformerMixin, BaseEstimator):  # type: ignore[misc]
    def fit(self, X: pd.DataFrame, y: object = None) -> "FeatureEngineer":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return engineer_features(X)
