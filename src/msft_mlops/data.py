"""Carga del dataset crudo con verificación de hash e integridad (FR-001, FR-003)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from .config import Config

REQUIRED_COLUMNS = [
    "date",
    "close",
    "high",
    "low",
    "open",
    "volume",
    "price_change",
    "price_change_pct",
]


class DataHashMismatch(RuntimeError):
    """El hash del CSV no coincide con el fijado en la configuración (código de salida 2)."""


class DataValidationError(RuntimeError):
    """El dataset no pasa la validación de integridad (código de salida 3)."""


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_integrity(df: pd.DataFrame, max_gap_days: int = 4) -> list[str]:
    """Devuelve la lista de avisos (huecos de calendario); lanza si hay errores duros."""
    errors: list[str] = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DataValidationError(f"Faltan columnas: {missing}")
    if df["date"].duplicated().any():
        errors.append("Fechas duplicadas")
    if not df["date"].is_monotonic_increasing:
        errors.append("Fechas no crecientes")
    base_cols = ["date", "close", "high", "low", "open", "volume"]
    if df[base_cols].isna().any().any():
        errors.append("Valores nulos en date/close/high/low/open/volume")
    nulls = df[["price_change", "price_change_pct"]].isna()
    if nulls.iloc[1:].any().any():
        errors.append("Nulos en price_change* fuera de la primera fila")
    tol = 1e-6
    if (df["high"] + tol < df[["open", "close"]].max(axis=1)).any():
        errors.append("high < max(open, close)")
    if (df["low"] - tol > df[["open", "close"]].min(axis=1)).any():
        errors.append("low > min(open, close)")
    if (df["volume"] <= 0).any():
        errors.append("volume <= 0")
    if errors:
        raise DataValidationError("; ".join(errors))
    gaps = df["date"].diff().dt.days
    warnings = [
        f"Hueco de {int(g)} días antes de {d.date()}"
        for d, g in zip(df["date"], gaps, strict=True)
        if pd.notna(g) and g > max_gap_days
    ]
    return warnings


def load_raw(config: Config, check_hash: bool = True) -> pd.DataFrame:
    path = config.data_path
    if check_hash:
        actual = sha256_file(path)
        if actual != config.data_sha256:
            raise DataHashMismatch(
                f"SHA-256 de {path.name} = {actual}, esperado {config.data_sha256}"
            )
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df
