from prometheus_client import Counter, Gauge, Histogram

PREDICTION_REQUESTS = Counter("prediction_requests_total", "Prediction requests", ["endpoint"])
PREDICTION_ERRORS = Counter("prediction_errors_total", "Prediction errors", ["error_type"])
PREDICTION_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Prediction latency",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1),
)
PREDICTION_CLASS = Counter("prediction_class_total", "Predicted classes", ["class_name"])
MODEL_LOADED = Gauge("model_loaded", "Whether a model is loaded")
MODEL_VERSION = Gauge("model_version_info", "Loaded model information", ["version"])
DRIFT_SCORE = Gauge("drift_score", "Latest aggregate drift score")
FEATURE_STORE_LATENCY = Histogram(
    "feature_store_latency_seconds", "Feature store operation latency", ["operation"]
)
