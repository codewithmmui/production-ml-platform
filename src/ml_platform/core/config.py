from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    environment: str = "development"
    log_level: str = "INFO"
    model_path: Path = Path("artifacts/model.joblib")
    model_metadata_path: Path = Path("artifacts/metadata.json")
    database_url: str = "postgresql+psycopg://mlplatform:change-me@localhost:5432/mlplatform"
    redis_url: str = "redis://localhost:6379/0"
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"
    request_timeout_seconds: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
