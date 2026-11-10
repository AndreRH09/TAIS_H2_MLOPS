# TAIS_H2_MLOPS

Experimento: **modelo estático (A) vs. monitoreo de deriva + reentrenamiento (B) vs.
reentrenamiento periódico (C)** sobre la serie diaria de MSFT (feb 2021 – feb 2026), clasificando la
dirección del cierre del día siguiente con evaluación walk-forward semestral (8 ventanas) y dos
réplicas (regresión logística y Random Forest).

Documentación Spec Kit: [constitución](.specify/memory/constitution.md) ·
[spec](specs/001-mlops-drift-experiment/spec.md) · [plan](specs/001-mlops-drift-experiment/plan.md) ·
[tareas](specs/001-mlops-drift-experiment/tasks.md) · [quickstart](specs/001-mlops-drift-experiment/quickstart.md).
Revisión de literatura: [literature-review/](literature-review/README.md).

## Uso

```bash
uv sync
uv run pytest                     # tests (incluye reproducibilidad, ~2 min)
uv run msft-mlops run             # experimento completo (~2 min) -> results/ y reports/
uv run msft-mlops report          # regenera reports/ desde results/
uv sync --group validation
uv run msft-mlops validate-data   # validación externa contra Yahoo Finance (requiere red)
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

## Estructura

| Ruta | Contenido |
|---|---|
| `config/experiment.toml` | Semilla, ventanas, umbrales y grids (fijados antes de ejecutar) |
| `src/msft_mlops/` | Datos, features, ventanas, modelos, deriva, umbral de F1, políticas, walk-forward, reporte |
| `results/` | CSV deterministas: métricas por ventana, versiones de modelo, deriva, comparaciones |
| `reports/` | `resumen.md`, figuras de F1 por ventana, `validacion_datos.md` |
| `data/raw/` | Dataset inmutable con SHA-256 y procedencia |
