import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any, cast

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from ml_platform.api.dependencies import get_predictor
from ml_platform.api.schemas import BatchPredictionRequest, PredictionResponse
from ml_platform.core.config import get_settings
from ml_platform.core.exceptions import MLPlatformError, ModelUnavailableError
from ml_platform.data.schemas import CustomerFeatures
from ml_platform.inference.model_loader import load_model
from ml_platform.inference.predictor import Predictor
from ml_platform.monitoring.logging import configure_logging
from ml_platform.monitoring.metrics import (
    MODEL_LOADED,
    MODEL_VERSION,
    PREDICTION_CLASS,
    PREDICTION_ERRORS,
    PREDICTION_LATENCY,
    PREDICTION_REQUESTS,
)

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("ml_platform.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.predictor = None
    try:
        loaded = load_model(settings.model_path, settings.model_metadata_path)
        app.state.predictor = Predictor(loaded)
        MODEL_LOADED.set(1)
        MODEL_VERSION.labels(version=str(loaded.metadata.get("model_version", "unknown"))).set(1)
    except ModelUnavailableError as exc:
        MODEL_LOADED.set(0)
        logger.warning(
            "model unavailable at startup",
            extra={"event": "model_load_failed", "request_id": "startup", "reason": str(exc)},
        )
    yield
    app.state.predictor = None
    MODEL_LOADED.set(0)


app = FastAPI(title="Production ML Platform", version="1.0.0", lifespan=lifespan)
PredictorDependency = Annotated[Predictor, Depends(get_predictor)]


@app.middleware("http")
async def request_context(request: Request, call_next: Any) -> Response:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:128]
    request.state.request_id = request_id
    start = time.perf_counter()
    response = cast(Response, await call_next(request))
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request complete",
        extra={
            "event": "request_complete",
            "request_id": request_id,
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            "status": response.status_code,
        },
    )
    return response


@app.exception_handler(MLPlatformError)
async def domain_error(request: Request, exc: MLPlatformError) -> JSONResponse:
    PREDICTION_ERRORS.labels(error_type=type(exc).__name__).inc()
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": type(exc).__name__,
                "message": str(exc),
                "request_id": request.state.request_id,
            }
        },
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "production-ml-platform", "docs": "/docs"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/ready")
def ready(request: Request) -> JSONResponse:
    available = request.app.state.predictor is not None
    return JSONResponse(
        status_code=200 if available else 503,
        content={"status": "ready" if available else "not_ready", "model_loaded": available},
    )


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/model/info")
def model_info(predictor: PredictorDependency) -> dict[str, Any]:
    metadata = predictor.loaded.metadata
    return {
        key: metadata.get(key)
        for key in ("model_version", "trained_at", "selected_model", "test", "dataset_sha256")
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(
    customer: CustomerFeatures, request: Request, predictor: PredictorDependency
) -> dict[str, Any]:
    PREDICTION_REQUESTS.labels(endpoint="single").inc()
    with PREDICTION_LATENCY.time():
        result = predictor.predict([customer.model_dump()])[0]
    PREDICTION_CLASS.labels(class_name=result["prediction"]).inc()
    return {**result, "request_id": request.state.request_id}


@app.post("/predict/batch")
def predict_batch(
    payload: BatchPredictionRequest, request: Request, predictor: PredictorDependency
) -> dict[str, Any]:
    PREDICTION_REQUESTS.labels(endpoint="batch").inc()
    with PREDICTION_LATENCY.time():
        results = predictor.predict([item.model_dump() for item in payload.customers])
    return {
        "predictions": [{**result, "request_id": request.state.request_id} for result in results]
    }


@app.post("/explain")
def explain(
    customer: CustomerFeatures, request: Request, predictor: PredictorDependency
) -> dict[str, Any]:
    return {**predictor.explain(customer.model_dump()), "request_id": request.state.request_id}
