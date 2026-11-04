# Datos crudos

## MSFT_5years_cleaned.csv

| Campo | Valor |
|---|---|
| Fuente | Kaggle: [ashrafkhetran/microsoft-stock-price-analysis-and-forecasting](https://www.kaggle.com/datasets/ashrafkhetran/microsoft-stock-price-analysis-and-forecasting) |
| Autor | Ashraf Khetran |
| Licencia | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Se redistribuye sin modificaciones, con atribución |
| Versión descargada | Última actualización del dataset: 2026-02-02 |
| Fecha de descarga | 2026-11-03, vía API pública de Kaggle |
| SHA-256 | `1617484d95f94f5968c176246decee0680c39cdb7733b503d73bda03eafe86f7` |
| Filas | 1254 (2021-02-04 → 2026-02-02) |
| Columnas | `date, close, high, low, open, volume, price_change, price_change_pct, day_of_week, month, year, quarter` |

**Observaciones de la inspección inicial:**
- Las 2 celdas vacías son `price_change` y `price_change_pct` de la primera fila, que no tiene
  día anterior. Es lo esperado.
- Los precios parecen **ajustados por dividendos**: el cierre del 2021-02-04 figura en ≈ 232,2
  y el cierre nominal de ese día fue ≈ 242. La validación contra Yahoo Finance (FR-002) debe
  compararlo con el cierre ajustado.
- `day_of_week` usa lunes = 0.

**Regla:** este archivo no se edita. Toda limpieza o transformación genera un archivo nuevo
fuera de `data/raw/`. Si el hash no coincide, los resultados no son reproducibles.
