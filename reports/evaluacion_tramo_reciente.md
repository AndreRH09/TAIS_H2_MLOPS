# Evaluación exploratoria del tramo reciente: julio 2025 a enero 2026

- **Periodo evaluado:** `2025-07-01` a `2026-01-30` (148 días bursátiles)
- **Periodo de reentrenamiento:** `2024-06-26` a `2025-06-27` (252 días bursátiles)
- **Subidas reales en el tramo:** `75 de 148` (50.7 %)
- **Hiperparámetros** (selección con 2021, mismo procedimiento que el walk-forward): logreg `{"C": 0.1}`; rf `{"max_depth": 10, "min_samples_leaf": 5, "n_estimators": 100}`

## Alcance

Análisis **exploratorio y posterior al diseño**: no está en la spec, no tiene contraste estadístico y no es una prueba independiente del walk-forward.

- 128 de 148 días pertenecen a ventanas ya evaluadas por `msft-mlops run` (2025-H2).
- 20 días son posteriores a `test_end` (2025-12-31), el tramo que la spec excluye de métricas, disparadores y comparaciones.
- El conjunto de reentrenamiento es el mismo con el que B y C se reentrenaron tras 2025-H1; el modelo «reentrenado» es el que el walk-forward ya usó en 2025-H2.

## Resultados

| Réplica | Configuración / Modelo | Periodo de Entrenamiento | F1 | Precision | Recall |
|---|---|---|:---:|:---:|:---:|
| baseline | Siempre Sube | Heurística (dummy) | 0.673 | 0.507 | 1.000 |
| baseline | Persistencia | Heurística (signo ret_0) | 0.493 | 0.493 | 0.493 |
| baseline | Estratificado | Proporción 2021 (0.521) | 0.487 | 0.469 | 0.507 |
| logreg | Grupo A (Estático) | 2021 (2021-03-04 a 2021-12-31) | 0.558 | 0.495 | 0.640 |
| logreg | Grupo B/C (Reentrenado 1 año) | Último año (2024-06-26 a 2025-06-27) | 0.650 | 0.516 | 0.880 |
| rf | Grupo A (Estático) | 2021 (2021-03-04 a 2021-12-31) | 0.419 | 0.425 | 0.413 |
| rf | Grupo B/C (Reentrenado 1 año) | Último año (2024-06-26 a 2025-06-27) | 0.583 | 0.510 | 0.680 |

## Lectura

- En **Regresión Logística**, el modelo reentrenado mejoró el F1 en **+0.092** (+9.2 puntos porcentuales) frente al estático.
- En **Random Forest**, el modelo reentrenado mejoró el F1 en **+0.164** (+16.4 puntos porcentuales) frente al estático.
- Ningún modelo supervisado supera al baseline «siempre sube» (F1 = 0.673); el mejor es Regresión Logística, Grupo B/C (Reentrenado 1 año) (F1 = 0.650).
- Con F1 de la clase «sube», predecir siempre 1 obtiene recall = 1; un F1 alto con recall alto puede reflejar sesgo alcista más que capacidad predictiva.
