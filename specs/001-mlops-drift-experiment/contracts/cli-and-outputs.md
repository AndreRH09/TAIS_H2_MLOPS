# Contrato: CLI y archivos de salida

El proyecto no expone red; sus interfaces son la línea de comandos y los archivos generados.

## CLI (`uv run msft-mlops <comando>`)

| Comando | Qué hace | Salida | Código de salida |
|---|---|---|---|
| `run` | Verifica hash del dataset, valida integridad, construye features, ajusta hiperparámetros, ejecuta el walk-forward de las 2 réplicas, registra en MLflow y genera el reporte. **Es el comando único de SC-001.** | `results/*.csv`, `reports/resumen.md`, `reports/*.png` | 0 ok; 2 hash distinto; 3 validación de datos fallida |
| `validate-data` | Compara el CSV con Yahoo Finance (cierre ajustado) y escribe el informe de discrepancias (FR-002). Requiere red y `uv sync --group validation`. | `reports/validacion_datos.md`, `data/external/*.csv` | 0 ok; 4 discrepancias sobre tolerancia |
| `report` | Regenera `reports/` a partir de `results/` sin reejecutar el experimento. | `reports/resumen.md`, figuras | 0 ok |

Opciones comunes: `--config config/experiment.toml` (por defecto), `--results-dir results`.

## Configuración (`config/experiment.toml`)

Secciones: `[data]` (ruta, sha256), `[run]` (seed), `[split]` (fechas de ajuste/validación/ventanas),
`[features]` (ventanas de medias, lags), `[models.logreg]`/`[models.rf]` (grids), `[drift]`
(`alpha = 0.05`, `test = "ks"`, `correction = "bonferroni"`), `[f1_trigger]` (`k_sigma = 2`,
`holdout_rows = 63`, `n_bootstrap = 1000`, `resample_size = 126`), `[retrain]` (`window_rows = 252`),
`[validation]` (tolerancias). **Se confirma (commit) antes de la primera ejecución sobre 2022+** (SC-008).

## Archivos de salida

Esquemas en [data-model.md](../data-model.md):

- `results/window_metrics.csv`, `results/model_versions.csv`, `results/drift_details.csv`,
  `results/comparisons.csv`, `results/run_manifest.json` (semilla, hash de datos, versiones de librerías, hash de cada CSV).
- `reports/resumen.md`: tablas de P/R/F1 por ventana, diferencias B−A / C−A / B−C, Wilcoxon,
  reentrenamientos con motivo, tramo excluido, amenazas a la validez.
- Garantía: con la misma config y semilla, `results/*.csv` son idénticos byte a byte (SC-003).

## MLflow

Backend `sqlite:///mlflow.db`, experimento `msft-mlops`. Run padre por réplica (`replica=logreg|rf`)
con parámetros `seed`, `data_sha256`; runs hijos por `group/window` con métricas `precision, recall, f1`;
modelos registrados `msft-{replica}-{grupo}` con etiqueta `reason`. Consulta: `uv run mlflow ui --backend-store-uri sqlite:///mlflow.db`.
