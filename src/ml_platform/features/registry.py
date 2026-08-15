from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class FeatureMetadata:
    feature_name: str
    entity: str
    data_type: str
    version: str
    description: str
    owner: str
    created_at: str = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
