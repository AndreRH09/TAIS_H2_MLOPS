from msft_mlops.drift import DriftResult
from msft_mlops.policies import PolicyA, PolicyB, PolicyC
from msft_mlops.threshold import F1Reference

REF = F1Reference(f1_ref=0.60, sigma=0.05, holdout_f1=0.6, n_undefined=0)  # umbral = 0.50
NO_DRIFT = DriftResult(False, 0.5, 0.0055, {})
DRIFT = DriftResult(True, 0.0001, 0.0055, {})


def test_a_never_retrains():
    assert PolicyA("A").should_retrain(0.0, DRIFT, REF) is None


def test_c_always_retrains():
    assert PolicyC("C").should_retrain(0.9, NO_DRIFT, REF) == "periodico"


def test_b_rules():
    p = PolicyB("B", 2.0)
    assert p.should_retrain(0.55, NO_DRIFT, REF) is None
    assert p.should_retrain(0.55, DRIFT, REF) == "deriva"
    assert p.should_retrain(0.45, NO_DRIFT, REF) == "caida_f1"
    assert p.should_retrain(0.45, DRIFT, REF) == "deriva+caida_f1"
    assert p.should_retrain(0.50, NO_DRIFT, REF) is None  # estrictamente menor


def test_b_undefined_f1_does_not_trigger_alone():
    assert PolicyB("B", 2.0).should_retrain(float("nan"), NO_DRIFT, REF) is None
