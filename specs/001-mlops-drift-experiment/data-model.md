# Modelo de datos (Phase 1)

Entidades de la spec y su representación. Todas las tablas de `results/` se escriben ordenadas y
con formato estable para que dos ejecuciones sean idénticas byte a byte.

## Observación diaria (`data/raw/MSFT_5years_cleaned.csv`)

`date, close, high, low, open, volume, price_change, price_change_pct, day_of_week, month, year, quarter`.
Inmutable; su SHA-256 se compara con `config/experiment.toml` al cargar.

Validaciones (`data.py`): fechas únicas y crecientes; sin nulos salvo `price_change*` de la primera
fila; `high ≥ max(open, close)`, `low ≤ min(open, close)`, `volume > 0`; sin saltos de calendario
anómalos (se listan huecos > 4 días).

## Tabla de modelado (`features.py`)

Índice `date`. Columnas: `ret_0, ret_1, ret_2, ret_3, ret_4, ma5_rel, ma10_rel, ma20_rel, vol_rel`
(K = 9) y `y` (1 si `close_{t+1} > close_t`). Sin NaN: se descartan las 19 primeras filas (sin historia para SMA20) y la última.

## Ventana de prueba (`windows.py`)

| Campo | Descripción |
|---|---|
| `window_id` | `2022-H1` … `2025-H2` (8) |
| `start`, `end` | primer y último día de negociación incluidos |
| `n` | número de registros |
| `complete` | siempre `True` para las 8; el tramo 2026 se reporta como `excluded_tail` con su `n` |

## Versión de modelo (`results/model_versions.csv`)

`replica, group, version, created_after_window, used_from_window, reason, train_start, train_end, n_train,
holdout_start, f1_ref, sigma, holdout_f1, val_f1_hyperparam_selection, hyperparams` (el id de run de MLflow no se guarda en el CSV porque cambia en cada ejecución y rompería el determinismo)

- `version` empieza en 1 (`reason = inicial`) para A, B y C.
- A solo tiene versión 1. B y C incrementan al reentrenar.
- `reason ∈ {inicial, deriva, caida_f1, deriva+caida_f1, periodico}`.
- `created_after_window` = ventana cuyo cierre disparó el reentrenamiento; la versión rige desde la
  siguiente. En la última ventana se registra con `used_in_window = null`.

## Evaluación de ventana (`results/window_metrics.csv`)

Una fila por `replica × group × window`, con `group ∈ {A, B, C, siempre_sube, persistencia, estratificado}`:

`replica, group, window_id, n, version, precision, recall, f1, precision_undefined,
recall_undefined, f1_undefined, n_pos_true, n_pos_pred, drift_detected, drift_min_p, drift_threshold, retrain_triggered, retrain_reason`

Para los baselines `version` y las columnas de deriva quedan vacías.

## Deriva por feature (`results/drift_details.csv`)

`replica, group, window_id, version, feature, ks_statistic, p_value, threshold, drifted`

Se registra para todos los grupos (informativo); solo B la usa como disparador.

## Comparación entre grupos (`results/comparisons.csv`)

`replica, comparison (B-A | C-A | B-C), n_effective, mean_diff_f1, windows_won, windows_lost,
windows_tied, wilcoxon_statistic, p_value, significant_at_0_05`

## Fuente bibliográfica (`literature-review/referencias.md`)

Referencia IEEE, DOI, eje temático (A MLOps, B deriva/reentrenamiento, C evaluación temporal, D
dirección bursátil), fila en `matriz-contraste.md`. No se modifica; se verifica con un test.

## Transiciones (grupo B)

```text
versión v ──(cierra ventana w, evaluada con v)──▶ ¿deriva(w, ref(v)) o F1_w < F1_ref(v) − 2σ(v)?
   no → B conserva v
   sí → reentrenar con 252 filas hasta w → versión v+1 (ref, F1_ref, σ nuevos) → rige en w+1
```

Grupo C: igual, pero siempre reentrena (`reason = periodico`). Grupo A: nunca.
