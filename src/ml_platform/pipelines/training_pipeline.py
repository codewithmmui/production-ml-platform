from pathlib import Path

from ml_platform.training.train import train_and_save


def run_training_pipeline(data_path: Path, output_dir: Path) -> dict[str, object]:
    return train_and_save(data_path, output_dir)
