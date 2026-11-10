"""Precision, Recall y F1 de la clase positiva "sube" con indefinidos explícitos (FR-018)."""

from __future__ import annotations

import numpy as np


def window_scores(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    n_pos_true = int((y_true == 1).sum())
    n_pos_pred = int((y_pred == 1).sum())
    precision = tp / n_pos_pred if n_pos_pred > 0 else float("nan")
    recall = tp / n_pos_true if n_pos_true > 0 else float("nan")
    if np.isnan(precision) or np.isnan(recall):
        f1 = float("nan")
    elif precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "precision_undefined": bool(np.isnan(precision)),
        "recall_undefined": bool(np.isnan(recall)),
        "f1_undefined": bool(np.isnan(f1)),
        "n_pos_true": n_pos_true,
        "n_pos_pred": n_pos_pred,
    }


def f1_value(y_true, y_pred) -> float:
    return window_scores(y_true, y_pred)["f1"]
