"""US2 / FR-020 / FR-021 / SC-005: la bibliografía y la matriz existen y están completas."""

import re
from pathlib import Path

LIT = Path(__file__).resolve().parents[2] / "literature-review"


def _entries() -> dict[int, str]:
    """Cada referencia empieza con ``**[n]**`` y termina antes de su anotación (línea con ``>``)."""
    text = (LIT / "referencias.md").read_text(encoding="utf-8")
    entries: dict[int, str] = {}
    for m in re.finditer(r"^\*\*\[(\d+)\]\*\*(.*?)(?=^>|\Z)", text, flags=re.M | re.S):
        entries[int(m.group(1))] = m.group(2)
    return entries


def test_at_least_20_references_each_with_doi_or_editorial_source():
    entries = _entries()
    assert len(entries) >= 20
    for n, body in entries.items():
        has_doi = re.search(r"10\.\d{4,9}/\S+", body)
        has_editorial = "[Online]. Available:" in body and "http" in body
        assert has_doi or has_editorial, f"[{n}] sin DOI ni fuente editorial"


def test_publication_years_within_2015_2026():
    for n, body in _entries().items():
        # El año de publicación va entre comas ("..., 2020, doi: ..."); las páginas usan guion.
        years = [int(y) for y in re.findall(r",\s+(20[12]\d)\s*[,.]", body)]
        assert years, f"[{n}] sin año"
        assert 2015 <= years[-1] <= 2026, f"[{n}] año fuera de rango"


def test_contrast_matrix_has_required_dimensions():
    text = (LIT / "matriz-contraste.md").read_text(encoding="utf-8").lower()
    for dim in ["datos", "partici", "baseline", "reentren", "métricas"]:
        assert dim in text, dim


def test_decisions_d1_to_d7_and_axes_documented():
    text = (LIT / "decisiones.md").read_text(encoding="utf-8")
    for d in range(1, 8):
        assert f"D{d}" in text
    readme = (LIT / "README.md").read_text(encoding="utf-8")
    for axis in ["(A)", "(B)", "(C)"]:
        assert axis in readme
