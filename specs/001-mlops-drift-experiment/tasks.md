---

description: "Tareas del experimento modelo estático vs. modelo operado con MLOps"
---

# Tasks: Experimento modelo estático vs. modelo operado con MLOps

**Input**: documentos de diseño en `/specs/001-mlops-drift-experiment/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-and-outputs.md, quickstart.md

**Tests**: se incluyen. La constitución (Principio I y II) exige tests automatizados de fuga y de
reproducibilidad, y CI con pytest.

**Organization**: por historia de usuario (US1 P1, US2 P2, US3 P3). Paquete `src/msft_mlops/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: paralelizable (archivos distintos, sin dependencias pendientes)
- Todas las rutas son relativas a la raíz del repositorio

---

## Phase 1: Setup

- [X] T001 Crear `pyproject.toml` (paquete `msft-mlops`, `requires-python = ">=3.12,<3.13"`, dependencias `scikit-learn`, `pandas<3`, `numpy`, `scipy`, `evidently`, `mlflow`, `matplotlib`; grupo `dev` con `pytest`, `ruff`; grupo `validation` con `yfinance`; entrada de script `msft-mlops = "msft_mlops.cli:main"`; config de ruff y pytest) y ejecutar `uv sync` para generar `uv.lock`
- [X] T002 [P] Crear la estructura de directorios y `__init__.py` en `src/msft_mlops/`, `tests/unit/`, `tests/integration/`, `tests/docs/`, `config/`, `results/`, `reports/`, `data/external/` (con `.gitkeep` donde esté vacío)
- [X] T003 [P] Crear `.github/workflows/ci.yml`: en `push`/`pull_request`, `astral-sh/setup-uv`, `uv sync`, `uv run ruff check .`, `uv run pytest`
- [X] T004 [P] Ampliar `.gitignore` con `results_check/`, `data/external/*.csv`, `.pytest_cache/`, `.ruff_cache/`

---

## Phase 2: Foundational (bloquea todas las historias)

- [X] T005 Crear `config/experiment.toml` con: `[data]` ruta y `sha256 = "1617484d95f94f5968c176246decee0680c39cdb7733b503d73bda03eafe86f7"`; `[run] seed = 42`; `[split]` ajuste 2021-02-04…2021-09-30, validación 2021-10-01…2021-12-31, ventanas semestrales 2022-H1…2025-H2, cola excluida desde 2026-01-01; `[features]` lags 4, medias 5/10/20, `vol_ma = 20`; `[models.logreg]` `C=[0.01,0.1,1,10]`; `[models.rf]` `n_estimators=[100,300]`, `max_depth=[3,5,10]`, `min_samples_leaf=[5,20]`; `[drift] alpha=0.05, test="ks", correction="bonferroni"`; `[f1_trigger] k_sigma=2, holdout_rows=63, n_bootstrap=1000, resample_size=126`; `[retrain] window_rows=252`; `[validation]` tolerancias (precio 0.5 %, volumen 5 %)
- [X] T006 Implementar `src/msft_mlops/config.py`: dataclasses tipadas + `load_config(path)` con `tomllib`; valida que `k_sigma`, `alpha`, `window_rows` existan y sean positivos
- [X] T007 [P] Implementar `src/msft_mlops/data.py` (FR-001, FR-003): `sha256_file`, `load_raw(config)` que **falla con `DataHashMismatch` (código de salida 2)** si el hash no coincide; `validate_integrity(df)` (fechas únicas y crecientes; sin nulos salvo `price_change`/`price_change_pct` de la primera fila; `high ≥ max(open, close)`, `low ≤ min(open, close)`, `volume > 0`; lista huecos de calendario > 4 días) que lanza `DataValidationError` (código 3)
- [X] T008 [P] Implementar `src/msft_mlops/features.py` (FR-004, FR-005, FR-006a): `build_dataset(df)` devuelve índice `date`, columnas `ret_0, ret_1, ret_2, ret_3, ret_4, ma5_rel, ma10_rel, ma20_rel, vol_rel` (K = 9) y `y = 1 si close_{t+1} > close_t`; rendimientos recalculados desde `close`; `ma_n_rel = close / SMA_n − 1`; `vol_rel = volume / SMA20(volume) − 1`; descarta las 20 primeras filas y la última, sin relleno. Constante `FEATURE_COLUMNS`
- [X] T009 [P] Implementar `src/msft_mlops/windows.py` (FR-007, FR-008): `split_2021(ds)` → (ajuste, validación, entrenamiento_inicial); `test_windows(ds)` → lista de 8 `Window(window_id, start, end, index)` por semestre calendario; `excluded_tail(ds)` con su tamaño; función `last_year_training(ds, window)` que devuelve las últimas 252 filas **hasta la penúltima fila de la ventana** (la última fila tiene etiqueta del día siguiente a la ventana)
- [X] T010 [P] Implementar `src/msft_mlops/metrics.py` (FR-018): `window_scores(y_true, y_pred)` con Precision/Recall/F1 de la clase "sube" (1), `zero_division=np.nan`, y banderas `precision_undefined`, `recall_undefined`, `f1_undefined`, más `n_pos_true`, `n_pos_pred`
- [X] T011 Implementar `src/msft_mlops/models.py` (FR-009, FR-010): `make_model(replica, params, seed)` (`Pipeline(StandardScaler, LogisticRegression(max_iter=1000))` para `logreg`; `RandomForestClassifier(n_jobs=1)` para `rf`, ambos con `random_state=seed`); `select_hyperparameters(replica, fit_df, val_df, grid, seed)` elige el mejor F1 de validación (desempate: primera combinación del grid); `fit_model(replica, params, seed, X, y)`
- [X] T012 [P] Tests unitarios fundacionales: `tests/unit/test_data.py` (hash incorrecto → `DataHashMismatch`; CSV real pasa la validación; 1254 filas), `tests/unit/test_features.py`, `tests/unit/test_windows.py` (8 ventanas, ≈ 126 filas, sin solapamiento, orden temporal, tamaño del tramo excluido ≈ 22, penúltima fila), `tests/unit/test_metrics.py` (sin positivos predichos → `precision` NaN + bandera, no 0)
- [X] T013 Test de fuga `tests/unit/test_leakage.py` (FR-006, SC-004, Principio I): (a) para cada fecha *t* de una muestra, las features calculadas con la serie truncada en *t* son idénticas a las de la serie completa; (b) perturbar `close`/`volume` posteriores a *t* no cambia las features de *t*; (c) ninguna feature es igual a la etiqueta ni correlaciona con `y` de forma exacta; (d) `y` de *t* depende del cierre de *t+1* (comprobación del desplazamiento)

**Checkpoint**: cargar datos, features, ventanas y modelos funcionan y los tests de fuga pasan.

---

## Phase 3: User Story 1 — Ejecutar el experimento walk-forward A vs. B vs. C (P1) 🎯 MVP

**Goal**: ejecutar con un comando las dos réplicas, con A, B, C y tres baselines por ventana, y registrar versiones y runs.

**Independent Test**: `uv run msft-mlops run` genera `results/window_metrics.csv` (96 filas), `results/model_versions.csv` y los runs en MLflow; dos ejecuciones producen CSV idénticos.

### Tests para US1

- [X] T014 [P] [US1] `tests/unit/test_drift.py` (FR-012a): con datos sintéticos, `detect_drift` coincide con `min(scipy.stats.ks_2samp p) < 0.05/K` para casos con y sin deriva; devuelve los K p-valores y la decisión
- [X] T015 [P] [US1] `tests/unit/test_threshold.py` (FR-013a): `f1_reference_and_sigma` es determinista con la misma semilla, `sigma > 0`, y `f1_ref` cercano al F1 observado del hold-out
- [X] T016 [P] [US1] `tests/unit/test_policies.py` (FR-011, FR-011a, FR-013): `should_retrain` de A siempre `None`; de C siempre `"periodico"`; de B `None` sin deriva y con F1 sobre el umbral, `"deriva"`, `"caida_f1"` o `"deriva+caida_f1"` según el caso
- [X] T017 [P] [US1] `tests/unit/test_baselines.py` (FR-017): "siempre sube" predice 1; persistencia predice `ret_0 > 0`; estratificado es determinista con semilla y respeta la proporción de 2021
- [X] T018 [US1] `tests/integration/test_walk_forward.py`: sobre un dataset sintético con cambio de régimen verifica: A conserva la versión 1; C crea una versión por ventana; una versión creada tras la ventana *w* se usa desde *w+1* y nunca en *w*; B no reentrena en una ventana sin deriva y sin caída; el reentrenamiento tras la última ventana se registra sin evaluarse; el conjunto de entrenamiento de cada versión no incluye fechas posteriores al cierre de la ventana que la disparó
- [X] T019 [US1] `tests/integration/test_reproducibility.py` (SC-003): ejecuta `run_experiment` dos veces con la misma config y semilla en directorios distintos y comprueba que los CSV de `results/` son idénticos byte a byte

### Implementación de US1

- [X] T020 [P] [US1] Implementar `src/msft_mlops/drift.py` (FR-012, FR-012a, FR-016): `detect_drift(reference_df, window_df, alpha)` con Evidently (`stattest="ks"`, `stattest_threshold = alpha / K`) que devuelve `DriftResult(drifted, min_p, threshold, per_feature)`; si Evidently no expone p-valores por columna, calcula con `scipy.stats.ks_2samp` y documenta la razón en el docstring
- [X] T021 [P] [US1] Implementar `src/msft_mlops/threshold.py` (FR-013a): `f1_reference_and_sigma(model_factory, train_df, holdout_rows, n_bootstrap, resample_size, seed)` ajusta sin el hold-out (últimas 63 filas), predice el hold-out, remuestrea con reemplazo `n_bootstrap` veces tamaño `resample_size` y devuelve `(f1_ref = media, sigma = desviación estándar)`; excluye remuestras con F1 indefinido y lo reporta
- [X] T022 [P] [US1] Implementar `src/msft_mlops/baselines.py` (FR-017): `predict_siempre_sube`, `predict_persistencia`, `predict_estratificado(n, p_up, rng)`
- [X] T023 [US1] Implementar `src/msft_mlops/policies.py` (FR-011, FR-011a, FR-013): clases/funciones `PolicyA`, `PolicyB`, `PolicyC` con `should_retrain(window_scores, drift_result, version) -> reason | None`; la única diferencia entre grupos vive aquí (Principio III)
- [X] T024 [US1] Implementar `src/msft_mlops/walk_forward.py` (FR-009 a FR-016, FR-018): `run_replica(replica, ds, config, tracker)` → selecciona hiperparámetros (ajuste feb–sep, validación oct–dic), entrena la versión inicial con todo 2021 y calcula `f1_ref`/`σ` (hold-out oct–dic) para A, B y C con el mismo modelo inicial; por cada ventana evalúa los tres grupos y los baselines, calcula la deriva contra la referencia de la versión vigente, aplica la política y, si corresponde, reentrena con `last_year_training` (misma función para B y C), recalcula referencia, `f1_ref` y `σ`, y activa la versión desde la ventana siguiente. Devuelve los DataFrames de `window_metrics`, `model_versions` y `drift_details`
- [X] T025 [P] [US1] Implementar `src/msft_mlops/tracking.py` (Principio II): `Tracker` con MLflow `sqlite:///mlflow.db`, experimento `msft-mlops`; run padre por réplica (`seed`, `data_sha256`, config), runs hijos por grupo/ventana con `precision`, `recall`, `f1`, registro de cada versión de modelo `msft-{replica}-{grupo}` con etiquetas `reason`, `train_start`, `train_end`; un `NullTracker` para tests
- [X] T026 [US1] Implementar `src/msft_mlops/results_io.py` y `run_experiment(config_path, results_dir)` en `src/msft_mlops/cli.py`: orquesta carga → validación → features → `run_replica` para `logreg` y `rf` → escritura ordenada y estable de `results/window_metrics.csv`, `model_versions.csv`, `drift_details.csv`, `run_manifest.json` (semilla, hash de datos, versiones de librerías, hash de cada CSV); `main()` con `argparse` y subcomando `run` y códigos de salida 0/2/3
- [X] T027 [US1] Ejecutar `uv run pytest` y `uv run msft-mlops run`; comprobar 96 filas en `window_metrics.csv` (8 × 6 grupos × 2 réplicas), sin NaN silenciosos y que las versiones de B/C coinciden con las banderas de reentrenamiento

**Checkpoint**: US1 funcional y reproducible; es el MVP.

---

## Phase 4: User Story 2 — Contrastar el diseño con la literatura (P2)

**Goal**: la bibliografía y la matriz están en el repositorio y se verifican automáticamente; los datos se validan contra una fuente externa.

**Independent Test**: `uv run pytest tests/docs` pasa; `validate-data` produce el informe.

- [X] T028 [P] [US2] `tests/docs/test_literature.py` (FR-020, FR-021, SC-005): `literature-review/referencias.md` tiene ≥ 20 entradas, cada una con DOI o URL de fuente editorial, años 2015–2026, y cubre los ejes A, B y C; existen `matriz-contraste.md` con las dimensiones obtención de datos, partición, baseline, disparador y métricas, y `decisiones.md` con D1–D7
- [X] T029 [P] [US2] Implementar `src/msft_mlops/external_validation.py` (FR-002): descarga con `yfinance` el cierre ajustado, apertura/máximo/mínimo y volumen de MSFT para el rango del CSV, cachea en `data/external/msft_yahoo.csv` con su SHA-256, compara fechas faltantes/sobrantes y diferencias relativas de precio y volumen contra las tolerancias de config y escribe `reports/validacion_datos.md`; código de salida 4 si superan la tolerancia
- [X] T030 [US2] Añadir el subcomando `validate-data` a `src/msft_mlops/cli.py` y ejecutarlo (`uv sync --group validation`); si hay discrepancias, documentarlas en `reports/validacion_datos.md` y en `data/raw/README.md`; si la red o Yahoo no están disponibles, dejar constancia explícita en el informe de que **no** se pudo validar
- [X] T031 [US2] Enlazar cada parámetro de `config/experiment.toml` con su decisión (D1–D7) en comentarios del TOML y en una sección "Trazabilidad con la literatura" de `reports/resumen.md` (SC-006)

**Checkpoint**: US2 verificable de forma independiente.

---

## Phase 5: User Story 3 — Analizar y reportar la comparación (P3)

**Goal**: resumen comparativo con series de P/R/F1, diferencias, Wilcoxon y reentrenamientos.

**Independent Test**: `uv run msft-mlops report` genera `reports/resumen.md` a partir de `results/` sin reejecutar.

- [X] T032 [P] [US3] `tests/unit/test_report.py` (FR-019a): Wilcoxon sobre diferencias conocidas coincide con `scipy.stats.wilcoxon`; los pares con NaN se excluyen y se reporta `n_effective`; diferencias todas cero no rompen; cuenta correctamente ventanas ganadas/perdidas/empatadas
- [X] T033 [US3] Implementar `src/msft_mlops/report.py` (FR-019, FR-019a): `compare_groups` (B−A, C−A, B−C por réplica: diferencia media, ventanas ganadas, Wilcoxon bilateral `zero_method="wilcox"`, α = 0,05) → `results/comparisons.csv`; `write_summary` → `reports/resumen.md` con tablas P/R/F1 por ventana (A, B, C, baselines) por réplica, reentrenamientos de B y C (ventana y motivo), deriva por ventana, tamaño del tramo excluido, y amenazas a la validez (un activo, n = 8 con baja potencia del Wilcoxon, bootstrap i.i.d., ajuste por dividendos, métricas bajas esperables)
- [X] T034 [P] [US3] Generar figuras con matplotlib en `reports/f1_por_ventana_{logreg,rf}.png` (serie de F1 de A, B, C y baselines; marcas en los reentrenamientos)
- [X] T035 [US3] Añadir el subcomando `report` a `src/msft_mlops/cli.py` e invocar la generación de reporte al final de `run`; regenerar `results/` y `reports/` y revisar que el resumen contiene la serie de F1 de los tres grupos y la lista de reentrenamientos

**Checkpoint**: las tres historias funcionan.

---

## Phase 6: Polish

- [X] T036 [P] Crear `README.md` raíz en español: objetivo, estructura, `uv sync`, comandos de `quickstart.md`, enlace a la literatura y a la spec
- [X] T037 Ejecutar la validación de `quickstart.md` completa (ruff, pytest, `run`, segunda ejecución a `results_check/` y comparación de hashes) y corregir lo que falle
- [X] T038 Ejecutar `uv run ruff check . && uv run ruff format --check .`; corregir hallazgos
- [X] T039 Actualizar el estado de `specs/001-mlops-drift-experiment/spec.md` a `Implemented` solo si T037 pasó y registrar en `reports/resumen.md` las limitaciones conocidas (p. ej. validación externa no realizada si no hubo red)

---

## Dependencies & Execution Order

- Setup (T001–T004) → Foundational (T005–T013) → US1 → US2/US3 → Polish.
- Dentro de Foundational: T005→T006; T007, T008, T009, T010 en paralelo tras T006; T011 tras T008/T009; T012–T013 tras sus módulos.
- US1: T014–T017 (tests) en paralelo antes de T020–T022; T023 tras T020/T021; T024 tras T020–T023 y T011; T025 en paralelo con T023; T026 tras T024/T025; T018/T019 requieren T024/T026; T027 al final.
- US2 es independiente de US1 salvo T031, que necesita el resumen (T033).
- US3 depende de los CSV de US1 (T026).

## Parallel Example: US1

```text
T014 test_drift.py   T015 test_threshold.py   T016 test_policies.py   T017 test_baselines.py
T020 drift.py        T021 threshold.py        T022 baselines.py
```

## Implementation Strategy

1. MVP = Setup + Foundational + US1: A/B/C reproducibles y registrados.
2. Añadir US3 (reporte) para obtener las conclusiones.
3. US2 (verificación de literatura y validación externa) puede avanzar en paralelo.
4. No ejecutar el experimento sobre 2022+ hasta confirmar `config/experiment.toml` (SC-008): se hace commit de la config antes de la primera ejecución completa.

## Notes

- Commits por grupo lógico en la rama `001-mlops-drift-experiment`; `main` no recibe commits directos.
- Los CSV de `results/` se versionan; `mlflow.db` no.
