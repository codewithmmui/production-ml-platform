from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CustomerFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    customer_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    tenure_months: int = Field(ge=0, le=120)
    monthly_spend: float = Field(ge=0, le=1000)
    total_spend: float = Field(ge=0, le=100_000)
    support_tickets: int = Field(ge=0, le=100)
    login_frequency: int = Field(ge=0, le=1000)
    subscription_plan: Literal["basic", "standard", "premium"]
    payment_failures: int = Field(ge=0, le=50)
    days_since_last_login: int = Field(ge=0, le=3650)
    usage_score: float = Field(ge=0, le=1)
    contract_type: Literal["monthly", "annual", "two_year"]
    region: Literal["north", "south", "east", "west"]
