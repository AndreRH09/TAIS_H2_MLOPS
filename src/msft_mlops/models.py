"""Clasificadores y selección de hiperparámetros (FR-009, FR-010)."""

from __future__ import annotations

import itertools
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .metrics import f1_value

REPLICAS = ("logreg", "rf")


def make_model(replica: str, params: dict[str, Any], seed: int):
    if replica == "logreg":
        return Pipeline(
            [
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=1000, random_state=seed, **params)),
            ]
        )
    if replica == "rf":
        return RandomForestClassifier(random_state=seed, n_jobs=1, **params)
    raise ValueError(f"Réplica desconocida: {replica}")


def param_grid(grid: dict[str, list]) -> list[dict[str, Any]]:
    keys = list(grid)
    return [dict(zip(keys, values, strict=True)) for values in itertools.product(*grid.values())]


def fit_model(replica: str, params: dict[str, Any], seed: int, x: pd.DataFrame, y: pd.Series):
    model = make_model(replica, params, seed)
    model.fit(x.to_numpy(), y.to_numpy())
    return model


def predict(model, x: pd.DataFrame) -> np.ndarray:
    return model.predict(x.to_numpy())


def select_hyperparameters(
    replica: str,
    fit_df: pd.DataFrame,
    val_df: pd.DataFrame,
    grid: dict[str, list],
    seed: int,
    feature_cols: list[str],
) -> tuple[dict[str, Any], float]:
    """Elige el mejor F1 de validación. Desempate: primera combinación del grid."""
    best_params, best_f1 = None, -np.inf
    for params in param_grid(grid):
        model = fit_model(replica, params, seed, fit_df[feature_cols], fit_df["y"])
        f1 = f1_value(val_df["y"], predict(model, val_df[feature_cols]))
        score = -1.0 if np.isnan(f1) else f1
        if score > best_f1:
            best_params, best_f1 = params, score
    assert best_params is not None
    return best_params, float(best_f1)
