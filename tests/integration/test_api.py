import json

import joblib
from fastapi.testclient import TestClient

from ml_platform.api.main import app, settings
from ml_platform.data.generate import generate_churn_data
from ml_platform.training.train import train_models


def valid_customer() -> dict[str, object]:
    return {
        "customer_id": "CUST-10001",
        "tenure_months": 13,
        "monthly_spend": 79.99,
        "total_spend": 1020.5,
        "support_tickets": 4,
        "login_frequency": 3,
        "subscription_plan": "premium",
        "payment_failures": 2,
        "days_since_last_login": 15,
        "usage_score": 0.42,
        "contract_type": "monthly",
        "region": "south",
    }


def test_health_readiness_prediction_and_validation(tmp_path) -> None:
    model, results = train_models(generate_churn_data(1200))
    settings.model_path = tmp_path / "model.joblib"
    settings.model_metadata_path = tmp_path / "metadata.json"
    joblib.dump(model, settings.model_path)
    settings.model_metadata_path.write_text(json.dumps({"model_version": "test", **results}))
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 200
        response = client.post("/predict", json=valid_customer())
        assert response.status_code == 200
        assert 0 <= response.json()["churn_probability"] <= 1
        invalid = valid_customer() | {"monthly_spend": -1}
        assert client.post("/predict", json=invalid).status_code == 422
