from pydantic import BaseModel, Field

from ml_platform.data.schemas import CustomerFeatures


class BatchPredictionRequest(BaseModel):
    customers: list[CustomerFeatures] = Field(min_length=1, max_length=1000)


class PredictionResponse(BaseModel):
    customer_id: str
    prediction: str
    churn_probability: float
    model_version: str
    request_id: str
