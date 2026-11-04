# Paul: [12] Bayram, Ahmed y Kassler (2022)

"From concept drift to model degradation: An overview on performance-aware drift detectors",
*Knowledge-Based Systems* 245. PDF: `papers/_local/12-bayram-2022.pdf` (preprint de arXiv,
45 páginas, local).

## Por qué te toca

Explica **cómo se detecta la deriva**: por cambio en la distribución de los datos (lo que hace
Evidently) o por caída del desempeño (nuestro umbral de F1). Tu lectura justifica por qué el
grupo B usa los dos.

## Qué leer

El paper es largo; lee solo esto:
1. **p. 1–4:** introducción y preguntas de investigación.
2. **p. 6–9:** detección basada en distribución frente a detección basada en desempeño
   (Figs. 2 y 3), ventajas y falsas alarmas.
3. **p. 12–18 (solo hojear):** definiciones matemáticas de los tipos de deriva, para el marco
   teórico.
4. **p. 19–21:** DDM y su familia, y la jerarquía de detectores (Fig. 9).
5. **p. 33:** conclusiones.

## Lo clave frente a nuestro experimento

| Lo que dice el paper | Nuestro diseño | Nota |
|---|---|---|
| Un cambio de distribución no siempre afecta al desempeño, lo que genera falsas alarmas (p. 7) | Disparador por deriva de features (Evidently) | ⚠ B puede reentrenar sin necesidad; hay que registrar el motivo de cada reentrenamiento |
| Los detectores por desempeño solo reaccionan cuando el desempeño cae (p. 7) | Disparador por caída de F1 | ✔ Respalda D5 |
| La mayoría vigila la tasa de error (p. 33) | Vigilamos F1 por ventana | ✔ |
| La clasificación es el problema más estudiado (p. 33) | Clasificación sube/baja | ✔ |
| Deriva real `P(y|X)` vs. cambio de covariables `P(X)` (p. 12–18) | Evidently mide `P(X)`; F1 refleja `P(y|X)` | ✔ Base del marco teórico |

## Qué reutilizar o adaptar (sin copiar)

- **Taxonomía formal de la deriva (p. 12–18):** usar sus definiciones matemáticas
  (cambio en `P(X)`, en `P(y|X)` y en `P(y)`) para la sección teórica, explicando qué detecta
  cada disparador de B.
- **Jerarquía de detectores (p. 20, Fig. 9):** ubicar nuestra elección dentro de ella:
  distribución (Evidently) + desempeño (umbral de F1 por ventana).
- **Familia DDM (p. 19):** si el equipo quiere un detector por desempeño más formal que un
  umbral fijo, DDM, EDDM, ADWIN o Page-Hinkley son las opciones estándar. *(Fuera del paper:
  la librería Python `river` las implementa. Usarla sería una dependencia nueva, así que solo
  se propone; no se añade.)*
- **Registro del motivo:** de la idea de falsas alarmas sale una métrica propia: % de
  reentrenamientos disparados solo por deriva que **no** mejoraron el F1 de la ventana
  siguiente.

## Entregable

- 5 viñetas: qué confirma, qué cuestiona y qué falta en nuestro diseño.
- Párrafo de marco teórico (máx. 200 palabras, redactado por ti y citando [12]) sobre los
  tipos de deriva y qué detecta cada disparador.
- Recomendación: ¿umbral fijo de F1 o un detector formal (DDM/ADWIN)?
