from ml_platform.training.evaluate import ModelMetrics
from ml_platform.training.registry import QualityGate, promotion_decision


def test_quality_gate_and_champion_comparison() -> None:
    candidate = ModelMetrics(0.82, 0.60, 0.58, 0.55, 0.62, 2.0)
    assert promotion_decision(candidate, QualityGate())[0]
    champion = ModelMetrics(0.83, 0.60, 0.58, 0.55, 0.62, 2.0)
    passed, failures = promotion_decision(candidate, QualityGate(), champion)
    assert not passed and "champion_improvement" in failures
