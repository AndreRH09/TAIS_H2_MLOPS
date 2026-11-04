# Frank: [6] Cavalcante y Oliveira (2015)

"An Approach to Handle Concept Drift in Financial Time Series Based on Extreme Learning Machines
and Explicit Drift Detection", *IJCNN 2015*. PDF: `papers/_local/06-cavalcante-2015.pdf`
(local, IEEE, no se sube a GitHub).

## Por qué te toca

Es el estudio **más parecido** al nuestro: acciones (incluida Apple y el S&P 500), datos
diarios de Yahoo Finance, partición temporal y reentrenamiento solo cuando se detecta deriva.
Tu lectura dice si nuestro grupo B tiene precedente y qué riesgo trae.

## Qué leer

El paper completo (8 páginas). Con atención especial a:
1. **p. 1:** métodos "ciegos" (reentrenan cada cierto tiempo) frente a métodos de detección
   explícita.
2. **p. 3–4, Sección III:** reglas de DDM y ECDD y el algoritmo de las Figs. 1 y 2.
3. **p. 5, Sección IV:** datos, features y partición (1/3 entrenamiento, 2/3 flujo).
4. **p. 6–7, Tablas I y III:** resultados, y el **"periodo de inestabilidad"**.

## Lo clave frente a nuestro experimento

| Ellos | Nosotros | Nota |
|---|---|---|
| S&P 500, Shanghai y Apple, diario, Yahoo Finance | MSFT diario, Kaggle validado con fuente externa | ✔ Respalda usar Yahoo Finance como validación |
| Regresión: precio de cierre del día siguiente, MAPE | Clasificación: dirección del día siguiente, P/R/F1 | ↔ Diferencia principal |
| Features: OHLC de 5 días + EMA + Bandas de Bollinger | Rendimientos rezagados + medias móviles + volumen | ◐ Parecidas |
| 1/3 entrenamiento, 2/3 flujo | 2021 entrenamiento, 2022–2026 prueba | ✔ Partición temporal |
| Detección instancia a instancia | Evaluación por ventana semestral | ↔ Nosotros reaccionamos más lento |
| Reentrenar por detección < actualizar siempre (p. 7) | B vs. A estático | ⚠ B > A respaldado, pero B podría perder ante un reentrenamiento más frecuente |

## Qué reutilizar o adaptar (sin copiar)

- **Reglas de DDM (p. 3):** alerta si `p_i + s_i ≥ p_min + 2·s_min`, deriva si
  `≥ p_min + 3·s_min`. En datos bursátiles el mejor ajuste fue alerta = 1σ, deriva = 2σ, con
  un mínimo de 100 instancias (p. 6). **Adaptación posible:** aplicar esta regla a la tasa
  de error diaria de B dentro de la ventana, como alternativa o validación del umbral de F1.
- **ECDD (p. 4, 6):** media móvil exponencial del error con λ = 0,2 como mejor parámetro.
  Es otro candidato de umbral.
- **Bucle de las Figs. 1 y 2 (p. 4):** "entrenar → predecir → medir el error → si hay deriva,
  reentrenar con lo acumulado". Escribir **nuestra** versión en pseudocódigo para el plan,
  ajustada a ventanas.
- **Evaluación estadística (p. 5):** 50 ejecuciones + test de Wilcoxon al 95 %. **Adaptación:**
  Wilcoxon *pareado* entre el F1 de A y el de B por ventana. Con 8 ventanas la potencia es
  baja, y eso hay que declararlo.
- **Features técnicas:** evaluar si agregar Bandas de Bollinger (decisión del equipo).

## Entregable

- 5 viñetas: qué confirma, qué cuestiona y qué falta en nuestro diseño.
- Recomendación: ¿adoptamos alguna regla DDM/ECDD como umbral? ¿Agregamos el grupo C
  (reentrenamiento periódico)?
- Pseudocódigo del bucle del grupo B adaptado a ventanas.
