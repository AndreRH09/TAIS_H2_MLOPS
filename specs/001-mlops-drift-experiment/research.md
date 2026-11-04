# Research: decisiones técnicas (Fase 0)

Las decisiones de **diseño experimental** (partición, umbrales, comparación) están respaldadas
en [`literature-review/`](../../literature-review/) y en la sección Clarifications de
[spec.md](spec.md). Este documento resuelve las incógnitas de **implementación**. Los números
entre corchetes remiten a [referencias.md](../../literature-review/referencias.md).

---

## R1. Versión de Python y gestión del entorno

- **Decision:** Python 3.12, gestionado con uv (`.python-version`, `pyproject.toml`,
  `uv.lock`).
- **Rationale:** el Python por defecto de la máquina es 3.14, demasiado reciente para
  garantizar ruedas precompiladas de scikit-learn, mlflow y evidently. 3.12 es estable y
  tiene soporte amplio. uv descarga el intérprete si falta, así que el equipo no instala
  Python a mano.
- **Alternatives considered:** 3.14 (riesgo de dependencias sin soporte); 3.11 (sin ventaja
  sobre 3.12).

## R2. Features (FR-005, FR-006a)

- **Decision:** K = 6 features relativas, calculadas con datos hasta `t`:
  1. `ret_1`: rendimiento de `t−1` a `t`.
  2. `ret_2`: rendimiento a 2 días.
  3. `ret_5`: rendimiento a 5 días.
  4. `px_sma5`: `close_t / SMA5_t − 1`.
  5. `px_sma20`: `close_t / SMA20_t − 1`.
  6. `vol_sma20`: `volume_t / mediaVol20_t − 1`.

  Etiqueta: `y_t = 1` si `close_{t+1} > close_t`. Se descartan las primeras 20 filas, que no
  tienen historia suficiente, y la última, que no tiene `t+1`.
- **Rationale:** son adimensionales, así que el test de deriva no se dispara solo por la
  tendencia de precio (≈ USD 240 → 500). Cubren rezagos, medias móviles y volumen como pide
  la spec, y son similares a las features técnicas de [6] p. 5 (OHLC de 5 días, EMA).
- **Alternatives considered:** precios en niveles (deriva permanente); Bandas de Bollinger
  (pendiente, según la lectura de Frank; si se agregan, K cambia y Bonferroni se ajusta solo).

## R3. Cálculo de la deriva (FR-012a)

- **Decision:** la decisión se calcula con `scipy.stats.ks_2samp` por feature y se aplica
  Bonferroni (`min(p) < 0,05/K`). Evidently genera un reporte HTML de deriva por ventana que se
  registra como artefacto en MLflow, sin intervenir en la decisión.
- **Rationale:** el método es exactamente el de [9] p. 4. scipy ya es dependencia de
  scikit-learn, es determinista y se prueba con casos sintéticos. La API de Evidently cambió
  mucho entre versiones; aislarla en la capa de reporte evita que un cambio de versión altere
  los resultados.
- **Alternatives considered:** decidir con `DataDriftPreset` de Evidently (regla del 50 % de
  columnas, sin respaldo, rechazada en clarify); escribir KS a mano (innecesario).

## R4. Referencia y σ para el umbral de F1 (FR-013a)

- **Decision:**
  - Para cada versión de modelo, la referencia sale de ajustar con el primer 80 % de su
    periodo de entrenamiento (en orden temporal) y evaluar en el último 20 %.
  - σ se estima con 1 000 remuestras bootstrap de ese hold-out, cada una del tamaño medio de
    una ventana (≈ 126), con semilla fija.
  - El modelo desplegado se reajusta con el 100 % del periodo.
  - Para la versión inicial, el hold-out es exactamente la validación de oct–dic 2021.
- **Rationale:** evita evaluar la referencia con datos que el modelo ya vio. Remuestrear al
  tamaño de la ventana hace que σ refleje el ruido de una ventana real. Es coherente con el
  "MSE en tiempo de entrenamiento" de [13] p. 3.
- **Alternatives considered:** σ analítico de F1 (no hay fórmula cerrada simple);
  hold-out = ventana anterior (mezcla la referencia con el desempeño en producción).
- **Limitación declarada:** el hold-out (~50 días) es menor que la remuestra (126), así que el
  bootstrap repite días y puede subestimar σ. Se documenta como amenaza a la validez.

## R5. Ventanas, datos de reentrenamiento y purga (FR-007, FR-008, FR-011a, FR-013)

- **Decision:**
  - Ventanas por semestre calendario (H1 = ene–jun, H2 = jul–dic), de 2022-H1 a 2025-H2.
  - El tramo 2026-01-01 → 2026-02-02 se excluye.
  - El reentrenamiento al cierre de la ventana *k* usa los dos semestres anteriores
    (*k−1* y *k*, ≈ 252 días) y **purga** el último día, cuya etiqueta depende del primer
    cierre de la ventana *k+1*.
  - La nueva versión predice desde la ventana *k+1*.
- **Rationale:** dos semestres equivalen al "último año" de la spec y coinciden con el año de
  entrenamiento de [13] p. 3. La purga elimina la única fuga posible en el límite de ventana.
- **Alternatives considered:** 252 días hábiles exactos (prácticamente igual y menos legible);
  sin purga (fuga de un día).

## R6. Modelos e hiperparámetros (FR-009, FR-010)

- **Decision:**
  - LR: `Pipeline(StandardScaler, LogisticRegression)` con `C ∈ {0,01; 0,1; 1; 10}`.
  - RF: `RandomForestClassifier(n_estimators=300)`, `max_depth ∈ {3, 5, None}`,
    `min_samples_leaf ∈ {5, 20}`, `random_state` fijo.
  - Se selecciona por F1 entrenando con feb–sep 2021 y evaluando en oct–dic 2021. Los
    hiperparámetros elegidos se **congelan** para todas las versiones de la réplica
    (Principio III).
- **Rationale:** mallas pequeñas, adecuadas para ≈ 160 filas. Congelar los hiperparámetros
  evita que B y C ganen por reajustarlos.
- **Alternatives considered:** reajustar los hiperparámetros en cada reentrenamiento (rompe la
  comparabilidad); `TimeSeriesSplit` dentro de 2021 (más costoso; queda opcional, como en
  [13] p. 3).

## R7. Baselines ingenuos (FR-017)

- **Decision:**
  - `always_up` (siempre 1).
  - `persistence`: la dirección de hoy es la de ayer, es decir, `y_hat_t = 1` si
    `ret_1_t > 0`.
  - `stratified`: Bernoulli con la proporción de subidas del entrenamiento de 2021 y semilla
    fija.
- **Rationale:** son los comparadores mínimos para saber si A, B o C superan al azar ([18]).
- **Alternatives considered:** `DummyClassifier` de scikit-learn. Cubre `always_up` y
  `stratified`, así que se usa para esos dos.

## R8. Registro en MLflow (FR-015, FR-018, Principio II)

- **Decision:**
  - Tracking URI `sqlite:///mlflow.db`, artefactos en `./mlartifacts`, experimento
    `msft-drift`.
  - Un run por ejecución completa, con runs anidados por réplica × grupo.
  - Las métricas por ventana se registran con `step = índice de ventana`.
  - Cada versión de modelo se registra en el Model Registry como `msft-{replica}-{group}`, con
    tags `reason`, `train_start`, `train_end`, `f1_ref`, `sigma` y `data_sha256`.
- **Rationale:** el Model Registry necesita un backend con base de datos, y SQLite lo cubre
  sin servidor. `step` permite ver la serie temporal en la UI.
- **Alternatives considered:** el file store `mlruns/` (no soporta el registry); PostgreSQL
  (innecesario para un solo usuario por ejecución).

## R9. Validación externa con Yahoo Finance (FR-002)

- **Decision:**
  - Script `validate` con `yfinance`, en un grupo de dependencias opcional `validation`.
  - Descarga MSFT diario del mismo rango **con precios ajustados** y guarda un snapshot en
    `data/external/msft_yahoo_adjusted.csv` con su SHA-256, una sola vez.
  - Compara fechas (presentes y faltantes) y precio de cierre (tolerancia relativa de 0,5 %).
  - Escribe `results/data_validation.md`.
- **Rationale:** Yahoo restringe la descarga manual de CSV. El snapshot versionado permite
  repetir la validación sin red. Los precios de Kaggle están ajustados por dividendos, así que
  la comparación debe hacerse contra el ajustado.
- **Alternatives considered:** CSV manual (no disponible de forma fiable); no validar (lo exige
  FR-002 y la amenaza a la validez del diseño original).

## R10. Comparación estadística y reporte (FR-019a)

- **Decision:**
  - `scipy.stats.wilcoxon(x, y)` pareado por ventana, bilateral, α = 0,05, para B−A, C−A y
    B−C en cada réplica.
  - Se reportan la diferencia media, las ventanas ganadas y el p-valor.
  - Figuras con matplotlib: F1 por ventana para A/B/C/baselines, con los reentrenamientos
    marcados (inspirado en el gráfico de envejecimiento de [13] p. 4).
  - Salida en `results/report.md`.
- **Rationale:** es el test de [6] p. 5 en su versión pareada. matplotlib es estándar y no
  requiere servidor.
- **Alternatives considered:** bootstrap por bloques (opción C en clarify, rechazada);
  Grafana o dashboards (fuera de alcance).
- **Nota:** con diferencias nulas, la opción por defecto de `wilcoxon` las descarta; se
  reporta el n efectivo.
