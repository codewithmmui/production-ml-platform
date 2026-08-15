from typing import Protocol

import pandas as pd
from sqlalchemy import create_engine


class OfflineFeatureStore(Protocol):
    def write_offline_features(self, frame: pd.DataFrame) -> None: ...
    def read_offline_features(self) -> pd.DataFrame: ...


class PostgresOfflineStore:
    def __init__(self, database_url: str, table: str = "customer_features") -> None:
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.table = table

    def write_offline_features(self, frame: pd.DataFrame) -> None:
        frame.to_sql(self.table, self.engine, if_exists="append", index=False, method="multi")

    def read_offline_features(self) -> pd.DataFrame:
        return pd.read_sql_table(self.table, self.engine)


class InMemoryOfflineStore:
    def __init__(self) -> None:
        self.frame = pd.DataFrame()

    def write_offline_features(self, frame: pd.DataFrame) -> None:
        self.frame = frame.copy()

    def read_offline_features(self) -> pd.DataFrame:
        return self.frame.copy()
