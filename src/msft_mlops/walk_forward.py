"""Bucle walk-forward por réplica (FR-009 a FR-018)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .baselines import (
    BASELINES,
    predict_estratificado,
    predict_persistencia,
    predict_siempre_sube,
)
from .config import Config
from .drift import detect_drift
from .metrics import window_scores
from .models import fit_model, predict, select_hyperparameters
from .policies import make_policies
from .threshold import F1Reference, f1_reference_and_sigma
from .tracking import NullTracker
from .windows import Window, last_year_training, split_2021, test_windows

GROUPS = ("A", "B", "C")


@dataclass
class ModelVersion:
    group: str
    number: int
    model: Any
    reason: str
    train: pd.DataFrame
    ref: F1Reference
    params: dict
    created_after_window: str | None
    used_from_window: str | None = None


def _train_version(
    group, number, reason, train_df, replica, params, cfg: Config, feature_cols, created_after
) -> ModelVersion:
    trig = cfg["f1_trigger"]
    ref = f1_reference_and_sigma(
        replica,
        params,
        cfg.seed,
        train_df,
        feature_cols,
        int(trig["holdout_rows"]),
        int(trig["n_bootstrap"]),
        int(trig["resample_size"]),
    )
    model = fit_model(replica, params, cfg.seed, train_df[feature_cols], train_df["y"])
    return ModelVersion(group, number, model, reason, train_df, ref, params, created_after)


def run_replica(
    replica: str, ds: pd.DataFrame, cfg: Config, tracker=None
) -> dict[str, pd.DataFrame]:
    tracker = tracker or NullTracker()
    feature_cols = [c for c in ds.columns if c != "y"]
    split = cfg["split"]
    fit_df, val_df, initial_df = split_2021(ds, split)
    windows: list[Window] = test_windows(ds, split)
    params, val_f1 = select_hyperparameters(
        replica, fit_df, val_df, cfg["models"][replica], cfg.seed, feature_cols
    )
    k_sigma = float(cfg["f1_trigger"]["k_sigma"])
    window_rows = int(cfg["retrain"]["window_rows"])
    alpha = float(cfg["drift"]["alpha"])
    holdout_rows = int(cfg["f1_trigger"]["holdout_rows"])
    policies = make_policies(k_sigma)

    tracker.start_replica(
        replica,
        {
            "seed": cfg.seed,
            "data_sha256": cfg.data_sha256,
            "hyperparams": json.dumps(params, sort_keys=True),
            "val_f1": val_f1,
            "k_sigma": k_sigma,
            "alpha": alpha,
            "window_rows": window_rows,
        },
    )
    # Mismo modelo inicial para A, B y C (Principio III): se entrena una vez con todo 2021.
    initial = _train_version(
        "A", 1, "inicial", initial_df, replica, params, cfg, feature_cols, None
    )
    current: dict[str, ModelVersion] = {}
    all_versions: list[ModelVersion] = []
    for g in GROUPS:
        v = ModelVersion(
            g,
            1,
            initial.model,
            "inicial",
            initial.train,
            initial.ref,
            params,
            None,
            windows[0].window_id,
        )
        current[g] = v
        all_versions.append(v)
        tracker.register_version(g, 1, v.model, {"reason": "inicial"})

    p_up = float(initial_df["y"].mean())
    rng = np.random.default_rng(cfg.seed)
    metric_rows: list[dict] = []
    drift_rows: list[dict] = []

    for i, w in enumerate(windows):
        x_w, y_w = w.data[feature_cols], w.data["y"].to_numpy()
        new_versions: dict[str, ModelVersion] = {}
        for g in GROUPS:
            v = current[g]
            scores = window_scores(y_w, predict(v.model, x_w))
            drift = detect_drift(v.train[feature_cols], x_w, alpha)
            reason = policies[g].should_retrain(scores["f1"], drift, v.ref)
            metric_rows.append(
                {
                    "replica": replica,
                    "group": g,
                    "window_id": w.window_id,
                    "n": w.n,
                    "version": v.number,
                    **scores,
                    "drift_detected": drift.drifted,
                    "drift_min_p": drift.min_p,
                    "drift_threshold": drift.threshold,
                    "retrain_triggered": reason is not None,
                    "retrain_reason": reason or "",
                }
            )
            for feat, p in drift.per_feature.items():
                drift_rows.append(
                    {
                        "replica": replica,
                        "group": g,
                        "window_id": w.window_id,
                        "version": v.number,
                        "feature": feat,
                        "p_value": p,
                        "threshold": drift.threshold,
                        "drifted": bool(p < drift.threshold),
                    }
                )
            tracker.log_window(
                g,
                w.window_id,
                {k: scores[k] for k in ("precision", "recall", "f1")},
                {"version": v.number, "drift": drift.drifted, "retrain_reason": reason or ""},
            )
            if reason is not None:
                train = last_year_training(ds, w, window_rows)
                new_versions[g] = _train_version(
                    g, v.number + 1, reason, train, replica, params, cfg, feature_cols, w.window_id
                )
        # Baselines: mismas métricas y ventanas.
        for b in BASELINES:
            if b == "siempre_sube":
                pred = predict_siempre_sube(w.n)
            elif b == "persistencia":
                pred = predict_persistencia(w.data)
            else:
                pred = predict_estratificado(w.n, p_up, rng)
            scores = window_scores(y_w, pred)
            metric_rows.append(
                {
                    "replica": replica,
                    "group": b,
                    "window_id": w.window_id,
                    "n": w.n,
                    "version": "",
                    **scores,
                    "drift_detected": "",
                    "drift_min_p": "",
                    "drift_threshold": "",
                    "retrain_triggered": False,
                    "retrain_reason": "",
                }
            )
            tracker.log_window(
                b, w.window_id, {k: scores[k] for k in ("precision", "recall", "f1")}, {}
            )
        # La nueva versión rige desde la ventana siguiente, nunca en la que la disparó.
        used_from = windows[i + 1].window_id if i + 1 < len(windows) else None
        for g, nv in new_versions.items():
            nv.used_from_window = used_from
            current[g] = nv
            all_versions.append(nv)
            tracker.register_version(
                g,
                nv.number,
                nv.model,
                {
                    "reason": nv.reason,
                    "created_after": w.window_id,
                    "train_start": nv.train.index.min().date(),
                    "train_end": nv.train.index.max().date(),
                },
            )

    tracker.end_replica()
    version_rows = [
        {
            "replica": replica,
            "group": v.group,
            "version": v.number,
            "created_after_window": v.created_after_window or "",
            "used_from_window": v.used_from_window or "",
            "reason": v.reason,
            "train_start": v.train.index.min().date(),
            "train_end": v.train.index.max().date(),
            "n_train": len(v.train),
            "holdout_start": v.train.index[-holdout_rows].date(),
            "f1_ref": v.ref.f1_ref,
            "sigma": v.ref.sigma,
            "holdout_f1": v.ref.holdout_f1,
            "val_f1_hyperparam_selection": val_f1 if v.number == 1 else "",
            "hyperparams": json.dumps(v.params, sort_keys=True),
        }
        for v in all_versions
    ]
    return {
        "window_metrics": pd.DataFrame(metric_rows),
        "model_versions": pd.DataFrame(version_rows),
        "drift_details": pd.DataFrame(drift_rows),
    }
