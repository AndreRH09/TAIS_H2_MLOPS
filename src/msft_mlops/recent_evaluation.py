"""Evaluación exploratoria del tramo reciente (julio 2025 - enero 2026).

Compara el modelo inicial (2021, grupo A) con un modelo reentrenado con el último año
disponible. Es un análisis **posterior** al diseño: no figura en la spec ni en los umbrales
fijados para SC-008, y **no** aporta evidencia independiente del walk-forward:

- 2025-07-01 … 2025-12-31 es la ventana 2025-H2, ya evaluada por ``msft-mlops run``;
- con los valores por defecto, el conjunto de reentrenamiento (252 filas hasta 2025-06-27) es
  el mismo con el que B y C se reentrenaron tras 2025-H1 (``last_year_training``);
- incluye 2026-01, el tramo que la spec excluye de métricas, disparadores y comparaciones.

El informe Markdown declara estas tres condiciones con los tamaños calculados a partir de los
datos. Los hiperparámetros se eligen con el mismo procedimiento que el walk-forward (ajuste
feb-sep 2021, validación oct-dic 2021); no se fijan a mano.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from .baselines import predict_estratificado, predict_persistencia, predict_siempre_sube
from .config import Config, load_config
from .data import load_raw
from .features import build_dataset
from .metrics import window_scores
from .models import fit_model, predict, select_hyperparameters
from .windows import last_year_training, split_2021, test_windows

REPLICA_NAMES = {"logreg": "Regresión Logística", "rf": "Random Forest"}


def _record(replica, model_type, training_period, n_train, n_test, scores) -> dict:
    return {
        "replica": replica,
        "model_type": model_type,
        "training_period": training_period,
        "n_train": n_train,
        "n_test": n_test,
        "f1": scores["f1"],
        "precision": scores["precision"],
        "recall": scores["recall"],
    }


def _period(df: pd.DataFrame) -> str:
    return f"{df.index[0]:%Y-%m-%d} a {df.index[-1]:%Y-%m-%d}"


def _fmt(x: float) -> str:
    return "n/d" if math.isnan(x) else f"{x:.3f}"


def delta_sentence(name: str, diff: float) -> str:
    """Frase con el signo real de ``F1_reentrenado − F1_estático``."""
    if math.isnan(diff):
        return f"- En **{name}**, la diferencia de F1 no está definida (F1 indefinido)."
    if diff == 0:
        return f"- En **{name}**, el reentrenamiento no cambió el F1."
    verb = "mejoró" if diff > 0 else "empeoró"
    return (
        f"- En **{name}**, el modelo reentrenado {verb} el F1 en **{diff:+.3f}** "
        f"({diff * 100:+.1f} puntos porcentuales) frente al estático."
    )


def evaluate_recent_slice(
    config: Config,
    ds: pd.DataFrame,
    test_start: str = "2025-07-01",
    test_end: str = "2026-01-30",
    train_recent_end: str = "2025-06-27",
    window_rows: int | None = None,
) -> tuple[pd.DataFrame, str]:
    """Evalúa el modelo estático (2021) frente al reentrenado (último año) en el tramo reciente."""
    feat_cols = [c for c in ds.columns if c != "y"]
    split = config["split"]
    if window_rows is None:
        window_rows = int(config["retrain"]["window_rows"])

    # 1. Conjunto inicial (todo 2021) y selección de hiperparámetros, igual que el walk-forward.
    fit_df, val_df, train_initial = split_2021(ds, split)

    # 2. Reentrenamiento: último año hasta train_recent_end (antes de test_start).
    train_recent = ds.loc[:train_recent_end].iloc[-window_rows:]

    # 3. Tramo de prueba.
    test_slice = ds.loc[test_start:test_end]
    x_test, y_test = test_slice[feat_cols], test_slice["y"]
    n_days = len(test_slice)
    p_up_2021 = float(train_initial["y"].mean())

    records = [
        _record(
            "baseline",
            "Siempre Sube",
            "Heurística (dummy)",
            0,
            n_days,
            window_scores(y_test, predict_siempre_sube(n_days)),
        ),
        _record(
            "baseline",
            "Persistencia",
            "Heurística (signo ret_0)",
            0,
            n_days,
            window_scores(y_test, predict_persistencia(test_slice)),
        ),
        _record(
            "baseline",
            "Estratificado",
            f"Proporción 2021 ({p_up_2021:.3f})",
            0,
            n_days,
            window_scores(
                y_test, predict_estratificado(n_days, p_up_2021, np.random.default_rng(config.seed))
            ),
        ),
    ]

    hyperparams: dict[str, dict] = {}
    for replica in config.replicas:
        params, _ = select_hyperparameters(
            replica, fit_df, val_df, config["models"][replica], config.seed, feat_cols
        )
        hyperparams[replica] = params
        m_static = fit_model(
            replica, params, config.seed, train_initial[feat_cols], train_initial["y"]
        )
        records.append(
            _record(
                replica,
                "Grupo A (Estático)",
                f"2021 ({_period(train_initial)})",
                len(train_initial),
                n_days,
                window_scores(y_test, predict(m_static, x_test)),
            )
        )
        m_recent = fit_model(
            replica, params, config.seed, train_recent[feat_cols], train_recent["y"]
        )
        records.append(
            _record(
                replica,
                "Grupo B/C (Reentrenado 1 año)",
                f"Último año ({_period(train_recent)})",
                len(train_recent),
                n_days,
                window_scores(y_test, predict(m_recent, x_test)),
            )
        )

    df = pd.DataFrame(records)
    md = _markdown(
        df, config, ds, test_slice, train_recent, window_rows, hyperparams, test_start, test_end
    )
    return df, md


def _markdown(
    df: pd.DataFrame,
    config: Config,
    ds: pd.DataFrame,
    test_slice: pd.DataFrame,
    train_recent: pd.DataFrame,
    window_rows: int,
    hyperparams: dict[str, dict],
    test_start: str,
    test_end: str,
) -> str:
    split = config["split"]
    n_days = len(test_slice)
    y_test = test_slice["y"]

    # Solapamiento con el walk-forward y con el tramo excluido por la spec.
    wf_end = pd.Timestamp(split["test_end"])
    windows = test_windows(ds, split)
    in_wf = [w.window_id for w in windows if w.end >= test_slice.index[0] and w.start <= wf_end]
    n_in_wf = int((test_slice.index <= wf_end).sum())
    n_tail = n_days - n_in_wf
    # Ventana tras cuyo cierre B y C se reentrenan justo antes del tramo, y la que la sigue.
    n_prior = sum(1 for w in windows if w.end < test_slice.index[0])
    same_train = 0 < n_prior < len(windows) and last_year_training(
        ds, windows[n_prior - 1], window_rows
    ).index.equals(train_recent.index)

    md = [
        "# Evaluación exploratoria del tramo reciente: julio 2025 a enero 2026\n",
        f"- **Periodo evaluado:** `{test_start}` a `{test_end}` ({n_days} días bursátiles)",
        f"- **Periodo de reentrenamiento:** `{train_recent.index[0]:%Y-%m-%d}` a "
        f"`{train_recent.index[-1]:%Y-%m-%d}` ({len(train_recent)} días bursátiles)",
        f"- **Subidas reales en el tramo:** `{int(y_test.sum())} de {n_days}` "
        f"({y_test.mean() * 100:.1f} %)",
        "- **Hiperparámetros** (selección con 2021, mismo procedimiento que el walk-forward): "
        + "; ".join(f"{r} `{json.dumps(p, sort_keys=True)}`" for r, p in hyperparams.items())
        + "\n",
        "## Alcance\n",
        "Análisis **exploratorio y posterior al diseño**: no está en la spec, no tiene contraste "
        "estadístico y no es una prueba independiente del walk-forward.\n",
        f"- {n_in_wf} de {n_days} días pertenecen a ventanas ya evaluadas por `msft-mlops run` "
        f"({', '.join(in_wf) or 'ninguna'}).",
        f"- {n_tail} días son posteriores a `test_end` ({split['test_end']}), el tramo que la "
        "spec excluye de métricas, disparadores y comparaciones.",
    ]
    if same_train:
        md.append(
            f"- El conjunto de reentrenamiento es el mismo con el que B y C se reentrenaron tras "
            f"{windows[n_prior - 1].window_id}; el modelo «reentrenado» es el que el walk-forward "
            f"ya usó en {windows[n_prior].window_id}."
        )
    md += [
        "\n## Resultados\n",
        "| Réplica | Configuración / Modelo | Periodo de Entrenamiento | F1 | Precision | Recall |",
        "|---|---|---|:---:|:---:|:---:|",
    ]
    for r in df.itertuples():
        md.append(
            f"| {r.replica} | {r.model_type} | {r.training_period} | "
            f"{_fmt(r.f1)} | {_fmt(r.precision)} | {_fmt(r.recall)} |"
        )

    md.append("\n## Lectura\n")
    for replica in [r for r in df["replica"].unique() if r != "baseline"]:
        sub = df[df["replica"] == replica].set_index("model_type")["f1"]
        diff = float(sub["Grupo B/C (Reentrenado 1 año)"] - sub["Grupo A (Estático)"])
        md.append(delta_sentence(REPLICA_NAMES.get(replica, replica), diff))

    up = float(df.loc[df["model_type"] == "Siempre Sube", "f1"].iloc[0])
    sup = df[df["replica"] != "baseline"].dropna(subset=["f1"])
    if len(sup):
        best = sup.loc[sup["f1"].idxmax()]
        name = f"{REPLICA_NAMES.get(best['replica'], best['replica'])}, {best['model_type']}"
        if best["f1"] < up:
            md.append(
                f"- Ningún modelo supervisado supera al baseline «siempre sube» (F1 = {up:.3f}); "
                f"el mejor es {name} (F1 = {best['f1']:.3f})."
            )
        else:
            md.append(
                f"- El mejor modelo supervisado ({name}, F1 = {best['f1']:.3f}) iguala o supera "
                f"al baseline «siempre sube» (F1 = {up:.3f})."
            )
    md.append(
        "- Con F1 de la clase «sube», predecir siempre 1 obtiene recall = 1; un F1 alto con "
        "recall alto puede reflejar sesgo alcista más que capacidad predictiva."
    )
    return "\n".join(md) + "\n"


def run_recent_evaluation(
    config_path: str | Path = "config/experiment.toml",
    results_dir: str | Path = "results",
    reports_dir: str | Path = "reports",
) -> pd.DataFrame:
    cfg = load_config(config_path)
    raw = load_raw(cfg)
    f = cfg["features"]
    ds = build_dataset(raw, f["n_lags"], tuple(f["ma_windows"]), f["vol_ma_window"])
    df, md_content = evaluate_recent_slice(cfg, ds)

    results_dir = Path(results_dir)
    reports_dir = Path(reports_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    csv_path = results_dir / "recent_slice_metrics.csv"
    df.to_csv(csv_path, index=False, lineterminator="\n")

    report_path = reports_dir / "evaluacion_tramo_reciente.md"
    report_path.write_text(md_content, encoding="utf-8")
    print(f"[recent] resultados escritos en {csv_path} y {report_path}")
    return df
