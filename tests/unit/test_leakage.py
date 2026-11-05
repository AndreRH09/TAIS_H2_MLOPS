"""FR-006 / SC-004 / Principio I: las features de t no usan información posterior a t."""

import numpy as np

from msft_mlops.features import FEATURE_COLUMNS, build_dataset


def test_truncating_future_does_not_change_features(raw):
    full = build_dataset(raw)
    for t in [300, 600, 900, 1200]:
        trunc = build_dataset(raw.iloc[: t + 2])  # +2: la fila t necesita close_{t+1} solo para y
        common = trunc.index.intersection(full.index)
        assert len(common) > 0
        a = trunc.loc[common, FEATURE_COLUMNS].to_numpy()
        b = full.loc[common, FEATURE_COLUMNS].to_numpy()
        assert np.allclose(a, b)


def test_perturbing_future_prices_leaves_past_features_unchanged(raw):
    base = build_dataset(raw)
    t = 700
    pert = raw.copy()
    pert["volume"] = pert["volume"].astype(float)
    pert.loc[t + 1 :, ["close", "volume"]] = pert.loc[t + 1 :, ["close", "volume"]] * 3.7
    out = build_dataset(pert)
    cutoff = raw["date"].iloc[t]
    past = base.loc[:cutoff, FEATURE_COLUMNS]
    assert np.allclose(past.to_numpy(), out.loc[past.index, FEATURE_COLUMNS].to_numpy())


def test_no_feature_equals_label_and_label_uses_next_close(ds):
    for c in FEATURE_COLUMNS:
        assert not (ds[c] == ds["y"]).all()
        assert abs(np.corrcoef(ds[c], ds["y"])[0, 1]) < 0.5


def test_label_shift_is_forward(raw):
    out = build_dataset(raw)
    close = raw.set_index("date")["close"]
    t = out.index[100]
    nxt = close.index[close.index.get_loc(t) + 1]
    assert out.loc[t, "y"] == int(close[nxt] > close[t])
