# Data Model (Fase 1)

Entidades del experimento, sus campos y sus reglas de validación. Son estructuras en memoria
(DataFrames y dataclasses) que se persisten como CSV en `results/` según
[contracts/outputs.md](contracts/outputs.md).

## Observación diaria

Fuente: `data/raw/MSFT_5years_cleaned.csv`.

| Campo | Tipo | Regla |
|---|---|---|
| `date` | fecha | Única, estrictamente creciente, solo días hábiles |
| `open`, `high`, `low`, `close` | float > 0 | `low ≤ open, close ≤ high` |
| `volume` | int > 0 | — |

**Validaciones al cargar** (falla con error si no se cumplen):
- SHA-256 del archivo = el valor registrado en `experiment.toml`.
- 1 254 filas entre 2021-02-04 y 2026-02-02.
- Sin fechas duplicadas ni nulos en OHLCV.

Las columnas `price_change*`, `day_of_week`, `month`, `year` y `quarter` del CSV **no se
usan** (se recalculan si hace falta, para no depender de los cálculos del notebook original).

## Fila de features

Derivada de la observación diaria. Detalle en research.md, R2.

| Campo | Tipo | Regla |
|---|---|---|
| `date` | fecha | — |
| `ret_1`, `ret_2`, `ret_5`, `px_sma5`, `px_sma20`, `vol_sma20` | float | Calculados solo con filas `≤ date`; adimensionales |
| `y` | {0, 1} | `1` si `close(date+1) > close(date)` |

- Se descartan las filas sin historia suficiente (las primeras 20) y la última (sin `date+1`).
- **Invariante de no fuga:** cambiar cualquier precio posterior a `date` no altera las
  features de `date`. Se verifica en `test_features.py`.

## Ventana de prueba

| Campo | Tipo | Regla |
|---|---|---|
| `window_id` | str | `2022-H1` … `2025-H2` (8 ventanas) |
| `index` | int | 0 … 7 |
| `start`, `end` | fecha | Primer y último día hábil del semestre |
| `n` | int | Número de filas (≈ 126) |

El tramo 2026-01-01 → 2026-02-02 no es una ventana: se registra solo su tamaño (FR-007).

## Versión de modelo

| Campo | Tipo | Regla |
|---|---|---|
| `replica` | {`lr`, `rf`} | — |
| `group` | {`A`, `B`, `C`} | — |
| `version` | int ≥ 1 | 1 = modelo inicial |
| `reason` | {`initial`, `drift`, `f1_drop`, `drift+f1_drop`, `scheduled`} | `A` solo `initial`; `C` solo `initial` o `scheduled` |
| `train_start`, `train_end` | fecha | `train_end` < inicio de la primera ventana en que se usa |
| `created_after_window` | str o null | Ventana cuyo cierre disparó la versión (null en la inicial) |
| `f1_ref`, `sigma` | float | De un hold-out temporal (research.md, R4) |
| `threshold` | float | `f1_ref − 2·sigma` |

**Transiciones de estado por grupo** (al cierre de cada ventana *k* ≤ 6; la ventana 7 es la
última y su reentrenamiento se registra pero no se evalúa):

```text
A: vigente(v1) ──────────────────────────────▶ vigente(v1)        (nunca cambia)
B: vigente(vn) ── deriva o F1 < threshold ──▶ vigente(vn+1)       (si no: sigue vn)
C: vigente(vn) ── siempre ──────────────────▶ vigente(vn+1)
```

## Evaluación de ventana

Una fila por réplica × grupo (o baseline) × ventana.

| Campo | Tipo | Regla |
|---|---|---|
| `replica`, `group`, `window_id` | — | `group` ∈ {A, B, C, always_up, persistence, stratified} |
| `model_version` | int o null | null para baselines |
| `precision`, `recall`, `f1` | float o `NaN` | `NaN` explícito si hay una sola clase (Edge Cases); positivo = "sube" |
| `n` | int | Igual al `n` de la ventana |
| `drift_detected` | bool | Para A, B y C (en A es informativo) |
| `drift_min_p`, `drift_alpha_k` | float | `drift_alpha_k = 0,05/K` |
| `f1_below_threshold` | bool | Solo B (informativo en A y C) |
| `retrained_after` | bool | Si al cierre de esta ventana se creó una nueva versión |

## Resultado de comparación

Una fila por réplica × par (B−A, C−A, B−C).

| Campo | Tipo |
|---|---|
| `replica`, `pair` | — |
| `mean_diff_f1` | float |
| `windows_won` | int (0–8) |
| `n_effective` | int (pares no nulos) |
| `wilcoxon_p` | float |
| `significant` | bool (`p < 0,05`) |

## Relaciones

```text
Observación diaria 1──* Fila de features *──1 Ventana de prueba
Versión de modelo 1──* Evaluación de ventana *──1 Ventana de prueba
Evaluación de ventana *──1 Resultado de comparación (agregadas por réplica y par)
```
