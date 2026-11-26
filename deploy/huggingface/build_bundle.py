"""Arma la carpeta que se sube al Space de Hugging Face (feature 002, FR-110).

Copia solo lo que necesita la imagen Docker. Hugging Face rechaza binarios fuera de LFS/Xet, así
que se dejan fuera PDF, DOCX, PNG y notebooks. El README del Space (con su cabecera YAML) reemplaza
al README del repositorio.

Uso:  python deploy/huggingface/build_bundle.py space_bundle
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INCLUDE = [
    "Dockerfile",
    ".dockerignore",
    "pyproject.toml",
    "uv.lock",
    ".streamlit/config.toml",
    "app",
    "src",
    "config",
    "data/raw/MSFT_5years_cleaned.csv",
    "data/raw/README.md",
    "results",
]
SKIP_SUFFIXES = {".pyc", ".png", ".pdf", ".docx", ".ipynb"}


def build(out: Path) -> list[Path]:
    if out.exists():
        shutil.rmtree(out)
    copied: list[Path] = []
    for rel in INCLUDE:
        src = ROOT / rel
        if not src.exists():
            raise FileNotFoundError(f"Falta {rel} en el repositorio")
        files = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file())
        for f in files:
            if f.suffix in SKIP_SUFFIXES or "__pycache__" in f.parts:
                continue
            dst = out / f.relative_to(ROOT)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)  # bytes exactos: el SHA-256 del CSV debe coincidir
            copied.append(dst)
    shutil.copy2(ROOT / "deploy" / "huggingface" / "README.md", out / "README.md")
    copied.append(out / "README.md")
    return copied


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "space_bundle").resolve()
    files = build(target)
    size = sum(f.stat().st_size for f in files) / 1e6
    print(f"{len(files)} archivos ({size:.1f} MB) en {target}")
