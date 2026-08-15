import pandas as pd

from ml_platform.features.offline_store import InMemoryOfflineStore
from ml_platform.features.online_store import InMemoryOnlineStore


def test_in_memory_feature_stores() -> None:
    offline = InMemoryOfflineStore()
    frame = pd.DataFrame({"customer_id": ["C-1"], "score": [0.5]})
    offline.write_offline_features(frame)
    assert offline.read_offline_features().equals(frame)
    online = InMemoryOnlineStore()
    online.write_online_features("C-1", {"score": 0.5})
    assert online.read_online_features("C-1") == {"score": 0.5}
    assert online.read_online_features("missing") is None
