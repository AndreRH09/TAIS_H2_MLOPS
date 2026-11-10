import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from msft_mlops.drift import detect_drift


def _frames(shift: float, seed: int = 1):
    rng = np.random.default_rng(seed)
    cols = [f"f{i}" for i in range(9)]
    ref = pd.DataFrame(rng.normal(size=(250, 9)), columns=cols)
    cur = pd.DataFrame(rng.normal(size=(126, 9)), columns=cols)
    cur["f3"] += shift
    return ref, cur


def test_matches_scipy_and_bonferroni_rule():
    for shift in (0.0, 0.2, 0.8):
        ref, cur = _frames(shift)
        res = detect_drift(ref, cur, alpha=0.05)
        scipy_p = {c: ks_2samp(ref[c], cur[c]).pvalue for c in ref.columns}
        for c in ref.columns:
            assert np.isclose(res.per_feature[c], scipy_p[c])
        assert np.isclose(res.threshold, 0.05 / 9)
        assert res.drifted == (min(scipy_p.values()) < 0.05 / 9)


def test_detects_strong_shift_and_not_none():
    assert detect_drift(*_frames(1.5)).drifted
    assert not detect_drift(*_frames(0.0, seed=7)).drifted


def test_reports_all_k_pvalues():
    ref, cur = _frames(0.5)
    res = detect_drift(ref, cur)
    assert len(res.per_feature) == 9 and res.min_p == min(res.per_feature.values())
