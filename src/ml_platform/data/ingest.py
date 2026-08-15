from pathlib import Path

import pandas as pd

from ml_platform.data.validation import validate_dataframe


def ingest_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"dataset not found: {path}")
    return validate_dataframe(pd.read_csv(path))
