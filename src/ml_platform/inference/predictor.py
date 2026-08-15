from typing import Any

import pandas as pd

from ml_platform.inference.model_loader import LoadedModel


class Predictor:
    def __init__(self, loaded: LoadedModel) -> None:
        self.loaded = loaded

    def predict(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        frame = pd.DataFrame(records)
        identifiers = frame.pop("customer_id").tolist()
        probabilities = self.loaded.pipeline.predict_proba(frame)[:, 1]
        version = str(self.loaded.metadata.get("model_version", "unknown"))
        return [
            {
                "customer_id": cid,
                "prediction": "churn" if p >= 0.5 else "retain",
                "churn_probability": round(float(p), 6),
                "model_version": version,
            }
            for cid, p in zip(identifiers, probabilities, strict=True)
        ]

    def explain(self, record: dict[str, Any]) -> dict[str, Any]:
        prediction = self.predict([record])[0]
        return {
            **prediction,
            "explanation": {"method": "risk_factors", "factors": _risk_factors(record)},
        }


def _risk_factors(record: dict[str, Any]) -> list[dict[str, object]]:
    rules = [
        ("payment_failures", float(record["payment_failures"]), 1),
        ("support_tickets", float(record["support_tickets"]), 2),
        ("days_since_last_login", float(record["days_since_last_login"]), 14),
        ("low_usage_score", 1 - float(record["usage_score"]), 0.5),
    ]
    return [
        {"feature": name, "value": value, "direction": "increases_churn_risk"}
        for name, value, threshold in rules
        if value > threshold
    ]
