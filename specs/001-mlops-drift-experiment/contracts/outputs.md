# Contrato: salidas en `results/`

Todos los CSV usan UTF-8, separador `,`, fechas ISO `YYYY-MM-DD` y `NaN` literal para las
métricas indefinidas. Cada archivo incluye las columnas `seed` y `data_sha256` para que el
resultado sea trazable (Principio II). Los campos se definen en
[../data-model.md](../data-model.md).

## `window_metrics.csv`

Una fila por réplica × grupo × ventana: 2 × 6 × 8 = **96 filas**.

```text
replica,group,window_id,window_index,n,model_version,precision,recall,f1,
drift_detected,drift_min_p,drift_alpha_k,f1_below_threshold,retrained_after,seed,data_sha256
```

## `model_versions.csv`

Una fila por versión de modelo creada.

```text
replica,group,version,reason,train_start,train_end,created_after_window,
f1_ref,sigma,threshold,mlflow_model_uri,seed,data_sha256
```

Invariantes verificables:
- A tiene exactamente 1 versión por réplica.
- C tiene 1 + 8 versiones por réplica (inicial + una por ventana; la última no se evalúa).
- Ningún `train_end` es igual o posterior al inicio de la ventana que predice esa versión.

## `comparison.csv`

Una fila por réplica × par: 2 × 3 = **6 filas**.

```text
replica,pair,mean_diff_f1,windows_won,n_effective,wilcoxon_p,significant,seed,data_sha256
```

## `report.md`

Contenido: resumen de la configuración (con hash), tabla de F1 por ventana y grupo, tabla de
comparación, conteo y motivo de los reentrenamientos de B y C, figura de F1 por ventana con
los reentrenamientos marcados, tamaño del tramo excluido y amenazas a la validez.

## `data_validation.md`

Contenido: resultado de las validaciones internas, fechas faltantes o sobrantes frente a
Yahoo, número de días con diferencia de cierre ajustado > 0,5 % y los máximos de diferencia.

## Reproducibilidad (SC-003)

Dos ejecuciones de `run` con la misma configuración deben producir `window_metrics.csv` y
`comparison.csv` **idénticos byte a byte**, salvo la columna `mlflow_model_uri` de
`model_versions.csv`.
