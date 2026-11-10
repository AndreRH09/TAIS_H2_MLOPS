"""Baselines ingenuos de referencia (FR-017)."""

from __future__ import annotations

import numpy as np
import pandas as pd

BASELINES = ("siempre_sube", "persistencia", "estratificado")


def predict_siempre_sube(n: int) -> np.ndarray:
    return np.ones(n, dtype=int)


def predict_persistencia(window: pd.DataFrame) -> np.ndarray:
    """Repite la dirección del día anterior: ``ret_0`` es el rendimiento de *t* (ya observado)."""
    return (window["ret_0"].to_numpy() > 0).astype(int)


def predict_estratificado(n: int, p_up: float, rng: np.random.Generator) -> np.ndarray:
    return (rng.random(n) < p_up).astype(int)
