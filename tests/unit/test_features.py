import numpy as np

from msft_mlops.features import FEATURE_COLUMNS


def test_shape_and_columns(ds, raw):
    assert len(FEATURE_COLUMNS) == 9
    assert list(ds.columns) == FEATURE_COLUMNS + ["y"]
    assert not ds.isna().any().any()
    # se descartan las 19 primeras filas (SMA20) y la última (sin etiqueta)
    assert len(ds) == len(raw) - 20


def test_label_is_next_day_direction(ds, raw):
    close = raw.set_index("date")["close"]
    expected = (close.shift(-1) > close).astype(int).reindex(ds.index)
    assert (ds["y"] == expected).all()


def test_features_are_relative(ds):
    assert ds[FEATURE_COLUMNS].abs().max().max() < 5  # nada parecido a niveles de precio


def test_ret0_matches_close(ds, raw):
    close = raw.set_index("date")["close"]
    assert np.allclose(ds["ret_0"], close.pct_change().reindex(ds.index))
