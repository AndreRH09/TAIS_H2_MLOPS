---
title: MLOps MSFT - Estático vs. alarmas vs. semestral
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
short_description: ¿Reentrenar un modelo en producción mejora su desempeño?
---

# Comparador de políticas MLOps sobre MSFT

Interfaz del proyecto **TAIS_H2_MLOPS**. Compara tres políticas para operar un modelo que predice
si el cierre de mañana de Microsoft (MSFT) será mayor que el de hoy:

- **Estático (A):** se entrena una vez y no se actualiza.
- **Con alarmas (B):** se reentrena cuando hay deriva en los datos (KS + Bonferroni) o cae el F1.
- **Cada seis meses (C):** se reentrena al cierre de cada semestre.

La página principal muestra los resultados oficiales del experimento (2022-H1 a 2025-H2). En
«Comparar con tus datos» puedes subir tu propio CSV de precios diarios y tu propio clasificador de
scikit-learn (`.skops`) para repetir la comparación.

Código, especificación y documentación: https://github.com/AndreRH09/TAIS_H2_MLOPS

Dataset: [Microsoft Stock Price Analysis and Forecasting](https://www.kaggle.com/datasets/ashrafkhetran/microsoft-stock-price-analysis-and-forecasting),
de Ashraf Khetran, licencia CC BY 4.0.
