import numpy as np

from msft_mlops.metrics import window_scores


def test_basic_scores():
    s = window_scores([1, 1, 0, 0], [1, 0, 1, 0])
    assert s["precision"] == 0.5 and s["recall"] == 0.5 and s["f1"] == 0.5


def test_no_positive_predictions_is_undefined_not_zero():
    s = window_scores([1, 0, 1], [0, 0, 0])
    assert np.isnan(s["precision"]) and s["precision_undefined"]
    assert s["recall"] == 0.0
    assert np.isnan(s["f1"]) and s["f1_undefined"]


def test_no_positive_true_is_undefined():
    s = window_scores([0, 0], [1, 0])
    assert np.isnan(s["recall"]) and s["recall_undefined"]
