"""Partición temporal y ventanas de prueba (FR-007, FR-008, FR-009)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Window:
    window_id: str
    start: pd.Timestamp
    end: pd.Timestamp
    data: pd.DataFrame  # filas de la ventana (features + y)

    @property
    def n(self) -> int:
        return len(self.data)


def _slice(ds: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    return ds.loc[pd.Timestamp(start) : pd.Timestamp(end)]


def split_2021(ds: pd.DataFrame, split: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """(ajuste feb-sep, validación oct-dic, entrenamiento inicial = todo 2021)."""
    fit = _slice(ds, split["fit_start"], split["fit_end"])
    val = _slice(ds, split["val_start"], split["val_end"])
    initial = _slice(ds, split["fit_start"], split["val_end"])
    return fit, val, initial


def test_windows(ds: pd.DataFrame, split: dict) -> list[Window]:
    """Semestres calendario consecutivos entre test_start y test_end."""
    start = pd.Timestamp(split["test_start"])
    end = pd.Timestamp(split["test_end"])
    windows: list[Window] = []
    year = start.year
    while pd.Timestamp(year=year, month=1, day=1) <= end:
        for half, (m1, m2, d2) in enumerate([(1, 6, 30), (7, 12, 31)], start=1):
            w_start = pd.Timestamp(year=year, month=m1, day=1)
            w_end = pd.Timestamp(year=year, month=m2, day=d2)
            if w_start < start or w_end > end:
                continue
            data = ds.loc[w_start:w_end]
            if len(data):
                windows.append(Window(f"{year}-H{half}", data.index[0], data.index[-1], data))
        year += 1
    return windows


def excluded_tail(ds: pd.DataFrame, split: dict) -> pd.DataFrame:
    """Tramo posterior a test_end, excluido de métricas, disparadores y comparaciones."""
    return ds.loc[pd.Timestamp(split["test_end"]) + pd.Timedelta(days=1) :]


def last_year_training(ds: pd.DataFrame, window: Window, window_rows: int) -> pd.DataFrame:
    """Últimas ``window_rows`` filas etiquetadas disponibles al cierre de la ventana.

    Se excluye la última fila de la ventana: su etiqueta usa el cierre del primer día de la
    ventana siguiente, que aún no se conoce al cerrar la ventana (Principio I).
    """
    upto = ds.loc[: window.end]
    upto = upto.iloc[:-1]
    return upto.iloc[-window_rows:]
