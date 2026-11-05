# Resumen comparativo: modelo estático (A) vs. monitoreo (B) vs. periódico (C)

Generado automáticamente por `msft-mlops report`. Clase positiva = "sube". Las métricas se esperan bajas (dirección diaria difícil de predecir); el interés está en las **diferencias** entre grupos. `n/d` = métrica indefinida (sin positivos reales o predichos), no un cero.

- Semilla: `42`; SHA-256 del dataset: `1617484d95f94f5968c176246decee0680c39cdb7733b503d73bda03eafe86f7`
- Ventanas de prueba: 8 semestres (2022-H1 … 2025-H2)
- Tramo excluido (posterior a 2025-12-31): **20 registros** (2026-01-02 … 2026-01-30), fuera de métricas, disparadores y comparaciones.

## Réplica: Regresión logística

### F1 por ventana

| ventana | A | B | C | siempre_sube | persistencia | estratificado |
|---|---|---|---|---|---|---|
| 2022-H1 | 0.538 | 0.538 | 0.538 | 0.652 | 0.420 | 0.512 |
| 2022-H2 | 0.528 | 0.429 | 0.429 | 0.612 | 0.513 | 0.500 |
| 2023-H1 | 0.580 | 0.449 | 0.197 | 0.681 | 0.562 | 0.543 |
| 2023-H2 | 0.600 | 0.429 | 0.429 | 0.740 | 0.554 | 0.588 |
| 2024-H1 | 0.582 | 0.655 | 0.655 | 0.702 | 0.541 | 0.492 |
| 2024-H2 | 0.490 | 0.639 | 0.639 | 0.694 | 0.584 | 0.525 |
| 2025-H1 | 0.569 | 0.566 | 0.566 | 0.723 | 0.507 | 0.569 |
| 2025-H2 | 0.568 | 0.678 | 0.678 | 0.680 | 0.485 | 0.493 |
| media | 0.557 | 0.548 | 0.516 | 0.685 | 0.521 | 0.528 |

### Precision por ventana

| ventana | A | B | C | siempre_sube | persistencia | estratificado |
|---|---|---|---|---|---|---|
| 2022-H1 | 0.500 | 0.500 | 0.500 | 0.484 | 0.424 | 0.492 |
| 2022-H2 | 0.478 | 0.429 | 0.429 | 0.441 | 0.509 | 0.456 |
| 2023-H1 | 0.541 | 0.558 | 1.000 | 0.516 | 0.562 | 0.538 |
| 2023-H2 | 0.592 | 0.519 | 0.519 | 0.587 | 0.554 | 0.645 |
| 2024-H1 | 0.554 | 0.551 | 0.551 | 0.540 | 0.545 | 0.508 |
| 2024-H2 | 0.467 | 0.541 | 0.541 | 0.531 | 0.580 | 0.507 |
| 2025-H1 | 0.574 | 0.518 | 0.518 | 0.566 | 0.507 | 0.607 |
| 2025-H2 | 0.512 | 0.535 | 0.535 | 0.516 | 0.485 | 0.472 |
| media | 0.527 | 0.519 | 0.574 | 0.523 | 0.521 | 0.528 |

### Recall por ventana

| ventana | A | B | C | siempre_sube | persistencia | estratificado |
|---|---|---|---|---|---|---|
| 2022-H1 | 0.583 | 0.583 | 0.583 | 1.000 | 0.417 | 0.533 |
| 2022-H2 | 0.589 | 0.429 | 0.429 | 1.000 | 0.518 | 0.554 |
| 2023-H1 | 0.625 | 0.375 | 0.109 | 1.000 | 0.562 | 0.547 |
| 2023-H2 | 0.608 | 0.365 | 0.365 | 1.000 | 0.554 | 0.541 |
| 2024-H1 | 0.612 | 0.806 | 0.806 | 1.000 | 0.537 | 0.478 |
| 2024-H2 | 0.515 | 0.779 | 0.779 | 1.000 | 0.588 | 0.544 |
| 2025-H1 | 0.565 | 0.623 | 0.623 | 1.000 | 0.507 | 0.536 |
| 2025-H2 | 0.636 | 0.924 | 0.924 | 1.000 | 0.485 | 0.515 |
| media | 0.592 | 0.611 | 0.577 | 1.000 | 0.521 | 0.531 |

### Diferencias de F1 por ventana

| ventana | B−A | C−A | B−C |
|---|---|---|---|
| 2022-H1 | 0.000 | 0.000 | 0.000 |
| 2022-H2 | -0.099 | -0.099 | 0.000 |
| 2023-H1 | -0.131 | -0.383 | 0.251 |
| 2023-H2 | -0.171 | -0.171 | 0.000 |
| 2024-H1 | 0.073 | 0.073 | 0.000 |
| 2024-H2 | 0.149 | 0.149 | 0.000 |
| 2025-H1 | -0.004 | -0.004 | 0.000 |
| 2025-H2 | 0.110 | 0.110 | 0.000 |

### Reentrenamientos

- **Grupo B**: 7 reentrenamientos
  - tras 2022-H1 → versión 2 (deriva); rige desde: 2022-H2; F1_ref=0.395, σ=0.055
  - tras 2023-H1 → versión 3 (deriva); rige desde: 2023-H2; F1_ref=0.272, σ=0.062
  - tras 2023-H2 → versión 4 (deriva); rige desde: 2024-H1; F1_ref=0.539, σ=0.048
  - tras 2024-H1 → versión 5 (deriva); rige desde: 2024-H2; F1_ref=0.606, σ=0.045
  - tras 2024-H2 → versión 6 (deriva); rige desde: 2025-H1; F1_ref=0.691, σ=0.043
  - tras 2025-H1 → versión 7 (deriva+caida_f1); rige desde: 2025-H2; F1_ref=0.601, σ=0.048
  - tras 2025-H2 → versión 8 (deriva); rige desde: sin ventana posterior; F1_ref=0.649, σ=0.045
- **Grupo C**: 8 reentrenamientos
  - tras 2022-H1 → versión 2 (periodico); rige desde: 2022-H2; F1_ref=0.395, σ=0.055
  - tras 2022-H2 → versión 3 (periodico); rige desde: 2023-H1; F1_ref=0.221, σ=0.056
  - tras 2023-H1 → versión 4 (periodico); rige desde: 2023-H2; F1_ref=0.272, σ=0.062
  - tras 2023-H2 → versión 5 (periodico); rige desde: 2024-H1; F1_ref=0.539, σ=0.048
  - tras 2024-H1 → versión 6 (periodico); rige desde: 2024-H2; F1_ref=0.606, σ=0.045
  - tras 2024-H2 → versión 7 (periodico); rige desde: 2025-H1; F1_ref=0.691, σ=0.043
  - tras 2025-H1 → versión 8 (periodico); rige desde: 2025-H2; F1_ref=0.601, σ=0.048
  - tras 2025-H2 → versión 9 (periodico); rige desde: sin ventana posterior; F1_ref=0.649, σ=0.045

Observación automática: en B se detectó deriva en 7 de 8 ventanas y se activó el disparador de caída de F1 en 1. Si B reentrena casi siempre, su política se aproxima a la de C y la diferencia B−C tiende a cero.

### Deriva de features por ventana (grupo B, vs. referencia de su versión vigente)

| ventana | version | drift_detected | drift_min_p | drift_threshold | f1 |
|---|---|---|---|---|---|
| 2022-H1 | 1 | sí | 0.000 | 0.006 | 0.538 |
| 2022-H2 | 2 | no | 0.053 | 0.006 | 0.429 |
| 2023-H1 | 2 | sí | 0.000 | 0.006 | 0.449 |
| 2023-H2 | 3 | sí | 0.003 | 0.006 | 0.429 |
| 2024-H1 | 4 | sí | 0.005 | 0.006 | 0.655 |
| 2024-H2 | 5 | sí | 0.004 | 0.006 | 0.639 |
| 2025-H1 | 6 | sí | 0.000 | 0.006 | 0.566 |
| 2025-H2 | 7 | sí | 0.000 | 0.006 | 0.678 |

### Contraste estadístico (Wilcoxon pareado sobre F1, α = 0,05)

| comparison | n_effective | mean_diff_f1 | windows_won | windows_lost | windows_tied | wilcoxon_statistic | p_value | significant_at_0_05 |
|---|---|---|---|---|---|---|---|---|
| B-A | 8 | -0.009 | 3 | 4 | 1 | 12.000 | 0.812 | no |
| C-A | 8 | -0.041 | 3 | 4 | 1 | 11.000 | 0.688 | no |
| B-C | 8 | 0.031 | 1 | 0 | 7 | 0.000 | 1.000 | no |

## Réplica: Random Forest

### F1 por ventana

| ventana | A | B | C | siempre_sube | persistencia | estratificado |
|---|---|---|---|---|---|---|
| 2022-H1 | 0.507 | 0.507 | 0.507 | 0.652 | 0.420 | 0.512 |
| 2022-H2 | 0.625 | 0.439 | 0.439 | 0.612 | 0.513 | 0.500 |
| 2023-H1 | 0.627 | 0.480 | 0.495 | 0.681 | 0.562 | 0.543 |
| 2023-H2 | 0.531 | 0.397 | 0.397 | 0.740 | 0.554 | 0.588 |
| 2024-H1 | 0.500 | 0.579 | 0.579 | 0.702 | 0.541 | 0.492 |
| 2024-H2 | 0.476 | 0.636 | 0.636 | 0.694 | 0.584 | 0.525 |
| 2025-H1 | 0.565 | 0.623 | 0.623 | 0.723 | 0.507 | 0.569 |
| 2025-H2 | 0.419 | 0.610 | 0.610 | 0.680 | 0.485 | 0.493 |
| media | 0.531 | 0.534 | 0.536 | 0.685 | 0.521 | 0.528 |

### Precision por ventana

| ventana | A | B | C | siempre_sube | persistencia | estratificado |
|---|---|---|---|---|---|---|
| 2022-H1 | 0.439 | 0.439 | 0.439 | 0.484 | 0.424 | 0.492 |
| 2022-H2 | 0.511 | 0.382 | 0.382 | 0.441 | 0.509 | 0.456 |
| 2023-H1 | 0.539 | 0.492 | 0.634 | 0.516 | 0.562 | 0.538 |
| 2023-H2 | 0.534 | 0.456 | 0.456 | 0.587 | 0.554 | 0.645 |
| 2024-H1 | 0.525 | 0.518 | 0.518 | 0.540 | 0.545 | 0.508 |
| 2024-H2 | 0.517 | 0.578 | 0.578 | 0.531 | 0.580 | 0.507 |
| 2025-H1 | 0.565 | 0.565 | 0.565 | 0.566 | 0.507 | 0.607 |
| 2025-H2 | 0.448 | 0.534 | 0.534 | 0.516 | 0.485 | 0.472 |
| media | 0.510 | 0.495 | 0.513 | 0.523 | 0.521 | 0.528 |

### Recall por ventana

| ventana | A | B | C | siempre_sube | persistencia | estratificado |
|---|---|---|---|---|---|---|
| 2022-H1 | 0.600 | 0.600 | 0.600 | 1.000 | 0.417 | 0.533 |
| 2022-H2 | 0.804 | 0.518 | 0.518 | 1.000 | 0.518 | 0.554 |
| 2023-H1 | 0.750 | 0.469 | 0.406 | 1.000 | 0.562 | 0.547 |
| 2023-H2 | 0.527 | 0.351 | 0.351 | 1.000 | 0.554 | 0.541 |
| 2024-H1 | 0.478 | 0.657 | 0.657 | 1.000 | 0.537 | 0.478 |
| 2024-H2 | 0.441 | 0.706 | 0.706 | 1.000 | 0.588 | 0.544 |
| 2025-H1 | 0.565 | 0.696 | 0.696 | 1.000 | 0.507 | 0.536 |
| 2025-H2 | 0.394 | 0.712 | 0.712 | 1.000 | 0.485 | 0.515 |
| media | 0.570 | 0.589 | 0.581 | 1.000 | 0.521 | 0.531 |

### Diferencias de F1 por ventana

| ventana | B−A | C−A | B−C |
|---|---|---|---|
| 2022-H1 | 0.000 | 0.000 | 0.000 |
| 2022-H2 | -0.186 | -0.186 | 0.000 |
| 2023-H1 | -0.147 | -0.132 | -0.015 |
| 2023-H2 | -0.134 | -0.134 | 0.000 |
| 2024-H1 | 0.079 | 0.079 | 0.000 |
| 2024-H2 | 0.160 | 0.160 | 0.000 |
| 2025-H1 | 0.058 | 0.058 | 0.000 |
| 2025-H2 | 0.191 | 0.191 | 0.000 |

### Reentrenamientos

- **Grupo B**: 7 reentrenamientos
  - tras 2022-H1 → versión 2 (deriva); rige desde: 2022-H2; F1_ref=0.450, σ=0.056
  - tras 2023-H1 → versión 3 (deriva); rige desde: 2023-H2; F1_ref=0.375, σ=0.061
  - tras 2023-H2 → versión 4 (deriva); rige desde: 2024-H1; F1_ref=0.567, σ=0.048
  - tras 2024-H1 → versión 5 (deriva); rige desde: 2024-H2; F1_ref=0.621, σ=0.047
  - tras 2024-H2 → versión 6 (deriva); rige desde: 2025-H1; F1_ref=0.581, σ=0.051
  - tras 2025-H1 → versión 7 (deriva); rige desde: 2025-H2; F1_ref=0.677, σ=0.044
  - tras 2025-H2 → versión 8 (deriva); rige desde: sin ventana posterior; F1_ref=0.536, σ=0.053
- **Grupo C**: 8 reentrenamientos
  - tras 2022-H1 → versión 2 (periodico); rige desde: 2022-H2; F1_ref=0.450, σ=0.056
  - tras 2022-H2 → versión 3 (periodico); rige desde: 2023-H1; F1_ref=0.447, σ=0.056
  - tras 2023-H1 → versión 4 (periodico); rige desde: 2023-H2; F1_ref=0.375, σ=0.061
  - tras 2023-H2 → versión 5 (periodico); rige desde: 2024-H1; F1_ref=0.567, σ=0.048
  - tras 2024-H1 → versión 6 (periodico); rige desde: 2024-H2; F1_ref=0.621, σ=0.047
  - tras 2024-H2 → versión 7 (periodico); rige desde: 2025-H1; F1_ref=0.581, σ=0.051
  - tras 2025-H1 → versión 8 (periodico); rige desde: 2025-H2; F1_ref=0.677, σ=0.044
  - tras 2025-H2 → versión 9 (periodico); rige desde: sin ventana posterior; F1_ref=0.536, σ=0.053

Observación automática: en B se detectó deriva en 7 de 8 ventanas y se activó el disparador de caída de F1 en 0. Si B reentrena casi siempre, su política se aproxima a la de C y la diferencia B−C tiende a cero.

### Deriva de features por ventana (grupo B, vs. referencia de su versión vigente)

| ventana | version | drift_detected | drift_min_p | drift_threshold | f1 |
|---|---|---|---|---|---|
| 2022-H1 | 1 | sí | 0.000 | 0.006 | 0.507 |
| 2022-H2 | 2 | no | 0.053 | 0.006 | 0.439 |
| 2023-H1 | 2 | sí | 0.000 | 0.006 | 0.480 |
| 2023-H2 | 3 | sí | 0.003 | 0.006 | 0.397 |
| 2024-H1 | 4 | sí | 0.005 | 0.006 | 0.579 |
| 2024-H2 | 5 | sí | 0.004 | 0.006 | 0.636 |
| 2025-H1 | 6 | sí | 0.000 | 0.006 | 0.623 |
| 2025-H2 | 7 | sí | 0.000 | 0.006 | 0.610 |

### Contraste estadístico (Wilcoxon pareado sobre F1, α = 0,05)

| comparison | n_effective | mean_diff_f1 | windows_won | windows_lost | windows_tied | wilcoxon_statistic | p_value | significant_at_0_05 |
|---|---|---|---|---|---|---|---|---|
| B-A | 8 | 0.003 | 4 | 3 | 1 | 13.000 | 0.938 | no |
| C-A | 8 | 0.005 | 4 | 3 | 1 | 13.000 | 0.938 | no |
| B-C | 8 | -0.002 | 0 | 1 | 7 | 0.000 | 1.000 | no |

## Amenazas a la validez

- **Un activo y un periodo**: MSFT 2021–2026; no se generaliza a otros activos o regímenes.
- **Potencia baja**: con n = 8 ventanas el test de Wilcoxon solo detecta diferencias muy consistentes (p mínimo bilateral = 0,0078); un resultado no significativo no implica igualdad.
- **Bootstrap i.i.d.**: el σ del F1 remuestrea pares (y, ŷ) como independientes y no refleja la autocorrelación; puede subestimar o sobrestimar el umbral de caída.
- **Hold-out corto**: 63 filas para estimar `F1_ref` y σ.
- **Dos réplicas, no independientes**: LR y RF usan los mismos datos; no son muestras independientes del mundo.
- **Precios ajustados por dividendos**: la validación externa debe compararse con el cierre ajustado (ver `reports/validacion_datos.md` si existe).
- **F1 indefinido** (sin positivos predichos o reales) no dispara reentrenamiento en B y se excluye de las comparaciones pareadas.
- **Múltiples comparaciones**: se hacen 3 contrastes por réplica sin corrección adicional.

## Trazabilidad con la literatura

| Parámetro | Valor | Respaldo (`literature-review/decisiones.md`) |
|---|---|---|
| Partición temporal sin barajado | 2021 ajuste/validación; 2022+ prueba | D1: [15], [16], [18], [19] |
| Ventanas semestrales | 8 × ≈ 126 registros | D2: [13], [17] (compromiso propio, ver brecha) |
| Clasificadores | LR y RF como réplicas | D3: [13], [19], [20], [22], [23] |
| Baselines ingenuos | siempre sube, persistencia, estratificado | D4: [18], [22] |
| Disparador | deriva KS+Bonferroni **o** `F1 < F1_ref − 2σ` | D5: [6], [9], [12] |
| Reentrenamiento | último año (252 filas) | D6: [13] p. 3, [5], [6] |
| Métricas | Precision, Recall, F1 (clase "sube") | D7: [17] |

