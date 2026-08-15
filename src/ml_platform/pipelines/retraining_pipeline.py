from pathlib import Path

import pandas as pd

from ml_platform.monitoring.drift import DriftConfig, detect_drift
from ml_platform.training.train import train_and_save


def run_retraining_pipeline(
    reference_path: Path, current_path: Path, output_dir: Path, config: DriftConfig | None = None
) -> dict[str, object]:
    reference, current = pd.read_csv(reference_path), pd.read_csv(current_path)
    report = detect_drift(reference, current, config)
    if not report["drift_detected"]:
        return {"status": "stopped", "reason": "drift_below_threshold", "drift": report}
    candidate = train_and_save(current_path, output_dir)
    return {
        "status": "candidate_evaluated",
        "drift": report,
        "candidate": candidate,
        "promotion": candidate["promotion"],
    }
