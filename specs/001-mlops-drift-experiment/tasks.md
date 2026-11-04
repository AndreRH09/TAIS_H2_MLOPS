---
description: "Lista de tareas para implementar el experimento A/B/C de MLOps sobre MSFT"
---

# Tasks: Experimento modelo estático vs. modelo operado con MLOps

**Input**: Documentos de diseño en `specs/001-mlops-drift-experiment/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Incluidos. La spec y la constitución los exigen: FR-006 (verificación automática
de fuga), SC-003 (reproducibilidad), SC-004 y Principio I (tests de leakage).

**Organization**: Tareas agrupadas por historia de usuario. US2 (literatura) ya está casi
completa; sus tareas hechas aparecen marcadas.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Se puede hacer en paralelo (archivo distinto, sin dependencias pendientes)
- **[Story]**: Historia de usuario (US1, US2, US3)
- Rutas relativas a la raíz del repositorio (proyecto único, layout `src/`)

---

## Phase 1: Setup (infraestructura compartida)

**Purpose**: Inicializar el proyecto Python con uv, el lint, los tests y la CI.

- [ ] T001 Crear `pyproject.toml` (nombre `mlops-exp`, layout `src/`, `requires-python = ">=3.12,<3.13"`) y `.python-version` con `3.12` en la raíz del repositorio
- [ ] T002 Añadir dependencias con uv en `pyproject.toml`: principales `pandas numpy scikit-learn scipy mlflow evidently matplotlib`; grupo `validation`: `yfinance`; grupo `dev`: `pytest ruff`. Generar `uv.lock` con `uv sync --all-groups`
- [ ] T003 [P] Configurar ruff (`line-length = 100`, reglas `E,F,I,B,UP`) y pytest (`testpaths = ["tests"]`) en `pyproject.toml`
- [ ] T004 [P] Crear el paquete vacío `src/mlops_exp/__init__.py` y la carpeta `tests/` con `tests/conftest.py`, que expone un fixture con la ruta de `data/raw/MSFT_5years_cleaned.csv`
- [ ] T005 [P] Crear `.github/workflows/ci.yml`: en `push` y `pull_request`, `ubuntu-latest`, `astral-sh/setup-uv`, `uv sync --all-groups`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest`
- [ ] T006 Crear `src/mlops_exp/run.py` con un CLI `argparse` y los subcomandos `fetch-external`, `validate`, `run` y `report` (sin implementar todavía, salen con código 3), opciones `--config` (por defecto `experiment.toml`), `--out` (por defecto `results/`) y `--no-mlflow`, según `specs/001-mlops-drift-experiment/contracts/cli.md`

---

## Phase 2: Foundational (prerrequisitos que bloquean todas las historias)

**Purpose**: Configuración, datos validados, features sin fuga, ventanas y modelos base.

**⚠️ CRITICAL**: Ninguna historia puede empezar hasta terminar esta fase.

- [ ] T007 Crear `experiment.toml` en la raíz exactamente con el esquema de `specs/001-mlops-drift-experiment/contracts/config.md` (semilla 42, sha256 `1617484d95f94f5968c176246decee0680c39cdb7733b503d73bda03eafe86f7`, `expected_rows = 1254`, KS α = 0,05 + Bonferroni, `k_sigma = 2.0`, `holdout_fraction = 0.2`, `bootstrap_samples = 1000`, Wilcoxon α = 0,05) y un campo `fuente` en cada sección
- [ ] T008 Implementar `src/mlops_exp/config.py`: carga `experiment.toml` con `tomllib`, devuelve un dataclass inmutable (`frozen=True`) y falla con `SystemExit(2)` si falta una sección, un valor o el campo `fuente`. No hay parámetros por grupo
- [ ] T009 Implementar `src/mlops_exp/data.py`: `load_raw(cfg)` verifica el SHA-256 (si no coincide, `SystemExit(1)`) y valida las reglas de data-model.md: `date` única y estrictamente creciente; `open, high, low, close > 0`; `low ≤ open, close ≤ high`; `volume > 0`; 1 254 filas entre 2021-02-04 y 2026-02-02; sin nulos en OHLCV. Usa solo `date, open, high, low, close, volume`
- [ ] T010 [P] Escribir `tests/test_data.py`: hash correcto pasa; un archivo con un byte alterado (en `tmp_path`) sale con código 1; las reglas OHLC detectan una fila inválida sintética
- [ ] T011 Implementar `src/mlops_exp/features.py`: `build_features(df)` con las 6 features relativas de research.md R2 (`ret_1, ret_2, ret_5, px_sma5, px_sma20, vol_sma20`) y la etiqueta `y = 1 si close(t+1) > close(t)`. Descarta las primeras 20 filas y la última
- [ ] T012 [P] Escribir `tests/test_features.py`: (a) invariante de no fuga: alterar todos los precios posteriores a una fecha `d` no cambia las features de `d`; (b) todas las features son adimensionales, es decir, multiplicar precios y volumen por 10 no las cambia; (c) `y` coincide con el signo de `close.shift(-1) - close`
- [ ] T013 Implementar `src/mlops_exp/windows.py`: `test_windows()` devuelve las 8 ventanas semestrales `2022-H1 … 2025-H2` (`window_id`, `index` 0–7, `start`, `end`, `n`); `excluded_tail(df)` devuelve el tamaño del tramo 2026-01-01 → 2026-02-02; `retrain_slice(features, k)` devuelve las ventanas k−1 y k purgando el último día (`purge_days = 1`, research.md R5)
- [ ] T014 [P] Escribir `tests/test_windows.py`: 8 ventanas sin solape ni huecos; ninguna fila de 2026 en las ventanas; el reentrenamiento tras la ventana k termina antes del primer día de k+1 y no incluye el último día de k
- [ ] T015 Implementar `src/mlops_exp/models.py`: `make_model(replica, params, seed)` (LR = `Pipeline(StandardScaler, LogisticRegression)`; RF = `RandomForestClassifier(n_estimators=300, random_state=seed)`); `tune(replica, features, cfg)`, que entrena con feb–sep 2021, elige por F1 en oct–dic 2021 y devuelve hiperparámetros **congelados**; `baselines(seed)` con `always_up` y `stratified` (`DummyClassifier`) y `persistence` (`y_hat = ret_1 > 0`)
- [ ] T016 Implementar `src/mlops_exp/validate_external.py` y los subcomandos `fetch-external` y `validate` en `src/mlops_exp/run.py`: `fetch-external` descarga MSFT diario **ajustado** con `yfinance` para el rango del dataset y escribe `data/external/msft_yahoo_adjusted.csv` y `.sha256`; `validate` compara fechas y cierre (tolerancia relativa 0,5 %) y escribe `results/data_validation.md` según contracts/outputs.md; sin snapshot, código 3
- [ ] T017 Ejecutar `uv run python -m mlops_exp.run fetch-external` una vez y `validate`, revisar `results/data_validation.md` y versionar `data/external/` y el reporte. Si hay discrepancias > 0,5 %, documentarlas y resolverlas antes de seguir (FR-002)

**Checkpoint**: datos verificados, features y ventanas probadas sin fuga. Pueden empezar las historias.

---

## Phase 3: User Story 1 — Ejecutar el experimento walk-forward A vs. B vs. C (Priority: P1) 🎯 MVP

**Goal**: Con un solo comando se obtienen las métricas por ventana de A, B, C y los baselines
en ambas réplicas, con cada versión de modelo registrada.

**Independent Test**: `uv run python -m mlops_exp.run run` produce `results/window_metrics.csv`
con 96 filas y `results/model_versions.csv` en el que A tiene 1 versión por réplica y C tiene
9; dos ejecuciones dan métricas idénticas.

### Tests for User Story 1

- [ ] T018 [P] [US1] Escribir `tests/test_drift.py`: datos idénticos → sin deriva; una feature desplazada 3σ → deriva; 6 features con p apenas menores a 0,05 pero mayores a 0,05/6 → **sin** deriva (verifica Bonferroni); devuelve `min_p` y `alpha_k = 0.05/K`
- [ ] T019 [P] [US1] Escribir `tests/test_trigger.py`: `threshold = f1_ref − 2·sigma`; con la misma semilla, el bootstrap da el mismo σ; política A nunca reentrena; B reentrena si `drift` **o** `f1 < threshold`, y no en otro caso; C reentrena siempre; la nueva versión se usa desde la ventana k+1, nunca en la k
- [ ] T020 [P] [US1] Escribir `tests/test_reproducibility.py`: ejecuta `run --no-mlflow` dos veces sobre `tmp_path/r1` y `tmp_path/r2` y compara `window_metrics.csv` byte a byte (SC-003)

### Implementation for User Story 1

- [ ] T021 [P] [US1] Implementar `src/mlops_exp/drift.py`: `detect(ref_X, win_X, alpha)` con `scipy.stats.ks_2samp` por feature y Bonferroni (`drift = min(p) < alpha/K`). Devuelve `drift_detected`, `min_p`, `alpha_k` y los p-valores por feature (FR-012a)
- [ ] T022 [P] [US1] Añadir a `src/mlops_exp/drift.py` `evidently_report(ref_X, win_X, path)`, que genera el HTML de deriva de Evidently solo como artefacto. No interviene en la decisión (research.md R3)
- [ ] T023 [US1] Implementar `src/mlops_exp/trigger.py`: `reference(model_factory, train_X, train_y, cfg, seed)`, que entrena con el primer 80 % temporal, evalúa en el último 20 % y estima σ con 1 000 remuestras bootstrap del tamaño medio de ventana (research.md R4); y las políticas `policy_A`, `policy_B` y `policy_C`, con motivos `initial | drift | f1_drop | drift+f1_drop | scheduled` según data-model.md
- [ ] T024 [US1] Implementar `src/mlops_exp/experiment.py`: para cada réplica (`lr`, `rf`), ajustar hiperparámetros (T015), entrenar el modelo inicial con todo 2021 (FR-009) y recorrer las 8 ventanas. Por ventana: predecir con la versión vigente de A, B y C; calcular precision, recall y F1 con positivo = "sube" (`NaN` explícito si hay una sola clase); evaluar deriva frente a los datos de entrenamiento de la versión vigente (FR-016); aplicar la política y, si corresponde, reentrenar con `retrain_slice` para la ventana siguiente. Incluye los 3 baselines
- [ ] T025 [US1] Escribir en `src/mlops_exp/experiment.py` las salidas `window_metrics.csv` (96 filas) y `model_versions.csv` con exactamente las columnas de contracts/outputs.md, incluidas `seed` y `data_sha256`, en la carpeta `--out`
- [ ] T026 [US1] Añadir el registro en MLflow en `src/mlops_exp/experiment.py` (se omite con `--no-mlflow`): tracking `sqlite:///mlflow.db`, experimento `msft-drift`, runs anidados por réplica × grupo, métricas con `step = window_index`, Model Registry `msft-{replica}-{group}` con tags `reason, train_start, train_end, f1_ref, sigma, data_sha256`, y el HTML de Evidently como artefacto (research.md R8)
- [ ] T027 [US1] Conectar el subcomando `run` en `src/mlops_exp/run.py` con `experiment.py`
- [ ] T028 [US1] Ejecutar `uv run python -m mlops_exp.run run`, comprobar los invariantes de contracts/outputs.md (96 filas; A con 1 versión y C con 9 por réplica; ningún `train_end` ≥ inicio de su ventana) y versionar `results/window_metrics.csv` y `results/model_versions.csv`

**Checkpoint**: US1 funciona y es reproducible. Este es el MVP.

---

## Phase 4: User Story 2 — Contrastar el diseño con la literatura (Priority: P2)

**Goal**: Bibliografía de ≥ 20 fuentes revisadas por pares con DOI verificado y matriz de
contraste legible en el repositorio.

**Independent Test**: abrir `literature-review/referencias.md` y verificar que cada fuente
tiene referencia IEEE con DOI que resuelve y una fila en la matriz o una decisión asociada.

- [x] T029 [US2] Bibliografía IEEE de 24 fuentes verificadas en `literature-review/referencias.md`
- [x] T030 [US2] Decisiones D1–D7 con respaldo en `literature-review/decisiones.md`
- [x] T031 [US2] Matriz de contraste en `literature-review/matriz-contraste.md`
- [x] T032 [US2] Citas textuales de los 4 papers más cercanos en `literature-review/evidencia-clave.md` y guías de lectura en `literature-review/lecturas/`
- [ ] T033 [US2] Integrar en `literature-review/matriz-contraste.md` y `literature-review/decisiones.md` los entregables de lectura de Andre, Frank, Willy y Paul, y resolver las celdas marcadas con ⚠ con la página exacta del PDF
- [ ] T034 [P] [US2] Añadir a `literature-review/decisiones.md` las decisiones técnicas que necesitan respaldo y que surgieron en el plan (purga de 1 día, hiperparámetros congelados, σ por bootstrap) con su fuente, o marcarlas como "decisión propia" si no la hay

**Checkpoint**: US2 completa. Cada parámetro de `experiment.toml` remite a una fuente (SC-006).

---

## Phase 5: User Story 3 — Analizar y reportar la comparación (Priority: P3)

**Goal**: Reporte comparativo con la evolución de F1, las diferencias B−A, C−A y B−C, el test
de Wilcoxon, los reentrenamientos y las amenazas a la validez.

**Independent Test**: `uv run python -m mlops_exp.run report` genera `results/comparison.csv`
(6 filas) y `results/report.md` con la figura de F1 por ventana y la lista de reentrenamientos.

### Tests for User Story 3

- [ ] T035 [P] [US3] Escribir `tests/test_report.py`: con un `window_metrics.csv` sintético en que B gana las 8 ventanas, `compare()` da `windows_won = 8` y un `wilcoxon_p` igual a `scipy.stats.wilcoxon` sobre las mismas diferencias; con diferencias nulas, reporta el `n_effective` correcto

### Implementation for User Story 3

- [ ] T036 [US3] Implementar `src/mlops_exp/report.py` `compare(window_metrics, cfg)`: para cada réplica y par (`B-A`, `C-A`, `B-C`), calcular `mean_diff_f1`, `windows_won`, `n_effective`, `wilcoxon_p` (pareado, bilateral) y `significant` (`p < 0.05`), y escribir `comparison.csv` según contracts/outputs.md (FR-019a)
- [ ] T037 [US3] Implementar en `src/mlops_exp/report.py` la figura `results/figures/f1_by_window_{replica}.png` con matplotlib: F1 por ventana de A, B, C y baselines, con los reentrenamientos de B y C marcados y el motivo en la leyenda
- [ ] T038 [US3] Implementar en `src/mlops_exp/report.py` la generación de `results/report.md` con el contenido listado en contracts/outputs.md: configuración y hash, tabla de F1, tabla de comparación, reentrenamientos con motivo, tramo excluido y amenazas a la validez (un activo, n = 8 y baja potencia, autocorrelación en KS, σ con hold-out pequeño, regresión vs. clasificación en [6] y [13])
- [ ] T039 [US3] Conectar el subcomando `report` en `src/mlops_exp/run.py`, ejecutarlo y versionar `results/comparison.csv`, `results/report.md` y `results/figures/`

**Checkpoint**: las tres historias funcionan de forma independiente.

---

## Phase 6: Polish & cross-cutting concerns

- [ ] T040 [P] Crear `README.md` en la raíz: objetivo, estructura del repositorio, enlaces a la spec, el plan, la literatura y el quickstart, atribución del dataset (CC BY 4.0) y cómo citar
- [ ] T041 [P] Ejecutar `uv run ruff format .` y `uv run ruff check --fix .` y dejar la CI en verde en GitHub Actions
- [ ] T042 Seguir `specs/001-mlops-drift-experiment/quickstart.md` desde un clon limpio, cronometrar (SC-007 < 30 min) y corregir cualquier paso que falle
- [ ] T043 Verificar SC-008 con `git log -- experiment.toml`: el archivo no cambió después del commit de la primera ejecución sobre la prueba (o cada cambio tiene su justificación)
- [ ] T044 Abrir el Pull Request de `001-mlops-drift-experiment` a `main` con el resumen de resultados (sin atribución de Claude)

---

## Dependencies & execution order

### Phase dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup y **bloquea** US1 y US3.
- **US1 (Phase 3)**: depende de Foundational. Es el MVP.
- **US2 (Phase 4)**: independiente del código. T033 depende de que el equipo entregue las
  lecturas.
- **US3 (Phase 5)**: necesita `window_metrics.csv` de US1 para T039. T035–T038 se pueden
  desarrollar antes con datos sintéticos.
- **Polish (Phase 6)**: depende de US1 y US3.

### Within each story

- Los tests se escriben primero y deben fallar antes de implementar (T018–T020 antes de
  T021–T027; T035 antes de T036).
- `drift.py` y `trigger.py` antes de `experiment.py`; `experiment.py` antes del subcomando
  `run`.

### Orden crítico

```text
T001 → T002 → T006 → T007 → T008 → T009 → T011 → T013 → T015 → T023 → T024 → T025 → T027 → T028 → T036 → T039
```

---

## Parallel execution examples

**Phase 1:** T003, T004 y T005 a la vez (archivos distintos).

**Phase 2** (después de T008, T009, T011 y T013 respectivamente):

```text
T010 tests/test_data.py      ∥  T012 tests/test_features.py  ∥  T014 tests/test_windows.py
```

**US1:**

```text
T018 tests/test_drift.py  ∥  T019 tests/test_trigger.py  ∥  T020 tests/test_reproducibility.py
T021 drift.py (KS)        ∥  T022 drift.py (Evidently)*
```

\* T021 y T022 tocan el mismo archivo: en paralelo solo si se coordinan; si no, en secuencia.

**Equipo:** US2 (T033, T034) puede avanzar en paralelo a todo el código.

---

## Implementation strategy

### MVP first (US1)

1. Phase 1 → Phase 2. Validar los datos (T017) **antes** de cualquier ejecución sobre la
   prueba.
2. Congelar `experiment.toml` con un commit (SC-008).
3. Phase 3 (US1) → **parar y validar**: invariantes, reproducibilidad, primera mirada en MLflow.

### Incremental delivery

1. Setup + Foundational → base lista.
2. US1 → métricas A/B/C (MVP).
3. US3 → comparación y reporte.
4. US2 → integrar las lecturas del equipo (en paralelo).
5. Polish → README, quickstart probado, PR.

### Reparto sugerido (4 integrantes)

| Integrante | Tareas |
|---|---|
| Andre | Setup (T001–T006), config (T007–T008), MLflow (T026), PR (T044) |
| Frank | Datos y validación externa (T009–T010, T016–T017), drift (T018, T021–T022) |
| Willy | Features y ventanas (T011–T014), trigger (T019, T023) |
| Paul | Modelos (T015), experimento (T024–T025, T027–T028), reporte (T035–T039) |

Todos: T033 (lecturas) y revisión cruzada de PRs.
