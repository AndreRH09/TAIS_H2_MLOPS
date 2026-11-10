"""Tests para la evaluación del tramo reciente."""

from msft_mlops.recent_evaluation import evaluate_recent_slice


def test_evaluate_recent_slice_runs(ds, config):
    df_results, md_content = evaluate_recent_slice(config, ds)
    assert len(df_results) == 7  # 3 baselines + 2 modelos x 2 réplicas
    assert set(df_results["replica"]) == {"baseline", "logreg", "rf"}
    assert "F1" in md_content
    assert "Regresión Logística" in md_content
    assert (df_results["f1"] >= 0).all()
    assert (df_results["f1"] <= 1).all()
