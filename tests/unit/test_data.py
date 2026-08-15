import pandas as pd
import pytest

from ml_platform.core.exceptions import DataValidationError
from ml_platform.data.generate import generate_churn_data
from ml_platform.data.validation import validate_dataframe


def test_generation_is_deterministic_and_nonrandom_signal() -> None:
    first = generate_churn_data(1000, 42)
    second = generate_churn_data(1000, 42)
    pd.testing.assert_frame_equal(first, second)
    assert 0.05 < first.churned.mean() < 0.65
    assert (
        first.groupby("contract_type").churned.mean()["monthly"]
        > first.groupby("contract_type").churned.mean()["two_year"]
    )


def test_validation_rejects_duplicate_and_negative_spend() -> None:
    frame = generate_churn_data(200)
    frame.loc[1, "customer_id"] = frame.loc[0, "customer_id"]
    frame.loc[2, "monthly_spend"] = -1
    with pytest.raises(DataValidationError, match=r"duplicate.*monthly_spend"):
        validate_dataframe(frame)


def test_drift_mode_changes_distributions() -> None:
    normal = generate_churn_data(2000, 42)
    shifted = generate_churn_data(2000, 42, drift=True)
    assert shifted.monthly_spend.mean() > normal.monthly_spend.mean() + 8
