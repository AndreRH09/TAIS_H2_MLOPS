import numpy as np
import pandas as pd
from scipy import stats

from msft_mlops.report import compare_groups, data_driven_threats


def _wm(f1_a, f1_b, f1_c):
    rows = []
    for i in range(8):
        for g, v in (("A", f1_a), ("B", f1_b), ("C", f1_c)):
            rows.append({"replica": "logreg", "group": g, "window_id": f"w{i}", "f1": v[i]})
    return pd.DataFrame(rows)


def test_wilcoxon_matches_scipy_and_counts():
    a = [0.5, 0.52, 0.48, 0.55, 0.5, 0.47, 0.53, 0.51]
    b = [0.55, 0.50, 0.52, 0.60, 0.49, 0.52, 0.58, 0.50]
    out = compare_groups(_wm(a, b, a))
    r = out[out["comparison"] == "B-A"].iloc[0]
    d = np.array(b) - np.array(a)
    assert np.isclose(r["p_value"], stats.wilcoxon(d).pvalue)
    assert r["windows_won"] == (d > 0).sum() and r["windows_lost"] == (d < 0).sum()
    assert r["n_effective"] == 8


def test_nan_pairs_excluded_and_all_zero_ok():
    a = [0.5] * 8
    b = [0.5] * 7 + [float("nan")]
    out = compare_groups(_wm(a, b, a))
    r = out[out["comparison"] == "B-A"].iloc[0]
    assert r["n_effective"] == 7 and r["windows_tied"] == 7
    assert np.isnan(r["p_value"]) and not r["significant_at_0_05"]


def test_data_driven_threats_quantify_drift_and_f1_bias():
    wm = _wm([0.5] * 8, [0.52] * 8, [0.48] * 8)
    wm = pd.concat(
        [
            wm,
            pd.DataFrame(
                {
                    "replica": "logreg",
                    "group": "siempre_sube",
                    "window_id": [f"w{i}" for i in range(8)],
                    "f1": 0.7,
                }
            ),
        ]
    )
    drift = pd.DataFrame(
        {
            "group": ["B"] * 4 + ["A"],
            "feature": ["ma20_rel", "ma20_rel", "ret_0", "ret_0", "ret_0"],
            "drifted": [True, True, False, False, True],
        }
    )
    text = "\n".join(data_driven_threats(wm, drift))
    assert "`ma20_rel` (2/2)" in text and "ret_0" not in text  # solo grupo B y features con deriva
    assert "0.700" in text and "por encima de" in text and "(0.480–0.520)" in text
