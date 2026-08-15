import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml_platform.core.config import get_settings
from ml_platform.core.constants import CATEGORICAL_FEATURES, ENTITY, NUMERIC_FEATURES, TARGET
from ml_platform.data.ingest import ingest_csv
from ml_platform.features.engineering import FeatureEngineer
from ml_platform.training.evaluate import ModelMetrics, confusion_values, evaluate_model
from ml_platform.training.registry import QualityGate, promotion_decision

DERIVED = [
    "avg_spend_per_month",
    "ticket_rate",
    "engagement_score",
    "payment_risk_score",
    "inactive_customer_flag",
    "high_value_customer",
]


def get_git_sha() -> str:
    supplied_sha = os.getenv("GIT_SHA", "").strip()
    if supplied_sha:
        return supplied_sha
    if shutil.which("git") is None:
        return "unavailable"
    return (
        subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
        ).stdout.strip()
        or "unavailable"
    )


def build_pipeline(model: object) -> Pipeline:
    numeric = NUMERIC_FEATURES + DERIVED
    preprocessor = ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
                ),
                numeric,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    return Pipeline(
        [("features", FeatureEngineer()), ("preprocess", preprocessor), ("model", model)]
    )


def train_models(
    frame: pd.DataFrame, *, tune: bool = False, seed: int = 42
) -> tuple[Pipeline, dict[str, object]]:
    X = frame.drop(columns=[TARGET, ENTITY])
    y = frame[TARGET].astype(int)
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=seed
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.25, stratify=y_train_val, random_state=seed
    )
    models = {
        "logistic_regression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=seed
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=180,
            max_depth=12,
            min_samples_leaf=3,
            class_weight="balanced",
            n_jobs=-1,
            random_state=seed,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=180, learning_rate=0.08, max_leaf_nodes=24, random_state=seed
        ),
    }
    results: dict[str, object] = {}
    candidates: dict[str, Pipeline] = {}
    for name, estimator in models.items():
        pipeline = build_pipeline(estimator)
        pipeline.fit(X_train, y_train)
        metrics = evaluate_model(pipeline, X_val, y_val)
        results[name] = metrics.to_dict()
        candidates[name] = pipeline
    best_name = max(results, key=lambda name: (results[name]["pr_auc"], results[name]["roc_auc"]))  # type: ignore[index]
    best = candidates[best_name]
    if tune and best_name == "random_forest":
        search = RandomizedSearchCV(
            best,
            {
                "model__n_estimators": [120, 180, 250],
                "model__max_depth": [8, 12, 16],
                "model__min_samples_leaf": [2, 3, 5],
            },
            n_iter=5,
            scoring="average_precision",
            cv=3,
            random_state=seed,
            n_jobs=-1,
        )
        search.fit(X_train, y_train)
        best = search.best_estimator_
        results["tuning"] = {
            "best_params": search.best_params_,
            "best_cv_pr_auc": float(search.best_score_),
        }
    best.fit(X_train_val, y_train_val)
    test_metrics = evaluate_model(best, X_test, y_test)
    results["selected_model"] = best_name
    results["test"] = test_metrics.to_dict()
    results["confusion_matrix"] = confusion_values(best, X_test, y_test)
    return best, results


def train_and_save(data_path: Path, output_dir: Path, *, tune: bool = False) -> dict[str, object]:
    frame = ingest_csv(data_path)
    model, results = train_models(frame, tune=tune)
    metrics = results["test"]
    assert isinstance(metrics, dict)
    typed_metrics = ModelMetrics(**metrics)
    passed, failures = promotion_decision(typed_metrics, QualityGate())
    results["promotion"] = {
        "decision": "PROMOTE TO PRODUCTION" if passed else "DO NOT PROMOTE",
        "failures": failures,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.joblib"
    joblib.dump(model, model_path)
    git_sha = get_git_sha()
    dataset_hash = hashlib.sha256(data_path.read_bytes()).hexdigest()
    metadata = {
        "model_version": "1",
        "trained_at": datetime.now(UTC).isoformat(),
        "git_sha": git_sha,
        "dataset_sha256": dataset_hash,
        **results,
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    settings = get_settings()
    try:
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment("customer-churn")
        with mlflow.start_run(run_name=str(results["selected_model"])):
            mlflow.log_params(
                {
                    "selected_model": results["selected_model"],
                    "dataset_sha256": dataset_hash,
                    "git_sha": git_sha,
                }
            )
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(output_dir / "metadata.json"))
    except Exception as exc:
        print(f"MLflow tracking unavailable; local artifacts retained: {exc}")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/raw/customers.csv"))
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    parser.add_argument("--tune", action="store_true")
    args = parser.parse_args()
    metadata = train_and_save(args.data, args.output, tune=args.tune)
    print(json.dumps(metadata["test"], indent=2))
    print(metadata["promotion"])


if __name__ == "__main__":
    main()
