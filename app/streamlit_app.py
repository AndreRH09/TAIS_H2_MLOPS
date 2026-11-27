"""Interfaz web: ¿qué política es más efectiva, estática, con alarmas o cada seis meses?

Ejecutar en local:  uv run streamlit run app/streamlit_app.py
Feature 002 (specs/002-interfaz-despliegue). La lógica está en ``msft_mlops.custom_run``.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
# En Streamlit Community Cloud solo se instala app/requirements.txt, no el paquete: se importa
# desde src/. En local (uv) y en Docker el paquete ya está instalado y esto no cambia nada.
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from msft_mlops.config import load_config  # noqa: E402
from msft_mlops.custom_run import (  # noqa: E402
    BASELINE_NAMES,
    CUSTOM_REPLICA,
    EXAMPLE_REPLICA,
    POLICIES,
    POLICY_NAMES,
    REPLICA_NAMES,
    CustomRunError,
    ExperimentParams,
    as_bool,
    build_config,
    build_manifest,
    describe_model,
    example_model,
    example_model_bytes,
    infer_split,
    load_model_bytes,
    normalize_prices,
    results_zip,
    run_custom_experiment,
    sha256_bytes,
    summarize_split,
    unsafe_models_allowed,
    verdict,
)
from msft_mlops.data import DataHashMismatch, DataValidationError, load_raw  # noqa: E402
from msft_mlops.features import FEATURE_COLUMNS, build_dataset  # noqa: E402

RESULTS = ROOT / "results"
REPO_URL = "https://github.com/AndreRH09/TAIS_H2_MLOPS"

COLORS = {
    "A": "#1f77b4",
    "B": "#d62728",
    "C": "#2ca02c",
    "siempre_sube": "#8c8c8c",
    "persistencia": "#bcbd22",
    "estratificado": "#9467bd",
}
GROUP_ORDER = ["A", "B", "C", "siempre_sube", "persistencia", "estratificado"]
LABELS = {**POLICY_NAMES, **BASELINE_NAMES}
SHORT_POLICY = {"A": "A · Estático", "B": "B · Alarmas", "C": "C · Cada 6 meses"}
METRIC_LABELS = {"f1": "F1", "precision": "Precision", "recall": "Recall"}
COMPARISON_LABELS = {
    "B-A": "Con alarmas (B) − Estático (A)",
    "C-A": "Cada seis meses (C) − Estático (A)",
    "B-C": "Con alarmas (B) − Cada seis meses (C)",
}
QUESTION = (
    "¿Qué política mantiene mejor el desempeño de un modelo en producción: **no reentrenarlo "
    "nunca (A)**, **reentrenarlo cuando saltan las alarmas de deriva o de caída de F1 (B)** o "
    "**reentrenarlo cada seis meses (C)**?"
)

st.set_page_config(
    page_title="MLOps MSFT · Estático vs. alarmas vs. semestral",
    page_icon="📈",
    layout="wide",
)


# ============================================================================== carga


@st.cache_resource
def base_config():
    return load_config(ROOT / "config" / "experiment.toml")


@st.cache_data
def official_results() -> dict[str, pd.DataFrame]:
    tables = {
        name: pd.read_csv(RESULTS / f"{name}.csv")
        for name in ("window_metrics", "model_versions", "drift_details", "comparisons")
    }
    recent = RESULTS / "recent_slice_metrics.csv"
    tables["recent"] = pd.read_csv(recent) if recent.exists() else pd.DataFrame()
    return tables


@st.cache_data
def project_dataset_bytes() -> bytes:
    return base_config().data_path.read_bytes()


@st.cache_data
def example_model_file() -> bytes:
    return example_model_bytes()


def replica_label(name: str) -> str:
    if name in REPLICA_NAMES:
        return REPLICA_NAMES[name]
    if name == CUSTOM_REPLICA:
        return "Tu modelo"
    if name == EXAMPLE_REPLICA:
        return "Modelo de ejemplo (Gradient Boosting)"
    return name


# ============================================================================== gráficos


def _color_scale(groups) -> alt.Scale:
    present = [g for g in GROUP_ORDER if g in set(groups)]
    return alt.Scale(domain=[LABELS[g] for g in present], range=[COLORS[g] for g in present])


def metric_chart(sub: pd.DataFrame, metric: str, show_baselines: bool) -> alt.Chart:
    d = sub[["window_id", "group", metric]].copy()
    if not show_baselines:
        d = d[d["group"].isin(POLICIES)]
    d["Grupo"] = d["group"].map(LABELS)
    d["Tipo"] = np.where(d["group"].isin(POLICIES), "Política", "Baseline")
    d[metric] = d[metric].astype(float)
    return (
        alt.Chart(d)
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X(
                "window_id:O", title="Ventana de prueba (semestre)", axis=alt.Axis(labelAngle=0)
            ),
            y=alt.Y(f"{metric}:Q", title=METRIC_LABELS[metric], scale=alt.Scale(zero=False)),
            color=alt.Color(
                "Grupo:N", scale=_color_scale(d["group"]), legend=alt.Legend(orient="bottom")
            ),
            strokeDash=alt.StrokeDash(
                "Tipo:N",
                scale=alt.Scale(domain=["Política", "Baseline"], range=[[1, 0], [5, 4]]),
                legend=None,
            ),
            tooltip=[
                "Grupo",
                alt.Tooltip("window_id", title="Ventana"),
                alt.Tooltip(f"{metric}:Q", title=METRIC_LABELS[metric], format=".3f"),
            ],
        )
        .properties(height=360)
    )


def diff_chart(sub: pd.DataFrame) -> alt.Chart:
    piv = sub.pivot(index="window_id", columns="group", values="f1").astype(float)
    diffs = pd.DataFrame(
        {
            "B − A": piv["B"] - piv["A"],
            "C − A": piv["C"] - piv["A"],
            "B − C": piv["B"] - piv["C"],
        }
    ).reset_index()
    long = diffs.melt(id_vars="window_id", var_name="Comparación", value_name="Diferencia")
    bars = (
        alt.Chart(long)
        .mark_bar()
        .encode(
            x=alt.X("window_id:O", title="Ventana de prueba", axis=alt.Axis(labelAngle=0)),
            xOffset="Comparación:N",
            y=alt.Y("Diferencia:Q", title="Diferencia de F1"),
            color=alt.Color(
                "Comparación:N",
                scale=alt.Scale(
                    domain=["B − A", "C − A", "B − C"], range=["#d62728", "#2ca02c", "#ff9f40"]
                ),
                legend=alt.Legend(orient="bottom"),
            ),
            tooltip=[
                "Comparación",
                alt.Tooltip("window_id", title="Ventana"),
                alt.Tooltip("Diferencia:Q", format="+.3f"),
            ],
        )
    )
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#888").encode(y="y:Q")
    return (bars + zero).properties(height=300)


def drift_chart(drift_b: pd.DataFrame) -> alt.Chart:
    d = drift_b.copy()
    d["Estado"] = np.where(as_bool(d["drifted"]), "Deriva", "Sin deriva")
    order = [f for f in FEATURE_COLUMNS if f in set(d["feature"])] or sorted(d["feature"].unique())
    return (
        alt.Chart(d)
        .mark_rect(stroke="#ffffff", strokeWidth=1)
        .encode(
            x=alt.X("window_id:O", title="Ventana evaluada", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("feature:N", title="Feature", sort=order),
            color=alt.Color(
                "Estado:N",
                scale=alt.Scale(domain=["Deriva", "Sin deriva"], range=["#d62728", "#9ecae1"]),
                legend=alt.Legend(orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("feature", title="Feature"),
                alt.Tooltip("window_id", title="Ventana"),
                alt.Tooltip("p_value:Q", title="p-valor KS", format=".2e"),
                alt.Tooltip("threshold:Q", title="Umbral α/K", format=".4f"),
                "Estado",
            ],
        )
        .properties(height=alt.Step(26))
    )


# ============================================================================== tablas


def wilcoxon_table(comp: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Comparación": comp["comparison"].map(COMPARISON_LABELS),
            "Diferencia media de F1": comp["mean_diff_f1"].astype(float).round(3),
            "Gana / pierde / empata": [
                f"{int(r.windows_won)} / {int(r.windows_lost)} / {int(r.windows_tied)}"
                for r in comp.itertuples()
            ],
            "p (Wilcoxon)": comp["p_value"].astype(float).round(4),
            "¿Significativa (α = 0,05)?": np.where(
                as_bool(comp["significant_at_0_05"]), "Sí", "No"
            ),
        }
    )


def retrain_table(mv: pd.DataFrame) -> pd.DataFrame:
    r = mv[mv["version"].astype(int) > 1].copy()
    used = r["used_from_window"].fillna("").astype(str).replace("", "sin ventana posterior")
    return pd.DataFrame(
        {
            "Política": r["group"].map(POLICY_NAMES),
            "Versión": r["version"].astype(int),
            "Tras la ventana": r["created_after_window"],
            "Rige desde": used,
            "Motivo": r["reason"],
            "Entrenada con": r["train_start"].astype(str) + " → " + r["train_end"].astype(str),
            "F1 de referencia": r["f1_ref"].astype(float).round(3),
            "σ": r["sigma"].astype(float).round(3),
        }
    )


# ============================================================================== resultados


def render_replica(v, wm: pd.DataFrame, mv: pd.DataFrame, drift: pd.DataFrame, key: str) -> None:
    st.markdown("#### Veredicto")
    cols = st.columns(4)
    for col, g in zip(cols, POLICIES, strict=False):
        val = v.mean_f1[g]
        delta = None if g == "A" or np.isnan(val) else f"{val - v.mean_f1['A']:+.3f} vs. A"
        col.metric(
            SHORT_POLICY[g] + (" ★" if g == v.best_policy else ""),
            "n/d" if np.isnan(val) else f"{val:.3f}",
            delta,
            border=True,
            help="F1 medio de la clase «sube» sobre las ventanas de prueba. ★ = mayor F1 medio.",
        )
    cols[3].metric(
        "Siempre sube",
        f"{v.baseline_up_f1:.3f}",
        border=True,
        help="Baseline: predice «sube» todos los días. Sirve para saber si los modelos aportan algo.",
    )
    box = st.success if v.significant else st.info
    box("\n".join(f"- {line}" for line in v.lines))

    st.markdown("#### Desempeño por ventana")
    c1, c2 = st.columns([3, 1])
    metric = c1.segmented_control(
        "Métrica",
        options=list(METRIC_LABELS),
        default="f1",
        format_func=METRIC_LABELS.get,
        key=f"{key}-metric",
    )
    show_baselines = c2.toggle("Mostrar baselines", value=True, key=f"{key}-baselines")
    st.altair_chart(metric_chart(wm, metric or "f1", show_baselines), width="stretch")
    st.caption(
        "Líneas continuas: políticas; discontinuas: baselines. Donde B y C obtienen el mismo valor, "
        "la línea de C tapa a la de B."
    )

    st.markdown("#### Diferencias de F1 por ventana")
    st.altair_chart(diff_chart(wm), width="stretch")
    st.markdown("#### Contraste estadístico")
    st.dataframe(wilcoxon_table(v.comparisons), hide_index=True, width="stretch")
    p_min = 2 / 2**v.n_windows if v.n_windows else float("nan")
    st.caption(
        "Wilcoxon de rangos con signo pareado sobre el F1 de cada ventana, bilateral. Con "
        f"n = {v.n_windows} ventanas el p mínimo posible es {p_min:.4f}: un resultado no "
        "significativo no prueba que las políticas sean iguales."
    )

    st.markdown("#### Reentrenamientos")
    st.caption(
        f"B reentrenó {v.retrains['B']} veces y C {v.retrains['C']}. Cada versión nueva rige "
        "desde la ventana siguiente, nunca en la que la disparó."
    )
    st.dataframe(retrain_table(mv), hide_index=True, width="stretch")

    drift_b = drift[drift["group"] == "B"]
    if len(drift_b):
        st.markdown("#### Alarmas de deriva del grupo B (KS por feature + Bonferroni)")
        st.altair_chart(drift_chart(drift_b), width="stretch")
        st.caption(
            "Cada celda compara la ventana con los datos de entrenamiento de la versión vigente "
            "de B. Las medias móviles (`ma10_rel`, `ma20_rel`) están autocorrelacionadas y KS supone "
            "independencia, así que pueden disparar alarmas sin un cambio real en los datos."
        )

    with st.expander("Ver métricas por ventana (tabla)"):
        st.dataframe(wm, hide_index=True, width="stretch")


def render_results(tables: dict[str, pd.DataFrame], key: str) -> None:
    wm, mv, drift, comp = (
        tables["window_metrics"],
        tables["model_versions"],
        tables["drift_details"],
        tables["comparisons"],
    )
    verdicts = verdict(wm, comp, mv)
    tabs = st.tabs([replica_label(v.replica) for v in verdicts])
    for tab, v in zip(tabs, verdicts, strict=True):
        with tab:
            r = v.replica
            render_replica(
                v,
                wm[wm["replica"] == r],
                mv[mv["replica"] == r],
                drift[drift["replica"] == r],
                key=f"{key}-{r}",
            )


# ============================================================================== páginas


def page_results() -> None:
    st.title("Estático vs. con alarmas vs. cada seis meses")
    st.markdown(QUESTION)
    cfg = base_config()
    st.caption(
        f"Resultados oficiales del experimento: acciones de Microsoft (MSFT), febrero 2021 – "
        f"febrero 2026, 8 semestres de prueba (2022-H1 a 2025-H2), semilla {cfg.seed}. Generados "
        "por `msft-mlops run` y guardados en `results/`; esta página no reejecuta nada."
    )
    tables = official_results()
    render_results(tables, key="official")

    recent = tables["recent"]
    if len(recent):
        with st.expander("Tramo reciente julio 2025 – enero 2026 (análisis exploratorio)"):
            st.warning(
                "Análisis posterior al diseño y sin contraste estadístico: 128 de sus 148 días son "
                "la ventana 2025-H2 ya mostrada arriba, y los 20 restantes (enero 2026) son el "
                "tramo que la especificación excluye."
            )
            show = recent.rename(
                columns={
                    "replica": "Réplica",
                    "model_type": "Modelo",
                    "training_period": "Entrenamiento",
                    "n_train": "Filas de entrenamiento",
                    "n_test": "Días de prueba",
                    "f1": "F1",
                    "precision": "Precision",
                    "recall": "Recall",
                }
            )
            st.dataframe(show.round(3), hide_index=True, width="stretch")


def _dataset_section(cfg) -> tuple[pd.DataFrame | None, bytes | None, str]:
    st.markdown("### 1 · Datos")
    source = st.radio(
        "Dataset",
        ["Dataset del proyecto (MSFT 2021–2026)", "Subir mi propio CSV"],
        horizontal=True,
        label_visibility="collapsed",
    )
    if source.startswith("Dataset del proyecto"):
        try:
            raw = load_raw(cfg)
        except DataHashMismatch as exc:
            st.error(f"El dataset del proyecto no coincide con su SHA-256: {exc}")
            return None, None, ""
        return raw, project_dataset_bytes(), "proyecto"

    st.caption(
        "CSV con precios diarios: fecha, apertura, máximo, mínimo, cierre y volumen. Se reconocen "
        "nombres habituales (`Date`, `Open`, `High`, `Low`, `Close`, `Volume`, también en español). "
        "Se necesitan al menos ~9 meses iniciales y 2 semestres de prueba completos."
    )
    st.download_button(
        "Descargar CSV de ejemplo (formato esperado)",
        project_dataset_bytes(),
        file_name="MSFT_5years_cleaned.csv",
        mime="text/csv",
    )
    up = st.file_uploader("CSV de precios diarios", type=["csv"])
    if up is None:
        return None, None, ""
    data = up.getvalue()
    try:
        df = pd.read_csv(io.BytesIO(data), sep=None, engine="python")
        raw, warns = normalize_prices(df)
    except (CustomRunError, DataValidationError) as exc:
        st.error(f"No se puede usar este archivo: {exc}")
        return None, None, ""
    except Exception as exc:  # CSV ilegible
        st.error(f"No se pudo leer el CSV: {type(exc).__name__}: {exc}")
        return None, None, ""
    for w in warns[:5]:
        st.caption(f"Aviso de datos: {w}")
    return raw, data, up.name


def _split_section(raw: pd.DataFrame, cfg) -> dict | None:
    try:
        split = infer_split(raw["date"])
        f = cfg["features"]
        ds = build_dataset(raw, f["n_lags"], tuple(f["ma_windows"]), f["vol_ma_window"])
        summary = summarize_split(ds, split, int(cfg["f1_trigger"]["holdout_rows"]))
    except CustomRunError as exc:
        st.error(str(exc))
        return None
    c = st.columns(4)
    c[0].metric("Filas", f"{len(raw):,}".replace(",", "."), border=True)
    c[1].metric(
        "Periodo inicial",
        f"{summary.n_initial} filas",
        help=f"Ajuste {split['fit_start']} → {split['fit_end']} ({summary.n_fit} filas) y "
        f"validación {split['val_start']} → {split['val_end']} ({summary.n_val} filas). El "
        "modelo inicial se entrena con todo el periodo.",
        border=True,
    )
    c[2].metric(
        "Ventanas de prueba",
        len(summary.window_ids),
        help=", ".join(summary.window_ids),
        border=True,
    )
    c[3].metric(
        "Tramo excluido",
        f"{summary.n_excluded_tail} filas",
        help="Días posteriores al último semestre completo: no entran en métricas ni contrastes.",
        border=True,
    )
    st.caption(
        f"Partición inferida con la misma regla que el experimento oficial: prueba de "
        f"{summary.window_ids[0]} a {summary.window_ids[-1]}."
    )
    for w in summary.warnings:
        st.warning(w)
    return split


def _model_section() -> tuple[list[tuple[str, object | None]], dict[str, str], bytes]:
    st.markdown("### 2 · Modelos")
    st.caption(
        "Cada modelo es una réplica: las tres políticas usan el mismo modelo y solo cambia cuándo "
        "se reentrena. Tu modelo se usa como plantilla y se reentrena según cada política."
    )
    c1, c2 = st.columns(2)
    use_lr = c1.checkbox("Regresión logística del proyecto", value=True)
    use_rf = c2.checkbox("Random Forest del proyecto (más lento)", value=False)
    replicas: list[tuple[str, object | None]] = []
    described: dict[str, str] = {}
    model_key = b""
    if use_lr:
        replicas.append(("logreg", None))
        described["logreg"] = "Regresión logística del proyecto (rejilla de C en config)"
    if use_rf:
        replicas.append(("rf", None))
        described["rf"] = "Random Forest del proyecto (rejilla en config)"

    exts = ["skops"] + (["pkl", "joblib"] if unsafe_models_allowed() else [])
    own = st.radio(
        "Tu modelo",
        ["Ninguno", "Subir mi modelo", "Usar el modelo de ejemplo"],
        horizontal=True,
    )
    if own == "Subir mi modelo":
        up = st.file_uploader(
            f"Clasificador de scikit-learn ({', '.join('.' + e for e in exts)})", type=exts
        )
        if up is not None:
            try:
                model = load_model_bytes(up.getvalue(), up.name)
            except CustomRunError as exc:
                st.error(str(exc))
            else:
                replicas.append((CUSTOM_REPLICA, model))
                described[CUSTOM_REPLICA] = describe_model(model)
                model_key = up.getvalue()
                st.success(f"Modelo cargado: `{described[CUSTOM_REPLICA]}`")
    elif own == "Usar el modelo de ejemplo":
        model = example_model()
        replicas.append((EXAMPLE_REPLICA, model))
        described[EXAMPLE_REPLICA] = describe_model(model)
        model_key = b"example"
        st.caption(f"`{described[EXAMPLE_REPLICA]}`")

    with st.expander("¿Cómo preparo mi modelo?"):
        st.markdown(
            "Guarda **sin entrenar** (o entrenado: se reentrena igual) cualquier clasificador de "
            "scikit-learn con [skops](https://skops.readthedocs.io), que se carga sin ejecutar "
            "código. Recibirá las 9 features del proyecto (`ret_0`…`ret_4`, `ma5_rel`, `ma10_rel`, "
            "`ma20_rel`, `vol_rel`) y debe predecir 1 = sube, 0 = no sube."
        )
        st.code(
            "from sklearn.ensemble import GradientBoostingClassifier\n"
            "from sklearn.pipeline import make_pipeline\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "import skops.io as sio\n\n"
            "modelo = make_pipeline(StandardScaler(), GradientBoostingClassifier(max_depth=2))\n"
            'sio.dump(modelo, "mi_modelo.skops")',
            language="python",
        )
        st.download_button(
            "Descargar modelo de ejemplo (.skops)",
            example_model_file(),
            file_name="modelo_ejemplo.skops",
            mime="application/octet-stream",
        )
        if not unsafe_models_allowed():
            st.caption(
                "Los archivos .pkl/.joblib están desactivados porque cargarlos puede ejecutar "
                "código. En tu equipo puedes habilitarlos con `ALLOW_UNSAFE_MODELS=1`."
            )
    return replicas, described, model_key


def _params_section(official: ExperimentParams) -> ExperimentParams:
    with st.expander("3 · Parámetros del experimento (opcional)"):
        st.caption(
            "Valores por defecto = los fijados antes de ejecutar el experimento oficial. Si los "
            "cambias, la ejecución es exploratoria."
        )
        c = st.columns(3)
        alpha = c[0].number_input(
            "α de deriva (KS, antes de Bonferroni)",
            min_value=0.0001,
            max_value=0.5,
            value=official.alpha,
            step=0.01,
            format="%.4f",
        )
        k_sigma = c[1].number_input(
            "Umbral de caída de F1 (k·σ)",
            min_value=0.5,
            max_value=5.0,
            value=official.k_sigma,
            step=0.5,
        )
        window_rows = c[2].number_input(
            "Filas para reentrenar (≈ 252 = 1 año)",
            min_value=126,
            max_value=1008,
            value=official.window_rows,
            step=21,
        )
    return ExperimentParams(float(alpha), float(k_sigma), int(window_rows))


@st.cache_data(show_spinner=False, max_entries=16)
def _cached_run(
    data_label: str,
    data_bytes: bytes,
    replica_names: tuple[str, ...],
    model_key: bytes,
    params: ExperimentParams,
    _raw: pd.DataFrame,
    _replicas: list,
    _described: dict,
) -> tuple[dict[str, pd.DataFrame], dict]:
    cfg_base = base_config()
    split = infer_split(_raw["date"])
    cfg = build_config(cfg_base, split, params, list(replica_names))
    tables = run_custom_experiment(_raw, cfg, _replicas)
    sha = cfg_base.data_sha256 if data_label == "proyecto" else sha256_bytes(data_bytes)
    manifest = build_manifest(
        cfg, sha, data_label, _described, ExperimentParams.from_config(cfg_base)
    )
    return tables, manifest


def page_compare() -> None:
    st.title("Comparar con tus datos y tu modelo")
    st.markdown(QUESTION)
    st.caption(
        "Ejecuta el mismo walk-forward del proyecto (features, ventanas semestrales, alarmas, "
        "métricas y Wilcoxon) sobre el dataset y los modelos que elijas. Son ejecuciones "
        "exploratorias: no sustituyen al experimento oficial."
    )
    cfg = base_config()
    official = ExperimentParams.from_config(cfg)

    raw, data_bytes, data_label = _dataset_section(cfg)
    split = _split_section(raw, cfg) if raw is not None else None
    replicas, described, model_key = _model_section()
    params = _params_section(official)

    ready = split is not None and bool(replicas)
    if raw is not None and not replicas:
        st.warning("Selecciona al menos un modelo.")
    n_rf = sum(1 for name, _ in replicas if name == "rf")
    st.caption(
        f"Tiempo estimado: ~{30 * len(replicas) + 30 * n_rf} s en CPU. Los resultados se guardan "
        "en caché: repetir la misma combinación es instantáneo."
    )
    if st.button("Ejecutar comparación", type="primary", disabled=not ready):
        with st.status("Ejecutando el walk-forward…", expanded=True) as status:
            st.write(
                "Réplicas: "
                + ", ".join(replica_label(n) for n, _ in replicas)
                + ". Para cada una: "
                "selección de hiperparámetros, modelo inicial, 3 políticas × "
                "ventanas, alarmas de deriva (Evidently) y umbral bootstrap de F1."
            )
            try:
                tables, manifest = _cached_run(
                    data_label,
                    data_bytes,
                    tuple(n for n, _ in replicas),
                    model_key,
                    params,
                    raw,
                    replicas,
                    described,
                )
            except CustomRunError as exc:
                status.update(label="La ejecución falló", state="error")
                st.error(str(exc))
                return
            status.update(label="Comparación terminada", state="complete", expanded=False)
        st.session_state["custom_result"] = (tables, manifest)

    if "custom_result" in st.session_state:
        tables, manifest = st.session_state["custom_result"]
        st.divider()
        st.subheader("Resultados")
        tag = (
            "exploratoria"
            if manifest["exploratory"]
            else "con el dataset y los parámetros oficiales"
        )
        st.caption(
            f"Ejecución {tag} · datos: `{manifest['data']['label']}` · SHA-256 "
            f"`{manifest['data']['sha256'][:16]}…` · prueba {manifest['split']['test_start']} → "
            f"{manifest['split']['test_end']} · α = {manifest['params']['alpha']}, "
            f"k·σ = {manifest['params']['k_sigma']}, reentrenamiento = "
            f"{manifest['params']['window_rows']} filas."
        )
        render_results(tables, key="custom")
        st.download_button(
            "Descargar resultados (CSV + manifiesto, .zip)",
            results_zip(tables, manifest),
            file_name="comparacion_politicas_mlops.zip",
            mime="application/zip",
            type="primary",
        )


def page_method() -> None:
    st.title("Metodología")
    st.markdown(
        f"""
{QUESTION}

**Tarea.** Clasificar si el cierre del día siguiente será mayor que el de hoy («sube» = 1). La
clase positiva para Precision, Recall y F1 es «sube».

**Features (9, relativas y sin información futura).** Rendimiento del día y de los 4 anteriores
(`ret_0`…`ret_4`), precio relativo a sus medias móviles de 5, 10 y 20 días (`ma5_rel`, `ma10_rel`,
`ma20_rel`) y volumen relativo a su media de 20 días (`vol_rel`).

**Partición temporal.** Ajuste de hiperparámetros con los primeros meses, validación con los 3
meses siguientes y modelo inicial con todo el periodo inicial. Prueba en semestres calendario
completos (*walk-forward*); lo posterior al último semestre completo se excluye.

**Políticas (lo único que cambia entre grupos).**

- **Estático (A):** se entrena una vez con el periodo inicial y nunca se reentrena.
- **Con alarmas (B):** al cerrar cada ventana se reentrena con las últimas 252 filas si hay
  deriva (KS por feature con Bonferroni, `min p < α/9`) **o** si el F1 cae bajo
  `F1_ref − k·σ` (σ por bootstrap).
- **Cada seis meses (C):** al cerrar cada ventana semestral se reentrena con las últimas 252
  filas, sin mirar alarmas.

La versión nueva rige desde la ventana siguiente, y al reentrenar se descarta el último día de la
ventana (su etiqueta depende del día siguiente).

**Baselines.** «Siempre sube», «persistencia» (repite la dirección de hoy) y «estratificado»
(azar con la proporción de subidas del periodo inicial).

**Comparación.** F1 medio por política, ventanas ganadas y test de Wilcoxon pareado sobre el F1
de cada ventana (B−A, C−A, B−C; α = 0,05).

**Amenazas a la validez.**
- Con 8 ventanas, Wilcoxon tiene poca potencia (p mínimo 0,0078).
- KS supone muestras independientes y las medias móviles están autocorrelacionadas: las alarmas
  de B saltan casi siempre y B termina pareciéndose a C.
- El F1 de la clase «sube» premia predecir siempre 1: por eso «siempre sube» es difícil de batir.
- Un activo, un periodo; las dos réplicas comparten datos.

Código, especificaciones y literatura: [{REPO_URL}]({REPO_URL}).
"""
    )


# ============================================================================== navegación

with st.sidebar:
    st.markdown("### MLOps en series financieras")
    st.caption(
        "Proyecto TAIS: ¿reentrenar un modelo en producción mejora su desempeño frente a dejarlo "
        "estático? Comparación de tres políticas sobre MSFT."
    )
    st.markdown(f"[Repositorio en GitHub]({REPO_URL})")

nav = st.navigation(
    [
        st.Page(page_results, title="Resultados del proyecto", icon="📊", default=True),
        st.Page(page_compare, title="Comparar con tus datos", icon="🧪", url_path="comparar"),
        st.Page(page_method, title="Metodología", icon="📘", url_path="metodologia"),
    ]
)
nav.run()
