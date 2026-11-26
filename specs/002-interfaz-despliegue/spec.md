# Feature Specification: Interfaz web y despliegue del comparador de políticas MLOps

**Feature Branch**: `002-interfaz-despliegue`

**Created**: 2026-11-19

**Status**: Implemented

**Amendment (2026-11-19)**: Hugging Face Spaces dejó de ofrecer Spaces Docker en el plan gratuito
(`402 Payment Required`, requiere PRO). El destino gratuito en la nube pasa a ser **Streamlit
Community Cloud**; la imagen Docker se mantiene para local y como alternativa de pago.

**Input**: Solicitud del docente: "una interfaz en la que se pueda subir su modelo, su base de
datos, etc.; primero lo que ya tenemos (nuestra base y nuestros modelos)". Desplegarla en local y
en un servicio gratuito en la nube. El propósito no cambia: comparar qué política es más efectiva
entre el modelo **estático (A)**, el reentrenado **con alarmas (B)** y el reentrenado **cada seis
meses (C)**.

## User Scenarios & Testing *(mandatory)*

Actor principal: **evaluador** (docente) que revisa el experimento desde el navegador, sin
instalar nada. Actor secundario: **investigador** (equipo) que lo ejecuta en local.

### User Story 1 - Ver los resultados oficiales del proyecto (Priority: P1)

El evaluador abre la interfaz y ve, sin ejecutar nada, los resultados oficiales del experimento
con nuestro dataset (MSFT 2021–2026) y nuestros modelos (regresión logística y Random Forest):
veredicto sobre qué política es más efectiva, F1 por ventana de A, B, C y baselines, contraste de
Wilcoxon, reentrenamientos y deriva por feature.

**Why this priority**: es el entregable del estudio; la interfaz debe mostrarlo primero.

**Independent Test**: abrir la interfaz y comprobar que las cifras coinciden con
`results/*.csv` y `reports/resumen.md`.

**Acceptance Scenarios**:

1. **Given** los CSV de `results/`, **When** el evaluador abre la página de resultados, **Then**
   ve por réplica el F1 medio de A, B y C, cuál es mayor y si la diferencia es significativa.
2. **Given** la misma página, **When** revisa los reentrenamientos, **Then** ve cuántas veces y
   tras qué ventana se reentrenaron B y C, y el motivo.

### User Story 2 - Comparar las políticas con su propio dataset y su propio modelo (Priority: P2)

El evaluador sube un CSV de precios diarios (fecha, apertura, máximo, mínimo, cierre, volumen) y,
opcionalmente, su propio clasificador de scikit-learn. La interfaz ejecuta el mismo walk-forward
A vs. B vs. C con las mismas features, ventanas semestrales, disparadores y métricas, y muestra
el mismo veredicto y las mismas vistas que en US1.

**Why this priority**: es lo que pide el docente; reutiliza todo el pipeline de la feature 001.

**Independent Test**: subir el dataset del proyecto con los parámetros por defecto y comprobar que
reproduce exactamente los resultados oficiales; subir otro dataset y un modelo y obtener métricas
para las 8 (o las que haya) ventanas.

**Acceptance Scenarios**:

1. **Given** un CSV válido, **When** el evaluador lanza la comparación, **Then** obtiene
   P/R/F1 por ventana para A, B, C y los baselines, el contraste de Wilcoxon y el veredicto.
2. **Given** un archivo de modelo `.skops`, **When** lo sube, **Then** se usa como plantilla: se
   clona y se reentrena según cada política (nunca se usa ya entrenado con otros datos).
3. **Given** un CSV inválido (columnas faltantes, fechas duplicadas, OHLC incoherente) o sin
   suficientes semestres, **When** se sube, **Then** la interfaz explica el error y no ejecuta.
4. **Given** el dataset del proyecto y los parámetros por defecto, **When** se ejecuta, **Then**
   las métricas coinciden con `results/window_metrics.csv`.
5. **Given** cualquier ejecución, **When** termina, **Then** se puede descargar un ZIP con los CSV
   y un manifiesto (semilla, SHA-256 del dataset, parámetros, modelo, versiones).

### User Story 3 - Desplegar en local y en la nube (Priority: P3)

El investigador levanta la interfaz en local (con `uv` o con Docker) y la publica gratis en
Streamlit Community Cloud desde el repositorio de GitHub, con un procedimiento documentado; cada
`git push` a la rama desplegada la actualiza.

**Independent Test**: `docker run -p 7860:7860` sirve la interfaz; con solo `app/requirements.txt`
instalado (como en Streamlit Cloud) la app carga y reproduce los resultados oficiales.

### Edge Cases

- Archivo de modelo con pickle (`.pkl`, `.joblib`): ejecutar pickle permite código arbitrario, así
  que MUST rechazarse salvo que el operador lo habilite en local (`ALLOW_UNSAFE_MODELS=1`).
- Archivo `.skops` con tipos fuera de scikit-learn / numpy / scipy: MUST rechazarse.
- Modelo que no es un clasificador binario o falla al entrenar: MUST informarse sin romper la app.
- Dataset con menos de 2 semestres de prueba: MUST rechazarse; con menos de 6, el contraste de
  Wilcoxon no puede dar p < 0,05 y MUST advertirse.
- Columnas con otros nombres habituales (`Date`, `Close`, `Adj Close`, `Volume`): MUST
  reconocerse sin distinguir mayúsculas.

## Requirements *(mandatory)*

- **FR-101**: La interfaz MUST mostrar primero los resultados oficiales de la feature 001 leídos de
  `results/` (sin reejecutar).
- **FR-102**: La interfaz MUST presentar, por réplica, un veredicto: F1 medio de A, B y C, la
  política con mayor F1 medio, el resultado de Wilcoxon (B−A, C−A, B−C), el número de
  reentrenamientos de B y C y la comparación con el baseline "siempre sube".
- **FR-103**: La interfaz MUST permitir subir un CSV de precios diarios y validarlo con las mismas
  reglas de integridad que la feature 001 (FR-001).
- **FR-104**: La partición para un dataset subido MUST derivarse de sus fechas con la misma regla
  que el experimento oficial: periodo inicial hasta el primer cierre de semestre con ≥ 9 meses de
  datos (validación = sus últimos 3 meses), prueba en semestres calendario completos. Aplicada al
  dataset del proyecto MUST reproducir la partición de `config/experiment.toml`.
- **FR-105**: La interfaz MUST permitir subir un clasificador de scikit-learn en formato `.skops`
  y cargarlo solo si todos sus tipos pertenecen a scikit-learn, numpy, scipy o builtins.
- **FR-106**: El modelo subido MUST usarse como plantilla (`sklearn.base.clone`) con la semilla del
  experimento; A, B y C lo entrenan según su política, igual que las réplicas oficiales
  (Principio III).
- **FR-107**: La interfaz MUST permitir ajustar los parámetros del experimento (α de deriva,
  k·σ, filas de reentrenamiento), con los valores oficiales por defecto, y MUST marcar como
  exploratoria cualquier ejecución con parámetros distintos.
- **FR-108**: Cada ejecución MUST poder descargarse (CSV + manifiesto con semilla, SHA-256 del
  dataset, parámetros, descripción del modelo y versiones de librerías).
- **FR-109**: La aplicación MUST ejecutarse en local con `uv` y con Docker, y MUST poder
  desplegarse gratis en Streamlit Community Cloud instalando solo `app/requirements.txt`.
- **FR-110**: El despliegue en la nube MUST actualizarse desde el repositorio sin pasos manuales
  tras la configuración inicial (Streamlit Cloud redepliega con cada push). La alternativa en
  Hugging Face (PRO) MUST publicarse solo tras una CI verde y sin binarios innecesarios.

## Success Criteria *(mandatory)*

- **SC-101**: Con el dataset del proyecto y los parámetros por defecto, la ejecución desde la
  interfaz produce métricas idénticas a `results/window_metrics.csv`.
- **SC-102**: Un evaluador sin entorno Python puede ver los resultados y comparar con su propio
  dataset desde el navegador.
- **SC-103**: Un archivo pickle o un `.skops` con tipos no permitidos nunca se ejecuta en el
  despliegue público.

## Assumptions

- Las ejecuciones desde la interfaz son **exploratorias**: no reemplazan el experimento oficial
  (`msft-mlops run`), que sigue siendo el único registrado en MLflow (Principio II).
- El modelo subido recibe las 9 features relativas de la feature 001 como matriz numérica.
- El plan gratuito de Streamlit Community Cloud suspende la app tras un tiempo sin visitas; la
  primera visita posterior la despierta y tarda en arrancar.
