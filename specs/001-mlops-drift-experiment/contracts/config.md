# Contrato: `experiment.toml`

Concentra **todos** los parámetros del experimento. Se versiona en git antes de la primera
ejecución sobre la prueba (SC-008). Cada parámetro de diseño lleva un campo `fuente` que
remite a `literature-review/` o a la sección Clarifications de la spec (Principio IV). Si
falta un campo, el cargador falla con el código 2.

```toml
seed = 42

[data]
path = "data/raw/MSFT_5years_cleaned.csv"
sha256 = "1617484d95f94f5968c176246decee0680c39cdb7733b503d73bda03eafe86f7"
expected_rows = 1254
fuente = "data/raw/README.md"

[split]
tune_train = ["2021-02-04", "2021-09-30"]
tune_valid = ["2021-10-01", "2021-12-31"]
initial_fit = ["2021-02-04", "2021-12-31"]   # clarify Q1
test_windows = "semiannual"                 # 2022-H1 … 2025-H2 (FR-008)
exclude_after = "2025-12-31"                # clarify Q4
fuente = "spec Clarifications Q1, Q4; [6] p. 5"

[features]
names = ["ret_1", "ret_2", "ret_5", "px_sma5", "px_sma20", "vol_sma20"]
fuente = "research R2; [6] p. 5"

[models.lr]
grid = { C = [0.01, 0.1, 1.0, 10.0] }
[models.rf]
n_estimators = 300
grid = { max_depth = [3, 5, "none"], min_samples_leaf = [5, 20] }
[models]
select_by = "f1"
fuente = "[13] p. 2; [20]; [22]"

[retrain]
window = "two_semesters"   # último año
purge_days = 1
fuente = "[13] p. 3; research R5"

[trigger.drift]
test = "ks"
alpha = 0.05
correction = "bonferroni"  # min(p) < alpha / K
fuente = "[9] p. 4, p. 6; spec Clarifications Q3"

[trigger.f1]
k_sigma = 2.0
holdout_fraction = 0.2
bootstrap_samples = 1000
fuente = "[6] p. 3, p. 6; [12] p. 19; spec Clarifications Q2"

[comparison]
test = "wilcoxon_paired"
alpha = 0.05
pairs = ["B-A", "C-A", "B-C"]
fuente = "[6] p. 5; spec Clarifications Q5"
```

**Reglas:**
- No hay parámetros por grupo. A, B y C leen los mismos valores (Principio III). La única
  diferencia entre grupos está en el código de la política.
- Cambiar un valor después de la primera ejecución sobre la prueba requiere un commit con la
  justificación, que queda en el historial (SC-008).
