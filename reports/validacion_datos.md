# Validación externa del dataset (FR-002)

- Dataset: `data/raw/MSFT_5years_cleaned.csv` (SHA-256 `1617484d95f94f5968c176246decee0680c39cdb7733b503d73bda03eafe86f7`)
- Fuente externa: Yahoo Finance vía `yfinance`, ticker `MSFT`, precios ajustados
- Tolerancias: precio 0.50%, volumen 5.00%

## Resultado

**Hay discrepancias sobre la tolerancia.**

- Fechas: local 1254, externa 1254, comunes 1254
- Solo en el dataset: ninguna
- Solo en la fuente externa: ninguna

- Factor de ajuste constante (dataset / Yahoo, mediana del cierre): **1.006344**. Yahoo reajusta por los dividendos pagados después de la descarga del dataset; el factor es multiplicativo y constante, por lo que no altera rendimientos ni features relativas. Las diferencias de la tabla se miden **después** de aplicarlo.

| Campo | Diferencia relativa máx. | Media | Filas sobre tolerancia |
|---|---|---|---|
| close | 0.3779% | 0.0003% | 0 |
| open | 0.0035% | 0.0000% | 0 |
| high | 0.0009% | 0.0000% | 0 |
| low | 0.4618% | 0.0004% | 0 |
| volume | 51.6768% | 0.0413% | 1 |

Mayores diferencias de cierre: 2026-02-02 (0.378%), 2022-04-07 (0.000%), 2021-11-22 (0.000%), 2022-04-18 (0.000%), 2021-09-20 (0.000%)

Mayores diferencias de volumen: 2026-02-02 (51.68%), 2026-01-30 (0.16%), 2021-02-04 (0.00%)
