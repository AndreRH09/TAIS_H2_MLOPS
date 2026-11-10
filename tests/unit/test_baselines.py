import numpy as np

from msft_mlops.baselines import predict_estratificado, predict_persistencia, predict_siempre_sube


def test_siempre_sube():
    assert predict_siempre_sube(5).tolist() == [1] * 5


def test_persistencia(ds):
    w = ds.iloc[:50]
    assert (predict_persistencia(w) == (w["ret_0"] > 0).astype(int)).all()


def test_estratificado_deterministic_and_proportion():
    a = predict_estratificado(5000, 0.55, np.random.default_rng(3))
    b = predict_estratificado(5000, 0.55, np.random.default_rng(3))
    assert (a == b).all()
    assert abs(a.mean() - 0.55) < 0.03
