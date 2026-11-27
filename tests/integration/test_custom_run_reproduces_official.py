"""Feature 002 SC-101: la interfaz, con el dataset del proyecto y los parámetros por defecto,
reproduce los resultados oficiales de ``results/window_metrics.csv``."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from msft_mlops.custom_run import ExperimentParams, build_config, infer_split, run_custom_experiment

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.slow
def test_interface_run_matches_official_results(raw, config):
    split = infer_split(raw["date"])
    cfg = build_config(config, split, ExperimentParams.from_config(config), ["logreg"])
    got = run_custom_experiment(raw, cfg, [("logreg", None)])["window_metrics"]
    official = pd.read_csv(ROOT / "results" / "window_metrics.csv")
    official = official[official["replica"] == "logreg"].reset_index(drop=True)
    assert list(got["group"]) == list(official["group"])
    assert list(got["window_id"]) == list(official["window_id"])
    for col in ("precision", "recall", "f1"):
        assert np.allclose(got[col].astype(float), official[col].astype(float), equal_nan=True)
    exp = got[got["group"].isin(["A", "B", "C"])].reset_index(drop=True)
    off = official[official["group"].isin(["A", "B", "C"])].reset_index(drop=True)
    assert (exp["version"].astype(int) == off["version"].astype(int)).all()
    assert (exp["retrain_reason"].fillna("") == off["retrain_reason"].fillna("")).all()
