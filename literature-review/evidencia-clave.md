# Evidencia clave: los 4 papers más cercanos al experimento

Fragmentos **textuales** extraídos del PDF de cada paper, para subrayarlos y contrastarlos con
el diseño. Las páginas corresponden al PDF guardado en `papers/` o `papers/_local/`.
Leyenda: ✔ respalda · ⚠ matiza o contradice · ↔ diferencia con nuestro diseño.

| # | Paper | Por qué es cercano | Archivo |
|---|---|---|---|
| [5] | Kreuzberger *et al.* 2023 | Define MLOps: el reentrenamiento por monitoreo es lo que hace "operado con MLOps" al grupo B | `papers/05-kreuzberger-2023.pdf` |
| [6] | Cavalcante y Oliveira 2015 | El caso más parecido: series bursátiles diarias de Yahoo Finance, reentrenamiento solo cuando se detecta deriva | `papers/_local/06-cavalcante-2015.pdf` |
| [13] | Vela *et al.* 2022 | Mide cómo envejece un modelo sin reentrenar (grupo A), entrena con 1 año, usa modelos lineal y RF | `papers/13-vela-2022.pdf` |
| [12] | Bayram *et al.* 2022 | Justifica el disparador por caída de desempeño (F1) frente al disparador solo por distribución | `papers/_local/12-bayram-2022.pdf` (arXiv) |

---

## [5] Kreuzberger *et al.* 2023: definición de MLOps

**p. 5 (revista p. 31870), principio P6:**
> "Continuous training (CT) means periodic retraining of the ML model based on new feature
> data. […] Continuous training always includes an evaluation run to assess the change in model
> quality"

✔ Grupo B. Cada reentrenamiento debe ir acompañado de una evaluación (FR-015: métricas de
validación de la nueva versión).

**p. 5, principio P7:**
> "Metadata tracking and logging is required for each training job iteration […] including the
> model specific metadata—e.g., used parameters and the resulting performance metrics, model
> lineage: data and code used"

✔ Principio II de la constitución y FR-015/FR-018: registro en MLflow de parámetros, métricas,
datos y versión.

**p. 5, principio P8:**
> "Continuous monitoring implies the periodic assessment of data, model, code, infrastructure
> resources, and model serving performance (e.g., prediction accuracy)"

✔ Evaluación al cierre de cada ventana de **datos** (deriva) y de **desempeño** (F1).

**p. 10–11 (revista p. 31875–31876), componente de monitoreo y feedback loop:**
> "Once the model-monitoring component (C9) detects a drift in the data, the information is
> forwarded to the scheduler, which then triggers the automated ML workflow pipeline for
> retraining (continuous training)."

> "Retraining is not only triggered automatically when a statistical threshold is reached; it can
> also be triggered when new feature data is available, or it can be scheduled periodically."

✔ D5: el disparador por deriva con umbral estadístico es una de las formas de CT definidas.
↔ La misma cita reconoce el reentrenamiento **periódico** como alternativa válida (ver la nota
final).

---

## [6] Cavalcante y Oliveira 2015: deriva en series financieras

**p. 1, Introducción** (las dos familias de adaptación):
> "two main approaches to handle concept drift are (i) the blind methods, which adapt the
> decision model at regular intervals without explicitly monitor changes in data, and (ii) the
> methods which explicitly detect drifts in data and reactively update the model"

✔ El grupo B pertenece a la familia (ii). Sirve para posicionar el experimento.

**p. 3, Sección III:**
> "There is a very high risk involved in using an outdated prediction model in financial
> markets, which can cause financial damage."

✔ Motivación del estudio: el riesgo del grupo A estático.

**p. 4, Sección III.B:**
> "The main idea of combining a batch algorithm with drift detection is to retrain the learned
> model whenever a drift is detected."

✔ Es exactamente la lógica de B: modelo batch que se reentrena solo cuando se detecta deriva.

**p. 5, Sección IV** (datos y partición, comparable con la nuestra):
- Datos: S&P 500, Shanghai y **Apple**, *"publicly available and can be obtained from Yahoo
  Finance"*. ✔ Valida usar Yahoo Finance como fuente externa (FR-002).
- Features: precios diarios OHLC de los 5 días previos + EMA + Bandas de Bollinger. ✔ Parecido
  a nuestras features (rezagos y medias móviles).
- > "we use the first 1/3 of the data for the initial training. Then, the remaining 2/3 of the
  > data are used to simulate a continuous data stream"

  ✔ D1: partición temporal con entrenamiento inicial y el resto como flujo simulado.

**p. 6–7, Resultados** ⚠ **(subrayar en otro color)**:
> "The results indicate that our first hypothesis is not entirely valid. Even if the ELM+DDM and
> the ELM+ECDD have lower computational costs than OS-ELM, these methods do not present an
> equivalent accuracy."

⚠ Reentrenar **solo cuando se detecta deriva** fue *menos preciso* que actualizar de forma
continua, por el "periodo de inestabilidad" (p. 6) entre el inicio de la degradación y la
detección. En cambio, sí superó con claridad al modelo nunca actualizado (Tabla I: S&P 500
MAPE 12,43 → 1,22). Para nuestra hipótesis A vs. B esto **respalda que B > A**, pero advierte
que B pierde frente a una actualización más frecuente.

↔ Diferencias: es **regresión** (precio de cierre, MAPE) y no clasificación (dirección, F1); y
detecta instancia a instancia, no por ventana semestral.

---

## [13] Vela *et al.* 2022: envejecimiento de modelos

**p. 2, elección de modelos:**
> "Penalized linear regression RidgeRegressor model (RV). Random forest RandomForestRegressor
> model (RF)." (2 de los 4 modelos estudiados)

✔ D3: el estudio de referencia compara un modelo lineal con RF y encuentra que **envejecen
distinto**. Respalda la opción C (ambos).

**p. 3, prueba de degradación temporal:**
> "We define the 'age' of an AI model as the time passed since the model was last trained on
> then-current data."

> "we trained each model using one year of historical data (from the year ending at t0)"

✔ D6: **ventana de entrenamiento de un año**, la misma que usa nuestro reentrenamiento.
✔ El "age" es exactamente lo que crece sin parar en el grupo A.

**p. 3:**
> "it is far more concerning to observe model quality degradation when the data remains
> consistent, with nothing alarming the users of potential problems."

**p. 6 (la cita más importante para D5):**
> "data drifts alone cannot be used to explain model failures, or to trigger model quality
> checks and re-training."

✔ D5: justifica que el disparador sea **deriva O caída de F1**. Vigilar solo la distribución
de las features no basta.

**p. 9–10, soluciones propuestas:**
> "develop a trigger to signal when the model must be retrained; develop an efficient and robust
> mechanism for automatic model retraining, and have constant access to the most recent ground
> truth."

✔ Son las tres piezas del grupo B: disparador, reentrenamiento automático y etiquetas reales
al cierre de cada ventana.

↔ Diferencia: usa regresión (MSE) y 32 datasets, no clasificación en un solo activo.

---

## [12] Bayram *et al.* 2022: detectores basados en desempeño

**p. 7 (arXiv), detectores por distribución:**
> "changes in the data distributions do not always affect the predictor performance, potentially
> leading to false alarms in the system"

⚠ El disparador por deriva de features (Evidently) puede reentrenar sin que haga falta. Hay que
**registrar el motivo** de cada reentrenamiento (FR-015) para medir cuántos fueron por
deriva y cuántos por F1.

**p. 7, detectores por desempeño:**
> "The main advantage of performance-based approaches is that they only handle the change when
> the performance is affected. Thus, these methods are more efficient in dealing with potential
> false alarms than distribution-based algorithms."

✔ D5: respalda incluir la caída de F1 como disparador.

**p. 33, conclusión 3:**
> "Most existing performance-based detectors rely on monitoring the error rate to identify the
> performance degradation and trigger a drift"

✔ Monitorear una métrica de error/desempeño (F1 en nuestro caso) es la práctica dominante.

**p. 33, conclusión 2:**
> "The classification problem comprises the major part of the task scope in drift handling."

✔ Plantear la tarea como clasificación (sube/baja) es coherente con la literatura de deriva.

---

## Qué confirma y qué cuestiona

| Decisión | Veredicto tras la lectura | Evidencia textual |
|---|---|---|
| D1 Partición temporal | ✔ | [6] p. 5 (1/3 entrenamiento, 2/3 flujo) |
| D3 LR y RF | ✔ opción C | [13] p. 2 (lineal + RF envejecen distinto) |
| D5 Deriva **o** F1 | ✔✔ | [13] p. 6, [12] p. 7, [5] p. 11 |
| D6 Ventana de 1 año | ✔ (antes ◐) | [13] p. 3 |
| Hipótesis B > A | ✔ con matiz | [6] Tabla I (B ≫ estático) |
| Fuente externa Yahoo Finance | ✔ | [6] p. 5 |

**Matiz para la discusión (no cambia la spec):** [6] p. 6–7 y [5] p. 11 muestran que el
reentrenamiento **periódico/continuo** (método "ciego") puede superar al reentrenamiento por
detección. Un tercer grupo C ("reentrenar cada semestre sin mirar la deriva") permitiría saber
si la ventaja de B viene del **monitoreo** o simplemente de **reentrenar**. Queda como amenaza
a la validez o como extensión opcional.
