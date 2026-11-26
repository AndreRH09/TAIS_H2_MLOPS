"""Feature 002: núcleo de la interfaz (datos subidos, modelos propios, veredicto)."""

import io
import json
import os
import zipfile

import joblib
import pandas as pd
import pytest
import skops.io as sio
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from conftest import fast_config, synthetic_prices
from msft_mlops.custom_run import (
    CustomRunError,
    ExperimentParams,
    build_config,
    build_manifest,
    example_model_bytes,
    infer_split,
    load_model_bytes,
    normalize_prices,
    results_zip,
    run_custom_experiment,
    summarize_split,
    verdict,
)
from msft_mlops.data import DataValidationError
from msft_mlops.models import make_model
from msft_mlops.windows import split_2021
from msft_mlops.windows import test_windows as make_windows

# ---------------------------------------------------------------- datos


def test_normalize_accepts_yahoo_style_columns(raw):
    yahoo = pd.DataFrame(
        {
            "Date": raw["date"].dt.strftime("%Y-%m-%d"),
            "Open": raw["open"],
            "High": raw["high"],
            "Low": raw["low"],
            "Close": raw["close"],
            "Adj Close": raw["close"] * 0.9,
            "Volume": raw["volume"],
        }
    ).iloc[::-1]  # desordenado: debe ordenarse por fecha
    out, _ = normalize_prices(yahoo)
    assert out["date"].is_monotonic_increasing
    assert (out["close"].to_numpy() == raw["close"].to_numpy()).all()  # usa Close, no Adj Close
    assert out["price_change"].isna().sum() == 1


def test_normalize_reports_missing_columns():
    with pytest.raises(CustomRunError, match="volume"):
        normalize_prices(
            pd.DataFrame(
                {"date": ["2024-01-02"], "open": [1], "high": [1], "low": [1], "close": [1]}
            )
        )


def test_normalize_rejects_incoherent_ohlc(raw):
    bad = raw[["date", "open", "high", "low", "close", "volume"]].copy()
    bad.loc[10, "high"] = bad.loc[10, "low"] - 1
    with pytest.raises(DataValidationError):
        normalize_prices(bad)


def test_infer_split_reproduces_official_partition(raw, ds, config):
    split = infer_split(raw["date"])
    official = config["split"]
    for a, b in zip(split_2021(ds, split), split_2021(ds, official), strict=True):
        assert a.index.equals(b.index)
    got = [w.window_id for w in make_windows(ds, split)]
    assert got == [w.window_id for w in make_windows(ds, official)]
    assert split["test_end"] == official["test_end"]


def test_infer_split_rejects_short_series():
    dates = pd.bdate_range("2024-01-02", periods=200)
    with pytest.raises(CustomRunError):
        infer_split(pd.Series(dates))


def test_summarize_split_warns_with_few_windows():
    raw_s, _ = normalize_prices(synthetic_prices(n=650, seed=2))
    from msft_mlops.features import build_dataset

    ds = build_dataset(raw_s)
    summary = summarize_split(ds, infer_split(raw_s["date"]), holdout_rows=63)
    assert 2 <= len(summary.window_ids) < 6
    assert summary.warnings and "Wilcoxon" in summary.warnings[0]


# ---------------------------------------------------------------- modelos


def test_skops_classifier_loads():
    model = load_model_bytes(sio.dumps(LogisticRegression(C=0.5)), "m.skops")
    assert isinstance(model, LogisticRegression) and model.C == 0.5
    assert type(load_model_bytes(example_model_bytes(), "x.skops")).__name__ == (
        "GradientBoostingClassifier"
    )


def test_skops_with_dangerous_function_is_rejected():
    evil = make_pipeline(FunctionTransformer(func=eval), LogisticRegression())
    with pytest.raises(CustomRunError, match="builtins.eval"):
        load_model_bytes(sio.dumps(evil), "evil.skops")
    with pytest.raises(CustomRunError, match="no permitidos"):
        load_model_bytes(sio.dumps(FunctionTransformer(func=os.system)), "evil.skops")


def test_pickle_rejected_unless_explicitly_allowed():
    buf = io.BytesIO()
    joblib.dump(LogisticRegression(), buf)
    with pytest.raises(CustomRunError, match="pickle"):
        load_model_bytes(buf.getvalue(), "m.joblib", allow_unsafe=False)
    assert isinstance(
        load_model_bytes(buf.getvalue(), "m.joblib", allow_unsafe=True), LogisticRegression
    )


def test_non_classifier_and_bad_format_rejected():
    with pytest.raises(CustomRunError, match="clasificador"):
        load_model_bytes(sio.dumps(LinearRegression()), "m.skops")
    with pytest.raises(CustomRunError, match="clasificador"):
        load_model_bytes(sio.dumps(StandardScaler()), "m.skops")
    with pytest.raises(CustomRunError, match="Formato"):
        load_model_bytes(b"abc", "m.txt")


def test_template_gets_experiment_seed_everywhere():
    pipe = make_pipeline(StandardScaler(), RandomForestClassifier(random_state=7))
    m = make_model("x", {}, 42, estimator=pipe)
    assert m.get_params()["randomforestclassifier__random_state"] == 42
    assert pipe.get_params()["randomforestclassifier__random_state"] == 7  # plantilla intacta


# ---------------------------------------------------------------- ejecución y veredicto


@pytest.fixture(scope="module")
def custom_run(config):
    raw_s, _ = normalize_prices(synthetic_prices(n=1150, seed=3, shift_at=520))
    split = infer_split(raw_s["date"])
    params = ExperimentParams(alpha=0.05, k_sigma=2.0, window_rows=252)
    cfg = build_config(fast_config(config), split, params, ["logreg", "arbol"])
    seen = []
    tables = run_custom_experiment(
        raw_s,
        cfg,
        [("logreg", None), ("arbol", DecisionTreeClassifier(max_depth=3))],
        on_replica=seen.append,
    )
    return cfg, tables, seen


def test_custom_run_covers_all_groups_and_replicas(custom_run):
    _, tables, seen = custom_run
    wm = tables["window_metrics"]
    assert seen == ["logreg", "arbol"]
    assert set(wm["replica"]) == {"logreg", "arbol"}
    assert set(wm["group"]) == {"A", "B", "C", "siempre_sube", "persistencia", "estratificado"}
    assert set(tables["comparisons"]["comparison"]) == {"B-A", "C-A", "B-C"}
    arbol = tables["model_versions"].query("replica == 'arbol'")
    assert (arbol["hyperparams"] == "{}").all()  # el modelo propio se usa con sus parámetros


def test_verdict_names_best_policy_and_evidence(custom_run):
    _, tables, _ = custom_run
    out = verdict(tables["window_metrics"], tables["comparisons"], tables["model_versions"])
    assert {v.replica for v in out} == {"logreg", "arbol"}
    for v in out:
        assert v.best_policy in {"A", "B", "C"}
        assert v.retrains["C"] == v.n_windows
        text = " ".join(v.lines)
        assert "F1 medio por política" in text and "siempre sube" in text


def test_verdict_flags_significance_and_b_like_c():
    rows, mv = [], []
    for i in range(8):
        for g, f1 in (("A", 0.40 + 0.001 * i), ("B", 0.60 + 0.002 * i), ("C", 0.60 + 0.002 * i)):
            rows.append(
                {
                    "replica": "r",
                    "group": g,
                    "window_id": f"w{i}",
                    "f1": f1,
                    "retrain_triggered": g != "A",
                }
            )
        rows.append(
            {
                "replica": "r",
                "group": "siempre_sube",
                "window_id": f"w{i}",
                "f1": 0.5,
                "retrain_triggered": False,
            }
        )
    for g in "BC":
        mv += [{"replica": "r", "group": g, "version": v} for v in range(1, 10)]
    wm = pd.DataFrame(rows)
    from msft_mlops.report import compare_groups

    (v,) = verdict(wm, compare_groups(wm), pd.DataFrame(mv))
    text = " ".join(v.lines)
    assert set(v.significant) == {"B-A", "C-A"}
    assert "Con alarmas (B) supera a Estático (A)" in text
    assert "casi como C" in text
    assert "supera al baseline" in text


def test_results_zip_contains_tables_and_manifest(custom_run, config):
    cfg, tables, _ = custom_run
    manifest = build_manifest(
        cfg,
        "abc",
        "subido",
        {"arbol": "DecisionTreeClassifier"},
        ExperimentParams.from_config(config),
    )
    zf = zipfile.ZipFile(io.BytesIO(results_zip(tables, manifest)))
    assert {"window_metrics.csv", "model_versions.csv", "comparisons.csv", "manifest.json"} <= set(
        zf.namelist()
    )
    data = json.loads(zf.read("manifest.json"))
    assert data["exploratory"] is True and data["seed"] == 42 and data["split"] == cfg["split"]
