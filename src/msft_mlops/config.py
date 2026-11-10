"""Carga y validación de ``config/experiment.toml``."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Config:
    raw: dict[str, Any]
    root: Path

    def __getitem__(self, key: str) -> Any:
        return self.raw[key]

    @property
    def seed(self) -> int:
        return int(self.raw["run"]["seed"])

    @property
    def replicas(self) -> list[str]:
        return list(self.raw["run"]["replicas"])

    @property
    def data_path(self) -> Path:
        return self.root / self.raw["data"]["path"]

    @property
    def data_sha256(self) -> str:
        return str(self.raw["data"]["sha256"])


_REQUIRED_POSITIVE = [
    ("drift", "alpha"),
    ("f1_trigger", "k_sigma"),
    ("f1_trigger", "holdout_rows"),
    ("f1_trigger", "n_bootstrap"),
    ("f1_trigger", "resample_size"),
    ("retrain", "window_rows"),
]


def load_config(path: str | Path = "config/experiment.toml") -> Config:
    path = Path(path).resolve()
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    for section, key in _REQUIRED_POSITIVE:
        try:
            value = raw[section][key]
        except KeyError as exc:
            raise ValueError(f"Falta [{section}] {key} en {path}") from exc
        if not value > 0:
            raise ValueError(f"[{section}] {key} debe ser positivo (es {value})")
    # El directorio raíz es el padre de config/
    return Config(raw=raw, root=path.parent.parent)
