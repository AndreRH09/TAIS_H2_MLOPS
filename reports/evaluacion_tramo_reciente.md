# Evaluación del Tramo Reciente: Julio 2025 a Enero 2026

- **Periodo evaluado:** `2025-07-01` a `2026-01-30` (148 días bursátiles)
- **Periodo reentrenamiento:** `2024-06-26` a `2025-06-27` (252 días bursátiles)
- **Total subidas reales en el tramo:** `75 de 148` (50.7 %)

## Resultados Comparativos

| Réplica | Configuración / Modelo | Periodo de Entrenamiento | F1 | Precision | Recall |
|---|---|---|:---:|:---:|:---:|
| baseline | Siempre Sube | Heurística (dummy) | 0.673 | 0.507 | 1.000 |
| baseline | Persistencia | Heurística (signo ret_0) | 0.493 | 0.493 | 0.493 |
| baseline | Estratificado | Proporción 2021 (0.521) | 0.487 | 0.469 | 0.507 |
| logreg | Grupo A (Estático) | 2021 (2021-03-04 a 2021-12-31) | 0.558 | 0.495 | 0.640 |
| logreg | Grupo B/C (Reentrenado 1 año) | Último año (2024-06-26 a 2025-06-27) | 0.650 | 0.516 | 0.880 |
| rf | Grupo A (Estático) | 2021 (2021-03-04 a 2021-12-31) | 0.419 | 0.425 | 0.413 |
| rf | Grupo B/C (Reentrenado 1 año) | Último año (2024-06-26 a 2025-06-27) | 0.583 | 0.510 | 0.680 |

## Conclusión del Tramo Reciente
- En **Regresión Logística**, el reentrenamiento reciente mejoró el F1 en **+0.092** (+9.2 puntos porcentuales).
- En **Random Forest**, el reentrenamiento reciente mejoró el F1 en **+0.164** (+16.4 puntos porcentuales).
- En ambos casos, el modelo reentrenado con el último año superó al modelo estático congelado en 2021, confirmando que en el tramo final el modelo inicial sufrió obsolescencia severa.
