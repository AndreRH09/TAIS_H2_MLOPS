# Willy: [13] Vela *et al.* (2022)

"Temporal quality degradation in AI models", *Scientific Reports* 12, 11654.
PDF: `papers/13-vela-2022.pdf` (CC BY 4.0).

## Por qué te toca

Mide qué le pasa a un modelo que **nunca se reentrena**, que es exactamente nuestro grupo A.
También entrena con **un año** de datos y compara un modelo lineal con RF, igual que nosotros.

## Qué leer (en orden)

1. **p. 2:** elección de los 4 modelos (Ridge, RF, XGBoost y red neuronal, en scikit-learn).
2. **p. 3–4:** la "prueba de degradación temporal": definición de edad del modelo, ventana de
   un año, fórmula del error relativo `E_rel(dT)` y precauciones (semillas, búsqueda de
   hiperparámetros con partición temporal).
3. **p. 4–6:** patrones de degradación (gradual, explosiva, imprevisible) y la conclusión de
   que la deriva de datos no basta para disparar el reentrenamiento.
4. **p. 9–10:** soluciones propuestas y la probabilidad `P_ac(dT)` de seguir teniendo un
   modelo aceptable.

## Lo clave frente a nuestro experimento

| Ellos | Nosotros | Nota |
|---|---|---|
| Entrenan con 1 año de historia (p. 3) | B reentrena con el último año | ✔ Respalda D6 |
| Ridge y RF entre los 4 modelos; envejecen distinto | LR o RF (Q2 pendiente) | ✔ Respalda probar ambos |
| La deriva de datos sola no sirve para disparar el reentrenamiento (p. 6) | Disparador: deriva **o** F1 | ✔ Respalda D5 |
| Hiperparámetros con búsqueda en malla y partición temporal de 5 folds (p. 3) | Ajuste con el periodo de validación | ◐ Podemos adoptar la partición temporal en el ajuste |
| Regresión (MSE), 32 datasets | Clasificación (F1), 1 activo | ↔ |

## Qué reutilizar o adaptar (sin copiar)

- **Prueba de degradación temporal (p. 3–4):** su métrica es
  `E_rel(dT) = MSE(t0 + dT) / MSE(t0)`. **Adaptación a clasificación:**
  `F1_rel(k) = F1(ventana k) / F1(validación)` para el grupo A, en función de la edad del
  modelo (semestres desde el entrenamiento). Es la curva de envejecimiento de A.
- **Umbral de "modelo aceptable" (p. 10):** consideran aceptable el modelo mientras
  `E_rel < 2,0` (error menor al doble del de entrenamiento). **Adaptación:** fijar el umbral de
  caída de F1 de B de forma relativa (por ejemplo, F1 < x % del F1 de validación) y
  justificarlo con este criterio. El valor de x lo decide el equipo antes de la prueba
  (Principio III).
- **Gráfico de envejecimiento (p. 4):** puntos de error frente a edad, con percentiles
  móviles. **Adaptación:** F1 de A y de B por ventana, marcando los reentrenamientos de B.
- **Precauciones metodológicas (p. 3):** varias semillas, hiperparámetros con partición
  temporal y verificación de la implementación. Son un checklist de reproducibilidad.

## Entregable

- 5 viñetas: qué confirma, qué cuestiona y qué falta en nuestro diseño.
- Propuesta concreta de umbral relativo de F1, con su justificación desde `E_rel < 2,0`.
- Boceto del gráfico de envejecimiento A vs. B.
