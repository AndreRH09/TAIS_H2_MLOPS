# Tasks: Interfaz web y despliegue

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Fundamentos

- [X] T101 Añadir `streamlit` (grupo `app`) y `skops` (dependencia explícita) con `uv add`
- [X] T102 Generalizar `make_model`, `fit_model`, `select_hyperparameters`,
  `f1_reference_and_sigma` y `run_replica` con un `estimator=` opcional (plantilla clonada con la
  semilla), sin cambiar los resultados oficiales

## Phase 2: US1 + US2 — núcleo (`src/msft_mlops/custom_run.py`)

- [X] T103 `normalize_prices`: reconoce nombres habituales de columnas, ordena por fecha y calcula
  `price_change*` si faltan; luego `validate_integrity`
- [X] T104 `infer_split` (FR-104) y test de que reproduce la partición oficial con el dataset del
  proyecto
- [X] T105 `load_model_bytes` (FR-105): `.skops` con lista blanca de tipos; pickle solo con
  `ALLOW_UNSAFE_MODELS=1`; comprobación de que es un clasificador
- [X] T106 `run_custom_experiment` (FR-106, FR-107) y `results_zip` con manifiesto (FR-108)
- [X] T107 `verdict` (FR-102): F1 medio, mejor política, Wilcoxon, reentrenamientos, baseline
- [X] T108 Tests unitarios (`tests/unit/test_custom_run.py`) y test lento SC-101
  (`tests/integration/test_custom_run_reproduces_official.py`)

## Phase 3: Interfaz (`app/streamlit_app.py`)

- [X] T109 Página "Resultados del proyecto" (US1) con veredicto, F1 por ventana, diferencias,
  Wilcoxon, reentrenamientos, deriva y tramo reciente exploratorio
- [X] T110 Página "Comparar con tus datos" (US2): dataset propio o del proyecto, modelos del
  proyecto y/o modelo propio o de ejemplo, parámetros, ejecución cacheada y descarga
- [X] T111 Página "Metodología": políticas, métricas y amenazas a la validez

## Phase 4: US3 — despliegue

- [X] T112 `Dockerfile` (usuario no root, puerto 7860), `.dockerignore`, `compose.yaml`,
  `.streamlit/config.toml`
- [X] T113 `deploy/huggingface/` (tarjeta del Space, `build_bundle.py`, `upload.py`) y
  `.github/workflows/deploy-hf.yml` tras CI verde
- [X] T114 `docs/DESPLIEGUE.md` y sección del README
- [X] T117 Hugging Face exige PRO para Spaces Docker: `app/requirements.txt` + importación desde
  `src/` para Streamlit Community Cloud, verificado en un contenedor limpio con solo esas
  dependencias

## Phase 5: Verificación

- [X] T115 ruff (lint + formato) y pytest completos
- [X] T116 Levantar la interfaz en local y recorrer las tres páginas
