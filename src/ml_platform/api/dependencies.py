from typing import cast

from fastapi import Request

from ml_platform.core.exceptions import ModelUnavailableError
from ml_platform.inference.predictor import Predictor


def get_predictor(request: Request) -> Predictor:
    predictor = getattr(request.app.state, "predictor", None)
    if predictor is None:
        raise ModelUnavailableError("model is not available")
    return cast(Predictor, predictor)
