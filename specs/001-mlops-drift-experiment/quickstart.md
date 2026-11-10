# Quickstart: validar el experimento de extremo a extremo

Prerrequisitos: [uv](https://docs.astral.sh/uv/) instalado; Python 3.12 (uv lo descarga si falta).

```bash
uv sync
```

## 1. Calidad y tests (CI)

```bash
uv run ruff check .
uv run pytest
```

Esperado: lint sin errores; tests de fuga, ventanas, deriva, umbral, políticas, literatura y
reproducibilidad en verde.

## 2. Ejecutar el experimento (SC-001)

```bash
uv run msft-mlops run
```

Esperado: `results/window_metrics.csv` con 8 ventanas × (A, B, C + 3 baselines) × 2 réplicas
(= 96 filas), `results/model_versions.csv`, `reports/resumen.md`. Salida con código 0.

## 3. Reproducibilidad (SC-003)

```bash
uv run msft-mlops run --results-dir results_check
```

Esperado: `results_check/*.csv` idénticos a `results/*.csv` (comparar hashes en `run_manifest.json`).

## 4. Validación externa de datos (FR-002, requiere red)

```bash
uv sync --group validation
uv run msft-mlops validate-data
```

Esperado: `reports/validacion_datos.md` con discrepancias de fechas, precio y volumen frente a Yahoo Finance.

## 5. Inspeccionar el registro de runs

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Esperado: experimento `msft-mlops` con 1 run padre por réplica y runs hijos por grupo y ventana.

## 6. Literatura (US2)

Abrir [literature-review/README.md](../../literature-review/README.md). El test
`tests/docs/test_literature.py` comprueba ≥ 20 fuentes con DOI y la matriz de contraste.
