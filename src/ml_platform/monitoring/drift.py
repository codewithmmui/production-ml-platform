from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import ks_2samp


@dataclass(frozen=True)
class DriftConfig:
    numeric_ks_pvalue: float = 0.01
    numeric_psi: float = 0.20
    categorical_js: float = 0.10
    minimum_drifted_features: int = 2


def population_stability_index(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    ref = reference.dropna().to_numpy()
    cur = current.dropna().to_numpy()
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    ref_hist = np.histogram(ref, bins=edges)[0] / max(len(ref), 1)
    cur_hist = np.histogram(cur, bins=edges)[0] / max(len(cur), 1)
    ref_hist, cur_hist = np.clip(ref_hist, 1e-6, None), np.clip(cur_hist, 1e-6, None)
    return float(np.sum((cur_hist - ref_hist) * np.log(cur_hist / ref_hist)))


def detect_drift(
    reference: pd.DataFrame, current: pd.DataFrame, config: DriftConfig | None = None
) -> dict[str, object]:
    config = config or DriftConfig()
    details: dict[str, dict[str, float | bool]] = {}
    drifted: list[str] = []
    common = sorted((set(reference.columns) & set(current.columns)) - {"customer_id", "churned"})
    for feature in common:
        if pd.api.types.is_numeric_dtype(reference[feature]):
            pvalue = float(ks_2samp(reference[feature].dropna(), current[feature].dropna()).pvalue)
            psi = population_stability_index(reference[feature], current[feature])
            flag = pvalue < config.numeric_ks_pvalue and psi >= config.numeric_psi
            details[feature] = {"ks_pvalue": pvalue, "psi": psi, "drifted": flag}
        else:
            categories = sorted(set(reference[feature].dropna()) | set(current[feature].dropna()))
            p = (
                reference[feature]
                .value_counts(normalize=True)
                .reindex(categories, fill_value=0)
                .to_numpy()
                + 1e-9
            )
            q = (
                current[feature]
                .value_counts(normalize=True)
                .reindex(categories, fill_value=0)
                .to_numpy()
                + 1e-9
            )
            js = float(jensenshannon(p, q) ** 2)
            flag = js >= config.categorical_js
            details[feature] = {"js_divergence": js, "drifted": flag}
        if flag:
            drifted.append(feature)
    return {
        "drift_detected": len(drifted) >= config.minimum_drifted_features,
        "drifted_features": drifted,
        "features": details,
    }
