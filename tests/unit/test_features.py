import pandas as pd

from ml_platform.features.engineering import engineer_features


def test_engineering_is_stable_and_avoids_target() -> None:
    frame = pd.DataFrame(
        {
            "tenure_months": [0],
            "monthly_spend": [120.0],
            "total_spend": [0.0],
            "support_tickets": [3],
            "login_frequency": [4],
            "payment_failures": [1],
            "days_since_last_login": [40],
            "usage_score": [0.2],
        }
    )
    result = engineer_features(frame)
    assert result.loc[0, "inactive_customer_flag"] == 1
    assert result.loc[0, "high_value_customer"] == 1
    assert "churned" not in result
