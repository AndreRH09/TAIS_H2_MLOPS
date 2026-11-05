"""SC-003: dos ejecuciones completas con la misma configuración dan CSV idénticos."""

from pathlib import Path

import pytest

from msft_mlops.cli import run_experiment
from msft_mlops.results_io import CSV_NAMES

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.slow
def test_full_run_twice_identical(tmp_path):
    cfg = ROOT / "config" / "experiment.toml"
    r1, r2 = tmp_path / "r1", tmp_path / "r2"
    m1 = run_experiment(cfg, r1, reports_dir=tmp_path / "rep1")
    m2 = run_experiment(cfg, r2, reports_dir=tmp_path / "rep2")
    assert m1["csv_sha256"] == m2["csv_sha256"]
    for name in (*CSV_NAMES, "comparisons"):
        assert (r1 / f"{name}.csv").read_bytes() == (r2 / f"{name}.csv").read_bytes()
    rows = (r1 / "window_metrics.csv").read_text().splitlines()
    assert len(rows) == 1 + 96  # 8 ventanas x 6 grupos x 2 réplicas
