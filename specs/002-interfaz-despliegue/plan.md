# Implementation Plan: Interfaz web y despliegue

**Branch**: `002-interfaz-despliegue` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## Summary

App web en Streamlit (`app/streamlit_app.py`) con tres páginas: resultados oficiales, comparación
con datos y modelo propios, y metodología. La lógica vive en `src/msft_mlops/custom_run.py`
(testeable, sin dependencia de Streamlit) y reutiliza el walk-forward de la feature 001, que se
generaliza para aceptar un estimador externo como plantilla. Se empaqueta en una imagen Docker
para local (puerto 7860). En la nube se despliega gratis en Streamlit Community Cloud, que instala
solo `app/requirements.txt` e importa el paquete desde `src/` (Hugging Face Spaces Docker exige
PRO desde 2026; su configuración queda como alternativa).

## Technical Context

- **Lenguaje**: Python 3.12 (mismo entorno `uv`).
- **Nuevas dependencias**: `streamlit` (grupo opcional `app`; trae Altair para gráficos) y
  `skops` declarada explícitamente (ya llegaba como dependencia de MLflow) para cargar modelos de
  forma segura.
- **Despliegue**: Docker (`python:3.12-slim` + `uv`) en local; Streamlit Community Cloud (gratis,
  Python 3.12, `app/requirements.txt` con versiones de `uv.lock`) en la nube; Hugging Face Spaces
  (PRO) opcional con `.github/workflows/deploy-hf.yml`.
- **Rendimiento**: una réplica completa (8 ventanas, bootstrap 1000, Evidently) tarda decenas de
  segundos en CPU; los resultados se cachean por (dataset, modelo, parámetros).

## Constitution Check

| Principio | Cumplimiento | Estado |
|---|---|---|
| I. Integridad temporal | Se reutiliza sin cambios el pipeline de features, ventanas, purga y disparadores; la partición de datos subidos sigue la misma regla temporal (FR-104) | ✔ |
| II. Reproducibilidad | Semilla fija; el modelo subido se clona con `random_state = seed`; manifiesto descargable con SHA-256 del dataset. Las ejecuciones de la interfaz no se registran en MLflow: ver *Complexity Tracking* | ◐ |
| III. Comparabilidad | El modelo subido es una réplica más: A, B y C comparten estimador, features, ventanas y métricas; solo cambia la política | ✔ |
| IV. Evidencia y simplicidad | Sin Kubernetes, Kafka, etc.: un contenedor y un servicio gratuito. Docker y Streamlit se justifican por FR-109 (despliegue pedido por el docente) | ✔ |
| Flujo | Spec Kit 002; CI con ruff (lint + formato) y pytest antes del despliegue | ✔ |

## Project Structure

```text
app/
├── streamlit_app.py            # UI: resultados oficiales, comparación propia, metodología
└── requirements.txt            # dependencias mínimas para Streamlit Community Cloud
src/msft_mlops/
├── custom_run.py               # normalizar CSV, partición inferida, carga segura de modelos,
│                               # ejecución personalizada, veredicto, ZIP de resultados
├── models.py / threshold.py / walk_forward.py   # aceptan `estimator=` opcional
tests/unit/test_custom_run.py
tests/integration/test_custom_run_reproduces_official.py   # SC-101 (slow)
Dockerfile, .dockerignore, compose.yaml, .streamlit/config.toml
deploy/huggingface/             # alternativa de pago (Spaces Docker requiere PRO)
├── README.md                   # tarjeta del Space (sdk: docker, app_port: 7860)
├── build_bundle.py             # copia solo lo necesario (sin PDF/DOCX/PNG/notebooks)
└── upload.py                   # sube el bundle al Space con huggingface_hub
.github/workflows/deploy-hf.yml # tras CI verde en main, o manual
docs/DESPLIEGUE.md              # guía paso a paso (local y nube)
```

## Complexity Tracking

| Desviación | Por qué | Alternativa descartada |
|---|---|---|
| Las ejecuciones desde la interfaz no se registran en MLflow (Principio II) | En el Space el disco es efímero y un registro por visitante no aporta trazabilidad; el registro se sustituye por el manifiesto descargable. El experimento oficial (`msft-mlops run`) sigue registrándose en MLflow | Registrar en un MLflow SQLite dentro del contenedor: se pierde en cada reinicio |
| `.skops` en lugar de pickle | Cargar pickle subido por un desconocido ejecuta código arbitrario en el servidor | Aceptar `.pkl`/`.joblib` en público; queda solo para local con `ALLOW_UNSAFE_MODELS=1` |
