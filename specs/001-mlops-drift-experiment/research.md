# Research (Phase 0)

La spec no deja `NEEDS CLARIFICATION`. Este documento fija las decisiones de implementación
que la spec no determina, con su respaldo.

## R1. Versiones y entorno

- **Decisión**: Python 3.12, `pandas<3`, Evidently 0.7.x, MLflow 3.x, scikit-learn 1.9, scipy 1.18.
- **Evidencia**: probado: Evidently falla al importar con pandas 3 (`infer_dtype_from_object`) y
  con Python 3.13.5 (conflicto de layout en pydantic v1). Con 3.12 + `pandas<3` importa bien.
- **Alternativas**: usar solo `scipy.stats.ks_2samp` (descartado: la constitución exige Evidently;
  se conserva scipy como verificación cruzada en un test).

## R2. Features y etiqueta (FR-004, FR-005, FR-006a)

- **Decisión**: K = 9 features, todas calculadas desde `close` y `volume` en el instante *t*:
  `ret_0` (rendimiento de *t*), `ret_1 … ret_4` (rendimientos rezagados), `ma5_rel`, `ma10_rel`,
  `ma20_rel` (`close / SMA_n − 1`) y `vol_rel` (`volume / SMA20(volume) − 1`).
  Etiqueta `y_t = 1` si `close_{t+1} > close_t`. Se descartan las primeras 20 filas (sin historia)
  y la última (sin etiqueta).
- **Rationale**: relativas para evitar que la tendencia (≈ 240 → 500) dispare la deriva en todas
  las ventanas; rendimientos recalculados desde `close` (no se usa `price_change_pct`, solo se
  contrasta). Ventanas 5/10/20 son las usuales en [21], [22].
- **Alternativas**: niveles absolutos (descartado por FR-006a); RSI/MACD (más complejidad sin
  respaldo en la spec).

## R3. Partición y ventanas (FR-007, FR-008, FR-009)

- **Decisión**: ajuste = 2021-02 … 2021-09; validación = 2021-10 … 2021-12; modelo inicial = todo
  2021. Ventanas = semestres calendario 2022-H1 … 2025-H2 (8). Tramo 2026-01-01…2026-02-02
  excluido y su tamaño reportado.
- **Rationale**: la spec lo fija; los semestres calendario dan ≈ 126 filas y fronteras
  reproducibles.
- **Respaldo**: D1, D2 en `literature-review/decisiones.md` ([15], [16], [18], [19]).
- **Detalle de fuga**: al reentrenar al cierre de la ventana *w*, la fila del último día de *w*
  tiene etiqueta del primer día de *w+1*; se excluye de los datos de entrenamiento.

## R4. Modelos e hiperparámetros (FR-009, FR-010)

- **Decisión**: `Pipeline(StandardScaler, LogisticRegression)` y `RandomForestClassifier`.
  Grids pequeños: LR `C ∈ {0.01, 0.1, 1, 10}`; RF `n_estimators ∈ {100, 300}`,
  `max_depth ∈ {3, 5, 10}`, `min_samples_leaf ∈ {5, 20}`. Se elige el mejor F1 de validación (desempate: grid más simple primero).
  Los hiperparámetros elegidos se **congelan** para A, B y C y para todos los reentrenamientos.
  `class_weight=None`; `random_state = seed`; `n_jobs=1`.
- **Respaldo**: D3 ([13], [20], [22], [23], [19]).

## R5. Deriva (FR-012, FR-012a, FR-016)

- **Decisión**: `evidently` `DataDriftPreset` con `stattest="ks"` por columna y
  `stattest_threshold = 0.05 / K`; hay deriva si alguna columna supera el umbral
  (≡ `min(p) < 0.05/K`). Se guardan los K p-valores. Referencia = features del periodo de
  entrenamiento de la versión vigente. Test unitario compara con `scipy.stats.ks_2samp`.
- **Respaldo**: [9] p. 4 y 6.
- **Riesgo**: la API de Evidently cambia entre versiones; se aísla en `drift.py` y se fija la
  versión en `uv.lock`. Si la API no expone p-valores por columna, se usan los de `ks_2samp` y se documenta.

## R6. Umbral de F1 (FR-013a)

- **Decisión**: por versión, ajustar el modelo en el training sin su hold-out (últimas 63 filas ≈
  un trimestre), predecir el hold-out, remuestrear 1000 veces con reemplazo muestras de tamaño
  126 (una ventana) y calcular `F1_ref = media` y `σ = desviación estándar` del F1 bootstrap.
  Disparo si `F1_ventana < F1_ref − 2σ`. El modelo desplegado es el reajustado con todo el
  periodo de entrenamiento. Para la versión inicial el hold-out es oct–dic 2021.
- **Respaldo**: [6] p. 3 y 6, [12] p. 19.
- **Nota**: remuestreo i.i.d. de pares (y, ŷ); no captura autocorrelación — se declara como amenaza.

## R7. Reentrenamiento (FR-011a, FR-013, FR-014, FR-015)

- **Decisión**: ventana deslizante de 252 filas etiquetadas terminando en la penúltima fila de la
  ventana cerrada; mismo procedimiento para B y C (`retrain(model_config, data)`). La nueva
  versión rige desde la ventana siguiente. Motivos: `inicial`, `deriva`, `caida_f1`, `periodico`
  (si ocurren deriva y caída a la vez, se registran ambos separados por `+`).
- **Respaldo**: D5, D6 ([13] p. 3, [5] p. 11, [6] p. 6–7).

## R8. Baselines (FR-017)

- **Decisión**: `siempre_sube` (predice 1), `persistencia` (predice `1` si `ret_0 > 0`),
  `estratificado` (`numpy.random.default_rng(seed)`, `p` = proporción de “sube” en 2021).
  Se evalúan en cada ventana con las mismas métricas. No dependen de la réplica; se reportan
  una vez y se repiten en ambas tablas.
- **Respaldo**: D4 ([18], [22]).

## R9. Métricas y comparación (FR-018, FR-019a)

- **Decisión**: clase positiva = “sube”; `zero_division=nan`: si no hay predicciones positivas, Precision
  es `NaN` y se marca `precision_indefinida`; igual con Recall/F1 sin positivos reales.
  Wilcoxon pareado (`scipy.stats.wilcoxon`, `zero_method="wilcox"`, dos colas, α = 0,05) sobre
  la diferencia de F1 por ventana; los pares con NaN se excluyen y se reporta `n_efectivo`.
  Se reporta diferencia media y ventanas ganadas.
- **Respaldo**: D7, [6] p. 5, [17].

## R10. Registro y reproducibilidad (Principio II)

- **Decisión**: MLflow con `sqlite:///mlflow.db`. Un experimento; un run padre por réplica con
  semilla, hash del dataset y config; runs hijos por (grupo, ventana) con métricas; cada versión
  de modelo se registra (`msft-{replica}-{grupo}`) con etiquetas de motivo y periodo. Las
  métricas canónicas se escriben también a `results/*.csv` (ordenados, float con `repr`), que es lo
  que comparan los tests de reproducibilidad (MLflow guarda marcas de tiempo, no comparables).

## R11. Validación externa (FR-002)

- **Decisión**: `yfinance` (`MSFT`, cierre ajustado, mismas fechas) en el grupo opcional
  `validation`; `validate-data` descarga, cachea en `data/external/` con su hash y escribe
  `reports/validacion_datos.md` (fechas faltantes/sobrantes, diferencia relativa de precios y de
  volumen con tolerancias fijadas en config). El experimento no depende de la red.
- **Alternativa**: Stooq (CSV público) si Yahoo falla.

## R12. Literatura (US2, FR-020/021)

- **Decisión**: ya existe en `literature-review/` (24 fuentes, matriz, decisiones). No se
  reescribe; un test verifica ≥ 20 referencias, DOI presente en cada una y la existencia de la
  matriz y de las tres áreas. La verificación de que cada DOI resuelve queda como paso manual
  documentado (el test no hace red).
