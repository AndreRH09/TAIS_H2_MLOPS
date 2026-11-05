import pandas as pd
import pytest

from conftest import fast_config, synthetic_prices
from msft_mlops.features import build_dataset
from msft_mlops.walk_forward import run_replica
from msft_mlops.windows import last_year_training
from msft_mlops.windows import test_windows as make_windows


@pytest.fixture(scope="module")
def synth(config):
    cfg = fast_config(config)
    ds = build_dataset(synthetic_prices(n=1150, seed=3, shift_at=520))
    return cfg, ds


@pytest.fixture(scope="module", params=["logreg", "rf"])
def out(request, synth):
    cfg, ds = synth
    return run_replica(request.param, ds, cfg)


def _g(out_, g):
    wm = out_["window_metrics"]
    return wm[wm["group"] == g].reset_index(drop=True)


def test_all_groups_and_baselines_each_window(out):
    wm = out["window_metrics"]
    n_windows = wm["window_id"].nunique()
    assert n_windows >= 6
    assert set(wm["group"]) == {"A", "B", "C", "siempre_sube", "persistencia", "estratificado"}
    assert (wm.groupby("group").size() == n_windows).all()


def test_a_never_changes(out):
    a = _g(out, "A")
    assert (a["version"] == 1).all() and not a["retrain_triggered"].any()


def test_c_retrains_every_window_and_versions_advance(out):
    c = _g(out, "C")
    assert c["retrain_triggered"].all()
    assert c["version"].tolist() == list(range(1, len(c) + 1))
    assert (c["retrain_reason"] == "periodico").all()


def test_new_version_used_only_from_next_window(out):
    b = _g(out, "B")
    assert b.loc[0, "version"] == 1
    for i in range(1, len(b)):
        expected = b.loc[i - 1, "version"] + int(bool(b.loc[i - 1, "retrain_triggered"]))
        assert b.loc[i, "version"] == expected


def test_b_keeps_version_without_trigger(out):
    b = _g(out, "B")
    for i in range(len(b) - 1):
        if not b.loc[i, "retrain_triggered"]:
            assert b.loc[i + 1, "version"] == b.loc[i, "version"]


def test_b_retrain_reason_consistent(out):
    for r in _g(out, "B").itertuples():
        if r.retrain_triggered:
            assert r.retrain_reason in {"deriva", "caida_f1", "deriva+caida_f1"}
        else:
            assert r.retrain_reason == "" or pd.isna(r.retrain_reason)


def test_b_detects_regime_shift(out):
    assert _g(out, "B")["retrain_triggered"].any()


def test_training_never_includes_future_data(out, synth):
    cfg, ds = synth
    windows = {w.window_id: w for w in make_windows(ds, cfg["split"])}
    mv = out["model_versions"]
    for r in mv[mv["version"] > 1].itertuples():
        w = windows[r.created_after_window]
        assert pd.Timestamp(r.train_end) < w.end
        expected = last_year_training(ds, w, 252)
        assert pd.Timestamp(r.train_start) == expected.index.min()
        assert r.n_train == 252


def test_last_window_retrain_registered_but_unused(out):
    mv, wm = out["model_versions"], out["window_metrics"]
    last = wm["window_id"].max()
    for r in mv[mv["created_after_window"] == last].itertuples():
        assert pd.isna(r.used_from_window) or r.used_from_window == ""


def test_same_initial_model_for_all_groups(out):
    mv = out["model_versions"]
    v1 = mv[mv["version"] == 1]
    assert v1["f1_ref"].nunique() == 1 and v1["hyperparams"].nunique() == 1
    wm = out["window_metrics"]
    first = wm[wm["window_id"] == wm["window_id"].min()].set_index("group")
    f1s = [first.loc[g, "f1"] for g in "ABC"]
    assert f1s[0] == f1s[1] == f1s[2] or any(pd.isna(x) for x in f1s)


def test_reproducible_on_synthetic(synth):
    cfg, ds = synth
    a = run_replica("logreg", ds, cfg)
    b = run_replica("logreg", ds, cfg)
    for name in a:
        pd.testing.assert_frame_equal(a[name], b[name])
