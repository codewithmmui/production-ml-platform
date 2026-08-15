from dataclasses import dataclass

from ml_platform.training.evaluate import ModelMetrics


@dataclass(frozen=True)
class QualityGate:
    min_roc_auc: float = 0.72
    min_pr_auc: float = 0.40
    min_f1: float = 0.45
    max_latency_ms: float = 25.0
    min_champion_improvement: float = 0.005


def promotion_decision(
    candidate: ModelMetrics, gate: QualityGate, champion: ModelMetrics | None = None
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    checks = {
        "roc_auc": candidate.roc_auc >= gate.min_roc_auc,
        "pr_auc": candidate.pr_auc >= gate.min_pr_auc,
        "f1": candidate.f1 >= gate.min_f1,
        "latency_ms": candidate.latency_ms <= gate.max_latency_ms,
    }
    failures.extend(name for name, passed in checks.items() if not passed)
    if champion and candidate.roc_auc < champion.roc_auc + gate.min_champion_improvement:
        failures.append("champion_improvement")
    return not failures, failures
