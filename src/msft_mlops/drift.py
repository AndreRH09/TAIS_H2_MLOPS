"""Detección de deriva: KS por feature + Bonferroni con Evidently (FR-012, FR-012a, FR-016).

Hay deriva si ``min(p) < alpha / K`` con K = número de features. Evidently calcula el
estadístico KS de cada columna (``ValueDrift``); su valor es el p-valor, idéntico al de
``scipy.stats.ks_2samp`` (verificado en tests/unit/test_drift.py).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import pandas as pd

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from evidently import DataDefinition, Dataset, Report
    from evidently.metrics import ValueDrift


@dataclass(frozen=True)
class DriftResult:
    drifted: bool
    min_p: float
    threshold: float
    per_feature: dict[str, float] = field(default_factory=dict)


def detect_drift(
    reference: pd.DataFrame, current: pd.DataFrame, alpha: float = 0.05
) -> DriftResult:
    cols = list(reference.columns)
    k = len(cols)
    threshold = alpha / k
    definition = DataDefinition(numerical_columns=cols)
    ref_ds = Dataset.from_pandas(reference.reset_index(drop=True), data_definition=definition)
    cur_ds = Dataset.from_pandas(current[cols].reset_index(drop=True), data_definition=definition)
    report = Report([ValueDrift(column=c, method="ks", threshold=threshold) for c in cols])
    snapshot = report.run(cur_ds, ref_ds)
    p_values: dict[str, float] = {}
    for metric in snapshot.dict()["metrics"]:
        cfg = metric["config"]
        p_values[cfg["column"]] = float(metric["value"])
    min_p = min(p_values.values())
    return DriftResult(bool(min_p < threshold), min_p, threshold, p_values)
