# Decisiones de diseño y su respaldo bibliográfico

Estado: **✔ respaldada** · **◐ respaldo indirecto** · **? pendiente de decidir**.
⚠ = la afirmación depende de detalles que no están en el resumen y hay que confirmarla con el
texto completo. Los números entre corchetes remiten a [referencias.md](referencias.md).

| ID | Decisión | Estado |
|---|---|---|
| D1 | Partición temporal, sin barajado | ✔ |
| D2 | Ventanas de prueba semestrales | ✔ esquema ([22] p. 6, [23] p. 27); tamaño semestral = adaptación justificada |
| D3 | Clasificador: LR, RF o ambos | ? |
| D4 | Baselines ingenuos de referencia | ? |
| D5 | Reentrenar si hay deriva **o** cae el F1 | ✔ |
| D6 | Reentrenar con el último año (ventana deslizante) | ✔ ([13] p. 3, ver [evidencia-clave.md](evidencia-clave.md)) |
| D7 | Métricas Precision, Recall y F1 | ◐ |
| D8 | Purga de 1 día entre entrenamiento y la ventana siguiente | ✔ |
| D9 | Hiperparámetros congelados en los reentrenamientos | ✔ (con contraejemplo) |
| D10 | σ del F1 de referencia estimada por bootstrap | ✔ |

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

## D2. Ventanas de prueba semestrales — ✔ (esquema respaldado)

**Decisión (FR-008):** ≈ 8 ventanas de ≈ 126 registros.

**Respaldo indirecto:**
- [13] La calidad del modelo se degrada con el tiempo transcurrido desde el último
  entrenamiento, así que la granularidad de la ventana determina cuándo se detecta.
- [17] Las métricas de clasificación son inestables con pocos ejemplos, y una ventana más larga
  reduce su varianza.

**Respaldo directo del esquema (lectura completa, 2026-11-03):**
- [22] p. 6: *"a training period of 750 days (approximately three years) and a trading period
  of 250 days (approximately one year) […] 23 of these study periods with non-overlapping
  trading periods"*. Son periodos de prueba de calendario, de longitud fija y sin solape, con
  un reentrenamiento por periodo: el mismo esquema que nuestras ventanas.
- [23] p. 27: *"we refit once every year as most of our signals are updated once per year"*.
  Fijan la cadencia de reajuste al ritmo con que cambian los datos.

**Por qué semestral y no anual:** con 4 años de prueba, ventanas anuales darían 4 puntos, y el
test de Wilcoxon necesita al menos 6 pares para que un p < 0,05 sea posible. Con ventanas
semestrales hay 8. El tamaño exacto (semestre) sigue siendo una adaptación propia del esquema
de [22] y [23] a un periodo más corto, y se declara así.

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

**Umbral de F1 (decidido en clarify 2026-11-03):** `F1_ventana < F1_referencia − 2σ`.
Ningún paper revisado respalda un porcentaje fijo (como 20 %). La literatura usa umbrales
estadísticos: DDM avisa a 2σ (95 %) y declara deriva a 3σ (99 %) [6] p. 3, y en series
financieras el mejor nivel de deriva fue 2σ [6] p. 6; la familia DDM es la base de los
detectores por desempeño [12] p. 19.
**Umbral de deriva (decidido en clarify 2026-11-03):** KS por feature + corrección de
Bonferroni, deriva si `min(p) < 0,05 / K`. Respaldo textual: [9] p. 4 describe el método y
p. 6 fija α = 0,05; los tests univariados agregados rinden *"comparable"* a los multivariados.
⚠ KS supone muestras independientes, y las features derivadas de ventanas móviles están
autocorrelacionadas. Se declara como amenaza a la validez.

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

**Decisión del equipo (2026-11-03):** se mantienen P/R/F1 sin MCC. La limitación de F1 se
declara como amenaza a la validez.

---

## D8. Purga de 1 día entre entrenamiento y prueba — ✔

**Decisión (plan, research R5):** al reentrenar al cierre de la ventana *k* se elimina el
último día, porque su etiqueta depende del cierre del primer día de *k+1*.

**Respaldo (lectura completa):**
- [15] p. 2: el *h-block CV*, en el que *"the h observations preceding and following the
  observation are left out"*, porque esas observaciones pueden ser dependientes.
- [16] p. 4: en la evaluación por bloques *"one can also introduce a gap between the training
  and test sets"*; p. 6: el hv-blocked CV *"creates a gap between both sets"*.

Nuestra purga es el caso mínimo (h = 1), suficiente porque la etiqueta mira un solo día hacia
adelante.

---

## D9. Hiperparámetros congelados en los reentrenamientos — ✔ (con contraejemplo)

**Decisión (plan, research R6):** los hiperparámetros se eligen una vez con 2021 y todos los
reentrenamientos de B y C reutilizan esa configuración; solo cambian los datos.

**Respaldo (lectura completa):**
- [11] p. 4, estrategia *Detect & Retrain*: *"retrains the pipelines from scratch on the latest
  s batches when drift is detected. The original pipeline configurations […] are kept"*. Es
  exactamente el grupo B.
- [11] p. 4, *Periodic Restart*: reinicia en cada lote, el equivalente al grupo C, y sirve
  para probar *"whether a drift detector is useful"*.

**Contraejemplo:** [23] p. 27 reajusta los hiperparámetros en cada reentrenamiento (desplaza
la validación hacia adelante), y [11] p. 4 también evalúa variantes que re-optimizan
(*Detect & Restart*). Congelar es una elección deliberada para cumplir el Principio III: si
B y C reajustaran hiperparámetros, su ventaja no se podría atribuir solo a la política de
reentrenamiento.

---

## D10. σ del F1 de referencia por bootstrap — ✔

**Decisión (FR-013a, research R4):** σ se estima con 1 000 remuestras bootstrap del hold-out
temporal.

**Respaldo (lectura completa, [25] en `papers/`):**
- [25] p. 4: para el F-score *"the common practice is to assume that they are not normally
  distributed"*, así que no corresponde una fórmula paramétrica.
- [25] p. 6: *"The idea of bootstrap is to use the samples as surrogate populations, for the
  purpose of approximating the sampling distribution of the statistic."*
- [25] p. 6, árbol de decisión: con pocos datos, *"Use bootstrap or randomization test"*.

**Limitación (también de [25] p. 6):** el bootstrap *"is less effective for small test sets"*.
Coincide con la limitación ya declarada en research R4 (hold-out de ≈ 50 días).
