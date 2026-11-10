"""F1 de referencia y σ por bootstrap sobre un hold-out temporal (FR-013a)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .metrics import f1_value
from .models import fit_model, predict


@dataclass(frozen=True)
class F1Reference:
    f1_ref: float
    sigma: float
    holdout_f1: float
    n_undefined: int  # remuestras con F1 indefinido, excluidas

    def lower_bound(self, k_sigma: float) -> float:
        return self.f1_ref - k_sigma * self.sigma


def f1_reference_and_sigma(
    replica: str,
    params: dict,
    seed: int,
    train_df: pd.DataFrame,
    feature_cols: list[str],
    holdout_rows: int,
    n_bootstrap: int,
    resample_size: int,
) -> F1Reference:
    """Ajusta con el entrenamiento sin su hold-out (últimas ``holdout_rows`` filas), predice el
    hold-out y remuestrea pares (y, ŷ) con reemplazo para estimar media y σ del F1."""
    if len(train_df) <= holdout_rows:
        raise ValueError("El entrenamiento es más corto que el hold-out")
    head, hold = train_df.iloc[:-holdout_rows], train_df.iloc[-holdout_rows:]
    model = fit_model(replica, params, seed, head[feature_cols], head["y"])
    y_true = hold["y"].to_numpy()
    y_pred = predict(model, hold[feature_cols])
    rng = np.random.default_rng(seed)
    f1s: list[float] = []
    undefined = 0
    for _ in range(n_bootstrap):
        idx = rng.integers(0, len(hold), size=resample_size)
        f1 = f1_value(y_true[idx], y_pred[idx])
        if np.isnan(f1):
            undefined += 1
        else:
            f1s.append(f1)
    if len(f1s) < 2:
        raise ValueError("Bootstrap sin suficientes remuestras con F1 definido")
    return F1Reference(
        f1_ref=float(np.mean(f1s)),
        sigma=float(np.std(f1s, ddof=1)),
        holdout_f1=float(f1_value(y_true, y_pred)),
        n_undefined=undefined,
    )
