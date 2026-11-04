# Implementation Plan: Experimento modelo estático vs. modelo operado con MLOps

**Branch**: `001-mlops-drift-experiment` | **Date**: 2026-11-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-mlops-drift-experiment/spec.md`

## Summary

Simulación walk-forward sobre el histórico diario de MSFT (2021-02 → 2025-12) que compara la
dirección del precio al día siguiente predicha por tres políticas de operación del mismo
clasificador:

- **A:** estático.
- **B:** reentrena cuando hay deriva de features, medida con KS + Bonferroni, o cuando F1 cae
  por debajo de `F1_ref − 2σ`.
- **C:** reentrena cada semestre.

Se agregan tres baselines ingenuos y dos réplicas (regresión logística y Random Forest). La
prueba son 8 ventanas semestrales (2022-H1 a 2025-H2). Cada ejecución registra modelos y
métricas en MLflow (SQLite), y un reporte final compara los grupos con un test de Wilcoxon
pareado.

Enfoque técnico: un paquete Python pequeño con un solo punto de entrada (`run`), configuración
inmutable en TOML, la regla de deriva calculada con `scipy` (la fuente de verdad, testeable),
reportes visuales de Evidently como artefacto y tests que prueban la ausencia de fuga, las
reglas de disparo y la reproducibilidad. Detalle en [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12 (fijado en `pyproject.toml` y `.python-version`; uv lo
gestiona)

**Primary Dependencies**: pandas, numpy, scikit-learn, scipy, mlflow, evidently, matplotlib.
Grupo opcional `validation`: yfinance. Grupo `dev`: pytest, ruff. Las versiones exactas
quedan en `uv.lock`.

**Storage**: archivos. `data/raw/` (CSV inmutable con SHA-256), `data/external/` (snapshot de
Yahoo Finance con hash), `results/` (CSV y reportes), MLflow con backend `sqlite:///mlflow.db`
y artefactos en `mlartifacts/` (ambos ignorados por git)

**Testing**: pytest (unitarios + una prueba de reproducibilidad de punta a punta); ruff para
lint y formato

**Target Platform**: Windows 11 y Linux (CI en GitHub Actions `ubuntu-latest`)

**Project Type**: CLI y librería de experimentación (simulación por lotes)

**Performance Goals**: el experimento completo (2 réplicas × 3 grupos × 8 ventanas + baselines
+ bootstrap) en < 5 min en una laptop; los tests en < 2 min en CI

**Constraints**: determinista (semillas fijas, SC-003); sin red durante el experimento (el
snapshot de Yahoo se descarga una sola vez); umbrales fijados antes de la prueba (SC-008)

**Scale/Scope**: 1 254 registros, ~6 features, 8 ventanas, ~10 versiones de modelo por réplica
como máximo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo cumple el plan | Estado |
|---|---|---|
| I. Integridad temporal | Ventanas por calendario; features solo con `t` y anteriores (FR-005, FR-006a); hiperparámetros solo con 2021; **purga de 1 día** al reentrenar (la etiqueta del último día depende del cierre siguiente); tests de fuga (`test_features.py`, `test_windows.py`) | ✅ |
| II. Reproducibilidad | `uv.lock`, semilla global en `experiment.toml`, SHA-256 del dataset verificado al cargar, todo run en MLflow; test que ejecuta dos veces y compara métricas | ✅ |
| III. Comparabilidad | Un mismo `GroupPolicy` con el mismo modelo, hiperparámetros, features y ventanas; solo cambia la política de reentrenamiento. Umbrales en `experiment.toml` versionado antes de la primera ejecución | ✅ |
| IV. Evidencia y simplicidad | Cada parámetro de `experiment.toml` cita su fuente de `literature-review/`; sin orquestador, feature store, serving ni base de datos con servidor | ✅ |
| Restricciones técnicas | Python + uv, scikit-learn, Evidently, MLflow (SQLite), CSV/Parquet, script Python, GitHub Actions | ✅ Ver la nota sobre Evidently/scipy |
| Flujo de trabajo | Rama `001-…`; CI (ruff + pytest) antes de integrar | ✅ |

**Nota Evidently/scipy:** la constitución asigna la detección de deriva a Evidently. La
**decisión** (KS por feature + Bonferroni, FR-012a) se calcula con `scipy.stats.ks_2samp`,
porque es el test exacto de [9], es determinista y se prueba sin depender de cambios de API de
Evidently. Evidently genera el reporte de deriva de cada ventana como artefacto en MLflow. No
es una violación, porque Evidently sigue en el stack; queda registrado en research.md (R3).

**Gate inicial:** PASS.

## Project Structure

### Documentation (this feature)

```text
specs/001-mlops-drift-experiment/
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones técnicas R1–R10
├── data-model.md        # Fase 1: entidades y reglas de validación
├── quickstart.md        # Fase 1: guía de ejecución y validación
├── contracts/
│   ├── cli.md           # Comandos y códigos de salida
│   ├── config.md        # Esquema de experiment.toml
│   └── outputs.md       # Esquema de los CSV de resultados
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
pyproject.toml           # Dependencias, ruff, pytest
uv.lock
.python-version          # 3.12
experiment.toml          # Parámetros congelados del experimento (con citas)
data/
├── raw/                 # MSFT_5years_cleaned.csv (inmutable, SHA-256)
└── external/            # Snapshot de Yahoo Finance + hash
src/mlops_exp/
├── __init__.py
├── config.py            # Carga y valida experiment.toml (tomllib)
├── data.py              # Carga, verificación de hash y validación del dataset
├── validate_external.py # Comparación con Yahoo Finance (FR-002)
├── features.py          # Features relativas + etiqueta
├── windows.py           # Ventanas semestrales, recortes de entrenamiento y purga
├── models.py            # Pipelines LR/RF, ajuste inicial, baselines ingenuos
├── drift.py             # KS + Bonferroni (decisión), reporte Evidently (artefacto)
├── trigger.py           # Umbral de F1 por bootstrap y políticas A/B/C
├── experiment.py        # Bucle walk-forward + registro en MLflow
├── report.py            # Comparación (Wilcoxon) y figuras
└── run.py               # CLI: validate | run | report
tests/
├── test_data.py
├── test_features.py     # Ausencia de fuga, features relativas
├── test_windows.py      # Límites de ventanas, exclusión del tramo final, purga
├── test_drift.py        # KS + Bonferroni con casos sintéticos
├── test_trigger.py      # Umbral 2σ, políticas A/B/C
└── test_reproducibility.py
results/                 # Salidas versionables (CSV, report.md, figuras)
.github/workflows/ci.yml # ruff + pytest
```

**Structure Decision**: proyecto único (CLI + librería) con layout `src/`. Un módulo por
concepto del dominio. Sin subpaquetes ni capas: el experimento es una sola simulación por
lotes.

## Complexity Tracking

Sin violaciones de la constitución que justificar.

## Post-Design Constitution Re-check

Revisado tras generar data-model.md, contracts/ y quickstart.md:
- I: la purga de 1 día y los tests de fuga están en el diseño (R5, `test_windows.py`). ✅
- II: el contrato `outputs.md` incluye semilla, hash de datos y versión de modelo en cada
  fila. ✅
- III: `experiment.toml` concentra todos los umbrales; el contrato `config.md` impide
  cambiarlos por grupo. ✅
- IV: cada parámetro del esquema `config.md` tiene un campo `fuente`. ✅

**Gate final:** PASS.
