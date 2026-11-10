"""Escritura estable y determinista de los resultados canónicos."""

from __future__ import annotations

import hashlib
import json
import platform
from importlib import metadata
from pathlib import Path

import pandas as pd

CSV_NAMES = ("window_metrics", "model_versions", "drift_details")
_LIBS = ("scikit-learn", "pandas", "numpy", "scipy", "evidently", "mlflow")


def write_csv(df: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_results(
    tables: dict[str, pd.DataFrame], results_dir: Path, seed: int, data_sha256: str
) -> dict:
    hashes = {}
    for name in CSV_NAMES:
        hashes[f"{name}.csv"] = write_csv(tables[name], results_dir / f"{name}.csv")
    manifest = {
        "seed": seed,
        "data_sha256": data_sha256,
        "python": platform.python_version(),
        "libraries": {lib: metadata.version(lib) for lib in _LIBS},
        "csv_sha256": hashes,
    }
    (results_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest
