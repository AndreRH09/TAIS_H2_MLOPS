"""Políticas de reentrenamiento. Es lo único que difiere entre A, B y C (Principio III)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .drift import DriftResult
from .threshold import F1Reference


@dataclass(frozen=True)
class Policy:
    group: str
    k_sigma: float = 2.0

    def should_retrain(self, f1_window: float, drift: DriftResult, ref: F1Reference) -> str | None:
        raise NotImplementedError


class PolicyA(Policy):
    """Control: nunca reentrena."""

    def should_retrain(self, f1_window, drift, ref):
        return None


class PolicyB(Policy):
    """Monitoreo: reentrena por deriva y/o ``F1 < F1_ref − k·σ``.

    Un F1 indefinido de la ventana no dispara por sí solo (no es evaluable).
    """

    def should_retrain(self, f1_window, drift, ref):
        f1_drop = (not math.isnan(f1_window)) and f1_window < ref.lower_bound(self.k_sigma)
        if drift.drifted and f1_drop:
            return "deriva+caida_f1"
        if drift.drifted:
            return "deriva"
        if f1_drop:
            return "caida_f1"
        return None


class PolicyC(Policy):
    """Periódico: reentrena al cierre de cada ventana."""

    def should_retrain(self, f1_window, drift, ref):
        return "periodico"


def make_policies(k_sigma: float) -> dict[str, Policy]:
    return {"A": PolicyA("A", k_sigma), "B": PolicyB("B", k_sigma), "C": PolicyC("C", k_sigma)}
