# Matriz de contraste

Compara el diseño propio con los estudios empíricos de la revisión, en las dimensiones de
FR-021. Celda `—` = el resumen no da información (⚠ hay que completarla con la lectura
completa). Las fuentes conceptuales o de revisión ([1]–[5], [7], [8], [10], [12], [14], [24])
no se incluyen porque no proponen un diseño experimental propio.

| Estudio | Datos | Partición temporal | Baseline / comparadores | Disparador de reentrenamiento | Métricas |
|---|---|---|---|---|---|
| **Este estudio** | MSFT diario 2021–2026, Kaggle validado con fuente externa | Entrenamiento y validación 2021; prueba walk-forward semestral 2022–2026 | Grupo A estático; baselines ingenuos (Q3) | Deriva de features **o** F1 < umbral | P, R, F1 (+ MCC propuesto) |
| [6] Cavalcante 2015 | Series financieras | Flujo secuencial | OS-ELM sin detección | Detector explícito (DDM, ECDD) | Precisión, tiempo |
| [9] Rabanser 2019 | Datasets con shift inducido ⚠ | — | Varios detectores | Tests de dos muestras (solo detección) | Potencia de detección |
| [11] Celik 2021 | Flujos reales y sintéticos con deriva | Secuencial por lotes | Sin adaptación vs. 6 estrategias | Varía según la estrategia | Desempeño por lote |
| [13] Vela 2022 | 32 datasets (salud, transporte, finanzas, clima) | Entrenamiento en t, evaluación en t + edad | 4 modelos estándar | — (mide el envejecimiento) | Error en función de la edad del modelo |
| [15] Bergmeir 2018 | Simulación + ejemplo real | CV vs. out-of-sample | — | No aplica | Error de pronóstico |
| [16] Cerqueira 2020 | Series reales | Compara CV y out-of-sample | — | No aplica | Error de estimación |
| [19] Kapoor 2023 | Revisión de 294 artículos + caso de guerra civil | Corrige la fuga temporal | LR clásica | No aplica | — |
| [20] Ballings 2015 | 5 767 empresas europeas | Horizonte de 1 año | LR, NN, SVM, KNN vs. RF, AdaBoost, KF | No aplica | AUC |
| [21] Krauss 2017 | S&P 500, 1992–2015 | Fuera de muestra en orden temporal ⚠ | DNN, GBT, RF y ensamble | — ⚠ | Retornos diarios |
| [22] Fischer 2018 | S&P 500, 1992–2015 | Fuera de muestra en orden temporal ⚠ | RF, DNN, LR | — ⚠ | Precisión direccional, retornos |
| [23] Gu 2020 | Acciones de EE. UU. | Recursivo fuera de muestra ⚠ | Regresión lineal vs. ML | — ⚠ | R² fuera de muestra |

## Lectura de la matriz

1. **Partición:** todos los estudios empíricos de finanzas evalúan fuera de muestra en orden
   temporal, igual que este diseño (D1).
2. **Disparador combinado:** [6] usa solo detección de deriva y [13] muestra degradación sin
   deriva. Combinar ambas señales (D5) cubre los dos casos y es lo que distingue a este diseño.
3. **Comparadores:** los estudios bursátiles comparan contra LR y RF ([20], [22]), lo que
   respalda incluir ambos (D3). Ninguno de los resúmenes menciona baselines ingenuos explícitos
   (D4) ⚠.
4. **Métricas:** la literatura bursátil usa AUC, precisión direccional o retornos, no F1. El
   uso de P/R/F1 viene del curso; MCC [17] haría las métricas comparables y simétricas (D7).
