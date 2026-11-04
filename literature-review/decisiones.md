# Decisiones de diseño y su respaldo bibliográfico

Estado: **✔ respaldada** · **◐ respaldo indirecto** · **? pendiente de decidir**.
⚠ = la afirmación depende de detalles que no están en el resumen y hay que confirmarla con el
texto completo. Los números entre corchetes remiten a [referencias.md](referencias.md).

| ID | Decisión | Estado |
|---|---|---|
| D1 | Partición temporal, sin barajado | ✔ |
| D2 | Ventanas de prueba semestrales | ◐ |
| D3 | Clasificador: LR, RF o ambos | ? |
| D4 | Baselines ingenuos de referencia | ? |
| D5 | Reentrenar si hay deriva **o** cae el F1 | ✔ |
| D6 | Reentrenar con el último año (ventana deslizante) | ✔ ([13] p. 3, ver [evidencia-clave.md](evidencia-clave.md)) |
| D7 | Métricas Precision, Recall y F1 | ◐ |

---

## D1. Partición temporal, sin barajado — ✔

**Decisión (FR-007):** entrenamiento y validación en 2021, prueba en ventanas consecutivas desde
2022.

**Respaldo:**
- [15] La validación cruzada K-fold solo es válida para modelos puramente autorregresivos con
  errores no correlacionados. Nuestras features (medias móviles, volumen) no cumplen ese
  supuesto.
- [18] Una partición incorrecta hace parecer competitivos a métodos que no lo son.
- [19] La fuga de información temporal está entre los tipos de leakage documentados; al
  corregirla, la ventaja de ML sobre la LR desaparece.
- [16] Compara empíricamente métodos de estimación del desempeño en series reales.
- [21], [22] Los estudios de referencia en dirección bursátil evalúan fuera de muestra en orden
  temporal.

**Observación:** el periodo de entrenamiento inicial (feb–sep 2021, ≈ 160 registros) es corto.
⚠ Hay que comprobar en [21] y [22] el tamaño de sus periodos de entrenamiento para comparar.

---

## D2. Ventanas de prueba semestrales — ◐

**Decisión (FR-008):** ≈ 8 ventanas de ≈ 126 registros.

**Respaldo indirecto:**
- [13] La calidad del modelo se degrada con el tiempo transcurrido desde el último
  entrenamiento, así que la granularidad de la ventana determina cuándo se detecta.
- [17] Las métricas de clasificación son inestables con pocos ejemplos, y una ventana más larga
  reduce su varianza.

**Brecha:** ninguna fuente revisada prescribe un tamaño de ventana para este problema. La
elección es una solución de compromiso propia (estabilidad de la métrica frente a frecuencia de
decisión) y se documenta como tal en la spec.

---

## D3. Clasificador: LR, RF o ambos — ? (Q2 pendiente)

**Evidencia:**
- [20] RF quedó primero y la LR última en dirección bursátil; los autores recomiendan incluir
  ensambles.
- [22] Usa RF y LR como benchmarks estándar.
- [23] Los métodos de árboles superan a los lineales gracias a las interacciones no lineales.
- [19] Al eliminar la fuga, ML deja de superar a la LR, que sigue siendo un comparador
  necesario.

**Lectura:** la literatura usa ambos. RF suele rendir más; la LR es el benchmark mínimo.
**Sugerencia:** opción C (ambos, como dos réplicas), que además mitiga la amenaza "un solo
modelo".

---

## D4. Baselines ingenuos — ? (Q3 pendiente)

**Evidencia:**
- [18] Sin comparación de referencia se concluye que métodos poco competitivos sí lo son.
- [22] El exceso de retorno desaparece después de 2010, coherente con mercados difíciles de
  predecir. Un baseline ingenuo permite saber si A o B superan al azar.
- [24] ⚠ Hay que verificar en el texto completo qué baselines reportan los estudios revisados.

**Sugerencia:** opción B (siempre "sube", persistencia del día anterior, aleatorio
estratificado). Su costo es mínimo y da contexto a métricas absolutas bajas.

---

## D5. Disparador: deriva de datos **o** caída de F1 — ✔

**Decisión (FR-012, FR-013):** reentrenar B si se detecta deriva en las features o si el F1 de
la ventana cae bajo un umbral.

**Respaldo:**
- [6] En series financieras, actualizar el modelo solo cuando un detector explícito señala
  deriva mantiene la precisión con menor costo. Es el antecedente directo del grupo B.
- [13] El desempeño puede degradarse **sin** deriva aparente en los datos, por lo que vigilar
  solo los datos no basta. Esto justifica el "o caída de F1".
- [12] Los detectores basados en desempeño (control del error) son una familia consolidada.
- [9], [10], [14] Los tests de dos muestras y los detectores no supervisados sobre la
  distribución de las features detectan deriva de datos sin esperar etiquetas.
- [8] Marco detección → comprensión → adaptación.
- [1], [4], [5] Monitoreo y entrenamiento continuo como componentes de MLOps.

**Pendiente:** fijar los umbrales (deriva, F1) antes de ejecutar la prueba (Principio III).
⚠ Hay que revisar en [12] los valores de umbral habituales.

---

## D6. Ventana de reentrenamiento: último año, deslizante — ◐

**Decisión (FR-013):** el reentrenamiento usa los datos del último año.

**Respaldo indirecto:**
- [8] Las ventanas sobre los datos recientes son una estrategia clásica de adaptación, porque
  olvidan los conceptos obsoletos.
- [11] Compara estrategias de adaptación (reentrenar sobre datos recientes frente a
  acumulados).

**Brecha:** el tamaño de un año no está prescrito en la literatura revisada.
⚠ Hay que confirmar en [11] si se compara una ventana deslizante con una expansiva. Conviene
evaluar la expansiva como sensibilidad.

---

## D7. Métricas Precision, Recall y F1 — ◐

**Respaldo:**
- [17] F1 ignora los verdaderos negativos y depende de qué clase se toma como positiva. En una
  tarea sube/baja, ambas clases importan.

**Sugerencia:** mantener P/R/F1 como pide el diseño y **añadir MCC** como métrica
complementaria. Es una decisión nueva que requiere tu aprobación.
