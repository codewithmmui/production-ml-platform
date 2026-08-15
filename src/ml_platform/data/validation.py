import pandas as pd

from ml_platform.core.constants import CATEGORICAL_FEATURES, ENTITY, NUMERIC_FEATURES, TARGET
from ml_platform.core.exceptions import DataValidationError

ALLOWED = {
    "subscription_plan": {"basic", "standard", "premium"},
    "contract_type": {"monthly", "annual", "two_year"},
    "region": {"north", "south", "east", "west"},
}
RANGES = {
    "tenure_months": (0, 120),
    "monthly_spend": (0, 1000),
    "total_spend": (0, 100_000),
    "support_tickets": (0, 100),
    "login_frequency": (0, 1000),
    "payment_failures": (0, 50),
    "days_since_last_login": (0, 3650),
    "usage_score": (0, 1),
}


def validate_dataframe(frame: pd.DataFrame, *, require_target: bool = True) -> pd.DataFrame:
    required = {ENTITY, *NUMERIC_FEATURES, *CATEGORICAL_FEATURES}
    if require_target:
        required.add(TARGET)
    missing = sorted(required - set(frame.columns))
    errors: list[str] = []
    if missing:
        errors.append(f"missing required columns: {missing}")
    if ENTITY in frame and frame[ENTITY].duplicated().any():
        errors.append("duplicate customer_id values")
    for col, (low, high) in RANGES.items():
        if col in frame:
            values = pd.to_numeric(frame[col], errors="coerce")
            if ((values.dropna() < low) | (values.dropna() > high)).any():
                errors.append(f"{col} contains values outside [{low}, {high}]")
            if values.isna().mean() > 0.05:
                errors.append(f"{col} null/invalid rate exceeds 5%")
    for col, allowed in ALLOWED.items():
        if col in frame:
            invalid = set(frame[col].dropna().astype(str)) - allowed
            if invalid:
                errors.append(f"{col} contains invalid categories: {sorted(invalid)}")
            if frame[col].isna().mean() > 0.05:
                errors.append(f"{col} null rate exceeds 5%")
    if (
        require_target
        and TARGET in frame
        and not set(frame[TARGET].dropna().unique()).issubset({0, 1})
    ):
        errors.append("churned must be binary")
    if errors:
        raise DataValidationError("; ".join(errors))
    return frame
