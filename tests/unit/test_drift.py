from ml_platform.data.generate import generate_churn_data
from ml_platform.monitoring.drift import DriftConfig, detect_drift


def test_drift_below_and_above_threshold() -> None:
    reference = generate_churn_data(3000, 10)
    same = generate_churn_data(3000, 10)
    shifted = generate_churn_data(3000, 11, drift=True)
    assert detect_drift(reference, same)["drift_detected"] is False
    report = detect_drift(reference, shifted, DriftConfig(numeric_psi=0.08))
    assert report["drift_detected"] is True
    assert "monthly_spend" in report["drifted_features"]
