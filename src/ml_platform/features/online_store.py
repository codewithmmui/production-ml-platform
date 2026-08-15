import json
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import redis

from ml_platform.core.exceptions import FeatureStoreUnavailableError


class RedisOnlineStore:
    def __init__(self, url: str, ttl_seconds: int = 3600) -> None:
        self.client = redis.Redis.from_url(url, decode_responses=True, socket_timeout=1)
        self.ttl_seconds = ttl_seconds

    def write_online_features(self, customer_id: str, features: dict[str, Any]) -> None:
        payload = {"features": features, "updated_at": datetime.now(UTC).isoformat()}
        try:
            self.client.setex(f"features:{customer_id}", self.ttl_seconds, json.dumps(payload))
        except redis.RedisError as exc:
            raise FeatureStoreUnavailableError("online feature store write failed") from exc

    def read_online_features(
        self, customer_id: str, max_age_seconds: int = 3600
    ) -> dict[str, Any] | None:
        try:
            value = self.client.get(f"features:{customer_id}")
        except redis.RedisError as exc:
            raise FeatureStoreUnavailableError("online feature store read failed") from exc
        if value is None:
            return None
        payload = json.loads(cast(str, value))
        updated = datetime.fromisoformat(payload["updated_at"])
        if datetime.now(UTC) - updated > timedelta(seconds=max_age_seconds):
            return None
        return dict(payload["features"])


class InMemoryOnlineStore:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def write_online_features(self, customer_id: str, features: dict[str, Any]) -> None:
        self.values[customer_id] = dict(features)

    def read_online_features(
        self, customer_id: str, max_age_seconds: int = 3600
    ) -> dict[str, Any] | None:
        del max_age_seconds
        value = self.values.get(customer_id)
        return dict(value) if value else None
