# Feature store

`PostgresOfflineStore` writes/reads dataframe feature sets for reproducible training; `RedisOnlineStore` writes entity-keyed JSON with an update timestamp and TTL. Both expose narrow interfaces and have in-memory implementations for deterministic tests.

Feature metadata records name, entity, type, semantic version, description, creation time, and owner. Freshness is checked on reads. Training-serving skew is controlled by using `FeatureEngineer` in the serialized sklearn pipeline; the materializer and inference service must deploy the same feature version. Schema, feature version, and dataset hash are promotion inputs.
