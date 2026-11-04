# Quickstart: ejecutar y validar el experimento

Guía para que cualquier integrante (o el evaluador) reproduzca los resultados (SC-007:
menos de 30 minutos). Los comandos están definidos en [contracts/cli.md](contracts/cli.md).

## Requisitos previos

- git y [uv](https://docs.astral.sh/uv/) (`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`)
- No hace falta instalar Python: uv instala 3.12 si falta.

## 1. Preparar el entorno

```bash
git clone https://github.com/AndreRH09/TAIS_H2_MLOPS.git
cd TAIS_H2_MLOPS
git checkout 001-mlops-drift-experiment
uv sync --all-groups
```

**Esperado:** se crea `.venv/` con las versiones exactas de `uv.lock`.

## 2. Verificar los tests

```bash
uv run ruff check .
uv run pytest
```

**Esperado:** todo en verde. Se validan la ausencia de fuga, los límites de las ventanas, la
regla KS + Bonferroni, el umbral 2σ, las políticas A/B/C y la reproducibilidad.

## 3. Validar los datos (FR-002)

```bash
uv run python -m mlops_exp.run validate
```

**Esperado:** código 0 y `results/data_validation.md` sin discrepancias por encima de la
tolerancia. El snapshot de Yahoo ya está versionado. Solo si falta, se ejecuta una vez
`uv run python -m mlops_exp.run fetch-external` (requiere internet).

## 4. Ejecutar el experimento

```bash
uv run python -m mlops_exp.run run
uv run python -m mlops_exp.run report
```

**Esperado:**
- `results/window_metrics.csv` con 96 filas y `results/comparison.csv` con 6.
- `results/report.md` con tablas y figura.
- En `model_versions.csv`: A con 1 versión por réplica y C con 9.

## 5. Explorar en MLflow

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Abrir http://127.0.0.1:5000, experimento `msft-drift`. Se ven los runs por réplica × grupo, el
F1 por ventana (eje `step`), los modelos registrados `msft-{lr|rf}-{A|B|C}` con su motivo y
los reportes de deriva de Evidently como artefactos.

## 6. Comprobar la reproducibilidad (SC-003)

```bash
uv run python -m mlops_exp.run run --no-mlflow --out tmp/r1
uv run python -m mlops_exp.run run --no-mlflow --out tmp/r2
git diff --no-index --stat tmp/r1/window_metrics.csv tmp/r2/window_metrics.csv
```

**Esperado:** sin diferencias.

## Escenarios de validación (aceptación de la spec)

| Escenario | Dónde se comprueba |
|---|---|
| US1-1: métricas por ventana para A, B y C | `window_metrics.csv` (96 filas, sin vacíos salvo `NaN` justificados) |
| US1-2/3: B reentrena solo con deriva o caída de F1, y desde la ventana siguiente | `model_versions.csv` (`reason`, `created_after_window`) + `test_trigger.py` |
| US1-4: C reentrena siempre | `model_versions.csv` (9 versiones por réplica) |
| US1-5: reproducibilidad | Paso 6 |
| US2: literatura | `literature-review/` (24 fuentes, matriz, decisiones) |
| US3: comparación | `results/report.md` y `comparison.csv` |
