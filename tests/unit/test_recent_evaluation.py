"""Tests para la evaluación exploratoria del tramo reciente."""

from msft_mlops.recent_evaluation import delta_sentence, evaluate_recent_slice


def test_evaluate_recent_slice_runs(ds, config):
    df_results, md_content = evaluate_recent_slice(config, ds)
    assert len(df_results) == 7  # 3 baselines + 2 modelos x 2 réplicas
    assert set(df_results["replica"]) == {"baseline", "logreg", "rf"}
    assert "F1" in md_content
    assert "Regresión Logística" in md_content
    assert (df_results["f1"] >= 0).all()
    assert (df_results["f1"] <= 1).all()


def test_report_declares_overlap_with_walk_forward(ds, config):
    _, md = evaluate_recent_slice(config, ds)
    assert "exploratorio" in md
    assert "2025-H2" in md  # ventana ya evaluada por el walk-forward
    assert "tras 2025-H1" in md  # mismo conjunto de reentrenamiento que B y C
    assert f"posteriores a `test_end` ({config['split']['test_end']})" in md


def test_delta_sentence_uses_real_sign():
    assert "mejoró" in delta_sentence("X", 0.05) and "+0.050" in delta_sentence("X", 0.05)
    assert "empeoró" in delta_sentence("X", -0.05) and "-0.050" in delta_sentence("X", -0.05)
    assert "no cambió" in delta_sentence("X", 0.0)
    assert "no está definida" in delta_sentence("X", float("nan"))
