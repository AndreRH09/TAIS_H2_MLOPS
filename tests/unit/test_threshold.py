import numpy as np

from msft_mlops.features import FEATURE_COLUMNS
from msft_mlops.models import select_hyperparameters
from msft_mlops.threshold import f1_reference_and_sigma
from msft_mlops.windows import split_2021


def _ref(ds, config, seed=42):
    _, _, initial = split_2021(ds, config["split"])
    return f1_reference_and_sigma(
        "logreg", {"C": 1.0}, seed, initial, FEATURE_COLUMNS, 63, 200, 126
    )


def test_deterministic_with_same_seed(ds, config):
    assert _ref(ds, config) == _ref(ds, config)


def test_sigma_positive_and_reference_near_holdout(ds, config):
    r = _ref(ds, config)
    assert r.sigma > 0
    assert abs(r.f1_ref - r.holdout_f1) < 0.15
    assert np.isclose(r.lower_bound(2.0), r.f1_ref - 2 * r.sigma)


def test_hyperparameter_selection_uses_only_2021(ds, config):
    fit, val, _ = split_2021(ds, config["split"])
    params, _ = select_hyperparameters("logreg", fit, val, {"C": [0.01, 1.0]}, 42, FEATURE_COLUMNS)
    assert params["C"] in (0.01, 1.0)
    assert fit.index.max() < val.index.min() < ds.loc["2022-01-01":].index.min()
    assert val.index.max() < ds.loc["2022-01-01":].index.min()
