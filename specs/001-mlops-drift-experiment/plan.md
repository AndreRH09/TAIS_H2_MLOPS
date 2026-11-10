# Implementation Plan: Experimento modelo estático vs. modelo operado con MLOps

**Branch**: `001-mlops-drift-experiment` | **Date**: 2026-11-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-mlops-drift-experiment/spec.md`

## Summary

Simulación por lotes, walk-forward semestral (8 ventanas, 2022-H1 … 2025-H2), de tres grupos
sobre la dirección diaria de MSFT: **A** (modelo fijo), **B** (reentrena solo si hay deriva KS +
Bonferroni o `F1 < F1_ref − 2σ`) y **C** (reentrena al cierre de cada ventana). Se ejecuta en dos
réplicas (regresión logística y Random Forest) y se contrasta con tres baselines ingenuos.

Enfoque técnico: paquete Python `msft_mlops` gestionado con `uv`; features relativas calculadas
solo con información pasada; bucle walk-forward en un script que decide el reentrenamiento;
deriva con Evidently; seguimiento de runs y versiones de modelo en MLflow (SQLite local);
resultados deterministas en CSV, resumen comparativo en Markdown con test de Wilcoxon pareado.
La literatura (US2) ya está en `literature-review/` y solo se verifica con un test.

## Technical Context

**Language/Version**: Python 3.12 (Evidently 0.7 no importa con pandas 3 ni con el Python 3.13 probado; se fija `pandas<3`)

**Primary Dependencies**: scikit-learn, pandas (<3), numpy, scipy, evidently, mlflow, matplotlib; `yfinance` solo en el grupo opcional `validation`

**Storage**: CSV versionado en `data/raw/` (inmutable, SHA-256); resultados en `results/` (CSV); MLflow con SQLite local (`mlflow.db`, ignorado por git)

**Testing**: pytest (+ ruff para lint), ambos en GitHub Actions

**Target Platform**: Windows/Linux, CPU, ejecución local por lotes

**Project Type**: CLI / script de investigación (single project)

**Performance Goals**: experimento completo (2 réplicas × 3 grupos × 8 ventanas) en < 5 min; reproducción completa por un evaluador en < 30 min (SC-007)

**Constraints**: determinismo bit a bit de las métricas (semilla fija, `n_jobs=1`); sin servicios externos para ejecutar el experimento (solo la validación FR-002 usa red)

**Scale/Scope**: 1254 filas, 1 activo, 9 features, 2 clasificadores, 8 ventanas de ≈ 126 filas

## Constitution Check

*GATE: pasa antes de Phase 0 y se re-evalúa tras Phase 1 (constitución v1.1.0).*

| Principio | Cumplimiento en el diseño | Estado |
|---|---|---|
| I. Integridad temporal | Partición solo temporal; features con ventanas hacia atrás (`rolling`/`shift` positivo); escalador, hiperparámetros y referencia de deriva ajustados solo con datos previos a la ventana; reentrenamiento descarta la última fila de la ventana cuya etiqueta usa el día siguiente; test de fuga (truncar el futuro no cambia las features) | ✔ |
| II. Reproducibilidad | `pyproject.toml` + `uv.lock`; semilla única en `config/experiment.toml`; hash del CSV verificado al cargar; cada run, versión y ventana se registra en MLflow; test que ejecuta dos veces y compara | ✔ |
| III. Comparabilidad | A, B y C comparten pipeline, hiperparámetros, features, ventanas y métricas; solo cambia la función `should_retrain`; umbrales en `config/experiment.toml` y en la spec antes de la primera ejecución | ✔ |
| IV. Evidencia y simplicidad | Cada parámetro enlazado a `literature-review/decisiones.md` (ver `research.md`); sin Kubernetes, Kafka, etc.; MLflow/Evidently ya exigidos por la constitución | ✔ |
| Flujo | Rama `001-mlops-drift-experiment`; CI ruff + pytest; documentación en español | ✔ |

Sin violaciones; no se requiere *Complexity Tracking*.

## Project Structure

### Documentation (this feature)

```text
specs/001-mlops-drift-experiment/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-and-outputs.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
pyproject.toml
uv.lock
config/
└── experiment.toml            # semilla, ventanas, umbrales, grids (se fija antes de ejecutar)
data/
├── raw/MSFT_5years_cleaned.csv   # inmutable (+ README con SHA-256)
└── external/                  # copia cacheada de la fuente externa (FR-002)
src/msft_mlops/
├── config.py                  # carga y valida experiment.toml
├── data.py                    # carga + verificación de hash + validación de integridad
├── external_validation.py     # compara contra Yahoo Finance (cierre ajustado)
├── features.py                # features relativas + etiqueta (FR-004/005/006a)
├── windows.py                 # partición temporal 2021 / 8 ventanas / tramo excluido
├── models.py                  # pipelines LR y RF, búsqueda de hiperparámetros (FR-009)
├── drift.py                   # KS por feature + Bonferroni con Evidently (FR-012a)
├── threshold.py               # F1 de referencia y σ por bootstrap (FR-013a)
├── policies.py                # should_retrain para A, B, C
├── baselines.py               # siempre sube, persistencia, estratificado
├── metrics.py                 # P/R/F1 con indefinidos explícitos
├── walk_forward.py            # bucle de simulación por réplica
├── tracking.py                # MLflow: runs, versiones y registro
├── report.py                  # resumen comparativo, Wilcoxon, gráficos
└── cli.py                     # entradas: run, validate-data, report
tests/
├── unit/                      # features, fuga, ventanas, drift, umbral, métricas, políticas
├── integration/               # walk-forward sintético y reproducibilidad (2 ejecuciones)
└── docs/                      # estructura de la bibliografía (≥ 20 fuentes, DOI, matriz)
results/                       # salida determinista (CSV) — se versiona
reports/                       # resumen.md y figuras
.github/workflows/ci.yml
```

**Structure Decision**: proyecto único con layout `src/`. Un módulo por responsabilidad de la
spec para que cada FR tenga un lugar claro y testeable. `results/` y `reports/` se versionan
porque son el entregable del estudio; `mlflow.db`/`mlruns/` quedan ignorados (ya en `.gitignore`).

## Complexity Tracking

Sin violaciones que justificar.
