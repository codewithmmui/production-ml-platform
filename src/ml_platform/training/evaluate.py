from dataclasses import asdict, dataclass
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass(frozen=True)
class ModelMetrics:
    roc_auc: float
    pr_auc: float
    f1: float
    precision: float
    recall: float
    latency_ms: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def evaluate_model(model: object, X: pd.DataFrame, y: pd.Series) -> ModelMetrics:
    start = perf_counter()
    probabilities = model.predict_proba(X)[:, 1]  # type: ignore[attr-defined]
    latency_ms = (perf_counter() - start) * 1000 / max(len(X), 1)
    predicted = (probabilities >= 0.5).astype(int)
    return ModelMetrics(
        roc_auc=float(roc_auc_score(y, probabilities)),
        pr_auc=float(average_precision_score(y, probabilities)),
        f1=float(f1_score(y, predicted, zero_division=0)),
        precision=float(precision_score(y, predicted, zero_division=0)),
        recall=float(recall_score(y, predicted, zero_division=0)),
        latency_ms=float(latency_ms),
    )


def confusion_values(model: object, X: pd.DataFrame, y: pd.Series) -> list[list[int]]:
    from sklearn.metrics import confusion_matrix

    values: list[list[int]] = (
        np.asarray(
            confusion_matrix(y, model.predict(X))  # type: ignore[attr-defined]
        )
        .astype(int)
        .tolist()
    )
    return values
