# Feature Specification: Experimento modelo estático vs. modelo operado con MLOps

**Feature Branch**: `001-mlops-drift-experiment`

**Created**: 2026-11-03

**Status**: Draft

**Input**: User description: "Diseño experimental: modelo estático vs. modelo operado con MLOps
(monitoreo de deriva y reentrenamiento automático) sobre el histórico diario de MSFT
(feb 2021 – feb 2026), clasificación de la dirección del precio al día siguiente, evaluación
walk-forward por ventanas, contraste del diseño con la literatura revisada por pares."

## User Scenarios & Testing *(mandatory)*

Actor principal: **investigador** (estudiante del curso) que ejecuta el experimento y
reporta conclusiones. Actor secundario: **evaluador** (docente) que revisa validez y
reproducibilidad.

### User Story 1 - Ejecutar el experimento walk-forward A vs. B vs. C (Priority: P1)

El investigador ejecuta, con un solo comando, la simulación completa sobre el periodo de
prueba. En cada ventana predicen la dirección del precio tres grupos, y sus métricas quedan
registradas por ventana:

- **Grupo A (control, sin MLOps):** modelo entrenado una vez con los datos iniciales y nunca
  actualizado.
- **Grupo B (MLOps por monitoreo):** modelo vigente que se reentrena solo cuando se detecta
  deriva o caída de desempeño.
- **Grupo C (MLOps periódico):** modelo que se reentrena al cierre de cada ventana sin mirar
  deriva ni desempeño.

Comparar B con C separa el efecto del **monitoreo** del efecto de **reentrenar**
(respaldo: [5] p. 11, [6] p. 6–7 en `literature-review/`).

**Why this priority**: es el núcleo del estudio; sin él no hay resultado que analizar.

**Independent Test**: ejecutar el experimento sobre el dataset y comprobar que existen
métricas por ventana para los tres grupos y un registro de cada reentrenamiento de B y C.

**Acceptance Scenarios**:

1. **Given** el dataset validado y la configuración fijada, **When** el investigador ejecuta
   el experimento, **Then** se obtienen Precision, Recall y F1 por ventana para A, B y C.
2. **Given** una ventana cerrada en la que se detecta deriva o el F1 de B cae bajo el umbral,
   **When** el sistema evalúa la ventana, **Then** B se reentrena con los datos del último año
   disponible, se registra como nueva versión y se usa desde la ventana siguiente (nunca en
   la ventana que disparó el reentrenamiento).
3. **Given** una ventana sin deriva ni caída de F1, **When** se cierra, **Then** B conserva su
   versión vigente y no se registra reentrenamiento.
4. **Given** cualquier ventana cerrada, **When** el sistema la evalúa, **Then** C se reentrena
   con los datos del último año disponible, independientemente de la deriva y del F1, y la
   nueva versión se usa desde la ventana siguiente.
5. **Given** la misma configuración y semilla, **When** el experimento se ejecuta dos veces,
   **Then** las métricas resultantes son idénticas.

---

### User Story 2 - Contrastar el diseño con la literatura (Priority: P2)

El investigador dispone, dentro del repositorio y en formato legible, de una bibliografía de
al menos 20 fuentes revisadas por pares (2015–2026, formato IEEE) y de una matriz que compara
el diseño propio con el de cada estudio en: forma de obtener los datos, partición temporal,
tipo de baseline, disparador de reentrenamiento y métricas.

**Why this priority**: los parámetros del experimento (partición, umbrales, baseline) deben
justificarse con evidencia antes de ejecutar la evaluación final.

**Independent Test**: abrir el documento de literatura y verificar que cada fuente tiene
referencia IEEE completa con DOI verificable y una fila en la matriz de contraste.

**Acceptance Scenarios**:

1. **Given** la bibliografía, **When** el evaluador revisa una referencia, **Then** su DOI o
   fuente editorial resuelve al documento citado.
2. **Given** la matriz de contraste, **When** se revisa una decisión del diseño (p. ej. la
   partición), **Then** se identifica al menos una fuente que la respalda o una divergencia
   justificada.
3. **Given** las tres áreas temáticas (MLOps general; deriva y reentrenamiento; evaluación
   temporal/walk-forward), **When** se revisa la bibliografía, **Then** cada área tiene
   fuentes asignadas.

---

### User Story 3 - Analizar y reportar la comparación (Priority: P3)

El investigador obtiene un resumen comparativo: evolución temporal de las métricas de A, B, C
y los baselines ingenuos, diferencias por ventana (B−A, C−A, B−C), número y momento de los
reentrenamientos de B y C, y las amenazas a la validez.

**Why this priority**: convierte los resultados en conclusiones evaluables; depende de US1.

**Independent Test**: a partir de las métricas registradas, generar el resumen y verificar
que incluye la serie temporal de F1 de los tres grupos y los baselines, y la lista de
reentrenamientos.

**Acceptance Scenarios**:

1. **Given** las métricas por ventana, **When** se genera el resumen, **Then** muestra la
   evolución de Precision, Recall y F1 de A, B, C y los baselines sobre todas las ventanas,
   por réplica.
2. **Given** el resumen, **When** el evaluador lo revisa, **Then** encuentra el número de
   reentrenamientos de B y de C, las ventanas en que ocurrieron y el motivo (deriva, caída de
   F1 o periódico).

---

### Edge Cases

- Ventana con una sola clase en las etiquetas reales (solo subidas o solo bajadas): las
  métricas indefinidas MUST registrarse explícitamente como tales, no como cero silencioso.
- Ventana incompleta al final del periodo (2026-Q1 con pocos días): MUST indicarse su tamaño
  y excluirse o reportarse aparte según regla fijada antes de la ejecución.
- Días sin cotización o registros faltantes/duplicados: MUST detectarse en la validación de
  datos antes de construir features.
- Discrepancias entre el dataset de Kaggle y la fuente externa de validación: MUST
  documentarse y resolverse antes del experimento.
- Reentrenamiento disparado en la última ventana: se registra, pero no hay ventana posterior
  donde evaluarlo.
- Las primeras observaciones sin historia suficiente para calcular rezagos o medias móviles
  MUST descartarse, no rellenarse con información futura.

## Requirements *(mandatory)*

### Functional Requirements

**Datos**

- **FR-001**: El sistema MUST cargar el histórico diario de MSFT (04-02-2021 a 02-02-2026) con
  apertura, cierre, máximo, mínimo, volumen y variación diaria.
- **FR-002**: El sistema MUST validar el dataset contra una fuente externa independiente de
  precios históricos y reportar discrepancias (fechas, precios, volumen).
- **FR-003**: El sistema MUST registrar la versión del dataset (identificador de contenido) y
  su procedencia y licencia.

**Variables y etiqueta**

- **FR-004**: La etiqueta MUST ser la dirección del cierre del día siguiente (sube / no sube).
- **FR-005**: Las features MUST construirse solo con información pasada: rendimientos
  rezagados, medias móviles y volumen.
- **FR-006**: El sistema MUST verificar automáticamente que ninguna feature use información
  posterior al instante de predicción.

**Partición y evaluación**

- **FR-007**: La partición MUST ser temporal: entrenamiento y validación con datos de 2021,
  prueba desde 2022-Q1 hasta 2026-Q1 en ventanas consecutivas.
- **FR-008**: El tamaño de ventana de prueba MUST ser semestral (≈ 8 ventanas de ≈ 126
  registros cada una), para reducir el ruido de las métricas por ventana.
- **FR-009**: Los hiperparámetros MUST ajustarse solo con el periodo de validación.

**Modelo**

- **FR-010**: El experimento MUST ejecutarse en dos réplicas independientes, una con regresión
  logística y otra con Random Forest. Dentro de cada réplica, todos los grupos usan el mismo
  clasificador (respaldo: [13], [20], [22], [23] en `literature-review/`).
- **FR-011**: El grupo A MUST mantener el modelo inicial sin cambios durante toda la prueba.
- **FR-011a**: El grupo C MUST reentrenarse al cierre de cada ventana con los datos del último
  año, usando el mismo procedimiento de reentrenamiento que B, sin evaluar deriva ni F1 como
  condición.

**Monitoreo y reentrenamiento (grupo B)**

- **FR-012**: Al cerrar cada ventana, el sistema MUST comparar la distribución de las
  features de la ventana con la de referencia y reportar si hay deriva del conjunto.
- **FR-013**: El sistema MUST disparar reentrenamiento de B cuando se detecte deriva o el F1
  de B en la ventana caiga bajo un umbral.
- **FR-014**: El umbral de deriva, el umbral de F1 y la ventana de reentrenamiento (último año)
  MUST fijarse y documentarse antes de ejecutar la prueba, con justificación en la literatura.
- **FR-015**: Cada reentrenamiento MUST registrar una nueva versión del modelo con fecha,
  motivo, datos usados y métricas de validación.
- **FR-016**: La referencia de deriva MUST actualizarse a los datos de entrenamiento de la
  versión vigente tras cada reentrenamiento.

**Referencias de comparación**

- **FR-017**: Además de los grupos experimentales, el sistema MUST reportar, por ventana y con
  las mismas métricas, tres baselines ingenuos: siempre "sube", persistencia de la dirección
  del día anterior y aleatorio estratificado según la proporción de clases del entrenamiento
  (respaldo: [18], [22]).

**Registro y reporte**

- **FR-018**: El sistema MUST registrar por ventana y grupo: Precision, Recall, F1, tamaño de
  ventana, versión de modelo usada y resultado de la evaluación de deriva.
- **FR-019**: El sistema MUST generar un resumen comparativo según US3.

**Literatura**

- **FR-020**: El repositorio MUST incluir una bibliografía legible de ≥ 20 fuentes revisadas
  por pares (2015–2026, IEEE), cada una con DOI verificado.
- **FR-021**: El repositorio MUST incluir una matriz de contraste con las dimensiones:
  obtención de datos, partición temporal, tipo de baseline, disparador de reentrenamiento y
  métricas.

### Key Entities

- **Observación diaria**: fecha, precios OHLC, volumen, variación; base de features y
  etiqueta.
- **Ventana de prueba**: periodo consecutivo (inicio, fin, número de registros) en el que se
  evalúan todos los grupos.
- **Versión de modelo**: réplica (LR o RF), grupo, número de versión, periodo de
  entrenamiento, fecha de creación, motivo (inicial / deriva / caída de F1 / periódico).
- **Evaluación de ventana**: ventana × grupo × versión → Precision, Recall, F1, resultado de
  deriva.
- **Fuente bibliográfica**: referencia IEEE, DOI, área temática y valores en la matriz de
  contraste.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El experimento completo se ejecuta de principio a fin con un solo comando, sin
  pasos manuales intermedios.
- **SC-002**: El 100 % de las ventanas de prueba tiene métricas registradas para los tres
  grupos y los tres baselines, en ambas réplicas.
- **SC-003**: Dos ejecuciones con la misma configuración producen métricas idénticas (diferencia
  0 en todas las ventanas).
- **SC-004**: El 100 % de las features pasa la verificación automática de ausencia de fuga de
  información.
- **SC-005**: La bibliografía contiene ≥ 20 fuentes revisadas por pares, con el 100 % de los
  DOI verificados, y cubre las tres áreas temáticas.
- **SC-006**: Cada parámetro del diseño (partición, umbrales, ventana de reentrenamiento,
  baseline) se vincula con al menos una fuente de la matriz de contraste.
- **SC-007**: Un evaluador puede reproducir los resultados a partir del repositorio en menos de
  30 minutos siguiendo la documentación.

## Assumptions

- El interés está en las **diferencias** entre A, B y C, no en el valor absoluto de las métricas;
  se esperan métricas bajas dada la dificultad de predecir la dirección diaria.
- La partición propuesta (entrenamiento feb–sep 2021, validación oct–dic 2021) es
  **provisional**: se revisará con la matriz de contraste antes de la ejecución final. El
  periodo de entrenamiento inicial tiene ≈ 160 registros, y el "80/20" se refiere solo a 2021.
- La clase positiva para Precision/Recall/F1 es "sube".
- Un solo activo y un solo tipo de modelo limitan la generalización; se documenta como amenaza
  a la validez.
- El experimento es una simulación por lotes sobre datos históricos; no hay despliegue en
  producción ni datos en tiempo real.
- La fuente externa de validación de precios es de acceso público.
- El dataset de Kaggle se usa bajo licencia Apache 2.0.
