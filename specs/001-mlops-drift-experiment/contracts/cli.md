# Contrato: CLI

Un solo punto de entrada: `uv run python -m mlops_exp.run <comando> [opciones]`.

| Comando | Qué hace | Lee | Escribe | Red |
|---|---|---|---|---|
| `fetch-external` | Descarga MSFT ajustado de Yahoo Finance para el rango del dataset y guarda el snapshot con su hash. Se ejecuta **una sola vez** | `experiment.toml` | `data/external/msft_yahoo_adjusted.csv` (+ `.sha256`) | Sí (requiere el grupo `validation`) |
| `validate` | Verifica el hash del dataset, sus validaciones internas y la comparación con el snapshot de Yahoo | `data/raw/`, `data/external/` | `results/data_validation.md` | No |
| `run` | Ejecuta el experimento completo (2 réplicas × A/B/C × 8 ventanas + baselines) y registra en MLflow | `experiment.toml`, `data/raw/` | `results/window_metrics.csv`, `results/model_versions.csv`, `mlflow.db`, `mlartifacts/` | No |
| `report` | Calcula la comparación (Wilcoxon) y genera figuras y reporte | `results/*.csv` | `results/comparison.csv`, `results/report.md`, `results/figures/*.png` | No |

## Opciones

| Opción | Comandos | Por defecto | Uso |
|---|---|---|---|
| `--config PATH` | todos | `experiment.toml` | Ruta a la configuración |
| `--out DIR` | `run`, `report` | `results/` | Carpeta de salida. La prueba de reproducibilidad la usa para escribir en dos carpetas temporales |
| `--no-mlflow` | `run` | desactivada | Corre sin registrar en MLflow (tests rápidos) |

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Éxito |
| 1 | Error de validación de datos (hash distinto, filas o fechas inesperadas, nulos) |
| 2 | Configuración inválida (falta un parámetro, valor fuera de rango o sin campo `fuente`) |
| 3 | Falta un insumo (snapshot de Yahoo para `validate`, resultados para `report`) |

Los mensajes de error van a stderr; el progreso, a stdout.
