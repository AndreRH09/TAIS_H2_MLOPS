from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from msft_mlops.config import load_config
from msft_mlops.data import load_raw
from msft_mlops.features import build_dataset

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def config():
    return load_config(ROOT / "config" / "experiment.toml")


@pytest.fixture(scope="session")
def raw(config):
    return load_raw(config)


@pytest.fixture(scope="session")
def ds(raw, config):
    f = config["features"]
    return build_dataset(raw, f["n_lags"], tuple(f["ma_windows"]), f["vol_ma_window"])


def fast_config(config):
    """Config con grids y bootstrap reducidos para tests rápidos (misma lógica, menos cómputo)."""
    import copy
    import dataclasses

    raw = copy.deepcopy(config.raw)
    raw["models"] = {
        "logreg": {"C": [1.0]},
        "rf": {"n_estimators": [20], "max_depth": [3], "min_samples_leaf": [5]},
    }
    raw["f1_trigger"]["n_bootstrap"] = 100
    return dataclasses.replace(config, raw=raw)


def synthetic_prices(n: int = 900, seed: int = 0, shift_at: int | None = None) -> pd.DataFrame:
    """Serie sintética de precios con cambio de régimen opcional (para tests rápidos)."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2021-02-04", periods=n)
    drift = np.full(n, 0.0004)
    vol = np.full(n, 0.012)
    if shift_at is not None:
        drift[shift_at:] = -0.0008
        vol[shift_at:] = 0.03
    ret = rng.normal(drift, vol)
    close = 230 * np.exp(np.cumsum(ret))
    volume = rng.integers(15_000_000, 40_000_000, n) * (1 + (np.arange(n) > (shift_at or n)) * 1.5)
    return pd.DataFrame(
        {
            "date": dates,
            "close": close,
            "open": close * (1 + rng.normal(0, 0.002, n)),
            "high": close * 1.01,
            "low": close * 0.99,
            "volume": volume.astype(int),
        }
    )
