"""Comparación A vs. B vs. C con datos y modelos propios (feature 002).

Núcleo de la interfaz web, sin dependencia de Streamlit para poder testearlo:

- ``normalize_prices``: reconoce nombres habituales de columnas y valida la integridad (FR-103).
- ``infer_split``: partición temporal derivada de las fechas con la misma regla que el experimento
  oficial; con el dataset del proyecto reproduce ``config/experiment.toml`` (FR-104).
- ``load_model_bytes``: carga segura de un clasificador ``.skops`` (FR-105). Pickle solo en local
  con ``ALLOW_UNSAFE_MODELS=1``, porque cargarlo ejecuta código arbitrario.
- ``run_custom_experiment``: el mismo walk-forward de la feature 001, con el modelo subido como
  plantilla (FR-106) y parámetros ajustables (FR-107).
- ``verdict``: qué política es más efectiva y con qué evidencia (FR-102).
- ``results_zip``: CSV + manifiesto descargables (FR-108).
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import io
import json
import math
import os
import platform
import zipfile
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path

import pandas as pd

from .config import Config
from .data import validate_integrity
from .features import build_dataset
from .report import compare_groups
from .walk_forward import run_replica
from .windows import split_2021, test_windows

POLICY_NAMES = {"A": "Estático (A)", "B": "Con alarmas (B)", "C": "Cada seis meses (C)"}
POLICIES = ("A", "B", "C")
BASELINE_NAMES = {
    "siempre_sube": "Siempre sube",
    "persistencia": "Persistencia",
    "estratificado": "Estratificado",
}
REPLICA_NAMES = {"logreg": "Regresión logística", "rf": "Random Forest"}
OFFICIAL_REPLICAS = ("logreg", "rf")
CUSTOM_REPLICA = "modelo_propio"
EXAMPLE_REPLICA = "ejemplo_gb"

_COLUMN_ALIASES = {
    "date": ("date", "fecha", "datetime", "timestamp", "day", "dia", "día"),
    "open": ("open", "apertura"),
    "high": ("high", "maximo", "máximo", "max"),
    "low": ("low", "minimo", "mínimo", "min"),
    "close": ("close", "cierre", "adj close", "adj_close", "adjclose", "precio"),
    "volume": ("volume", "volumen", "vol"),
}

# Tipos que un .skops puede contener. Se permiten clases de scikit-learn, numpy y scipy, y solo
# tipos de datos básicos de builtins (nunca funciones como eval, exec u open).
_ALLOWED_ROOTS = ("sklearn.", "numpy.", "scipy.")
_ALLOWED_BUILTINS = {
    "builtins.bool",
    "builtins.bytes",
    "builtins.complex",
    "builtins.dict",
    "builtins.float",
    "builtins.frozenset",
    "builtins.int",
    "builtins.list",
    "builtins.NoneType",
    "builtins.set",
    "builtins.slice",
    "builtins.str",
    "builtins.tuple",
}
_DENIED_FRAGMENTS = (
    "numpy.load",
    "numpy.save",
    "numpy.fromfile",
    "numpy.memmap",
    ".npyio",
    "scipy.io",
)


class CustomRunError(ValueError):
    """Error explicable al usuario de la interfaz (datos o modelo no válidos)."""


# --------------------------------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------------------------------


def normalize_prices(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Devuelve el dataset con las columnas del pipeline y los avisos de integridad.

    Acepta nombres habituales (``Date``, ``Close``, ``Adj Close``, ``Volume``…), sin distinguir
    mayúsculas. Usa ``close`` si existe y ``adj close`` solo si no hay ``close``.
    """
    lower = {str(c).strip().lower(): c for c in df.columns}
    picked: dict[str, str] = {}
    for target, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower:
                picked[target] = lower[alias]
                break
    missing = [c for c in _COLUMN_ALIASES if c not in picked]
    if missing:
        raise CustomRunError(
            f"Faltan columnas: {', '.join(missing)}. Se esperan fecha, apertura, máximo, mínimo, "
            f"cierre y volumen (columnas encontradas: {', '.join(map(str, df.columns))})."
        )
    try:
        dates = pd.to_datetime(df[picked["date"]], errors="coerce")
        if getattr(dates.dt, "tz", None) is not None:
            dates = dates.dt.tz_localize(None)
    except (TypeError, ValueError) as exc:
        raise CustomRunError(f"No se pudo interpretar la columna de fechas: {exc}") from exc
    if dates.isna().any():
        raise CustomRunError(f"{int(dates.isna().sum())} fechas no se pudieron interpretar.")
    out = pd.DataFrame({"date": dates.dt.normalize()})
    for col in ("open", "high", "low", "close", "volume"):
        out[col] = pd.to_numeric(df[picked[col]], errors="coerce").astype(float)
    out = out.sort_values("date").reset_index(drop=True)
    out["price_change"] = out["close"].diff()
    out["price_change_pct"] = out["close"].pct_change() * 100
    warnings = validate_integrity(out)  # lanza DataValidationError con el motivo
    return out, warnings


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _semester_ends(first: pd.Timestamp, last: pd.Timestamp) -> list[pd.Timestamp]:
    ends = []
    for year in range(first.year, last.year + 2):
        ends += [
            pd.Timestamp(year=year, month=6, day=30),
            pd.Timestamp(year=year, month=12, day=31),
        ]
    return ends


def infer_split(
    dates: pd.Series,
    min_initial_months: int = 9,
    val_months: int = 3,
    tail_tolerance_days: int = 3,
) -> dict[str, str]:
    """Partición temporal derivada de las fechas (FR-104).

    - Periodo inicial: desde la primera fecha hasta el primer cierre de semestre (30-jun o 31-dic)
      con al menos ``min_initial_months`` meses de datos. Sus últimos ``val_months`` meses son la
      validación de hiperparámetros; el resto, el ajuste.
    - Prueba: semestres calendario consecutivos tras el periodo inicial, hasta el último semestre
      completo (los datos llegan a ``tail_tolerance_days`` días de su cierre). Lo posterior queda
      excluido, como enero 2026 en el experimento oficial.
    """
    dates = pd.to_datetime(pd.Series(dates))
    first, last = dates.min(), dates.max()
    ends = _semester_ends(first, last)
    min_end = first + pd.DateOffset(months=min_initial_months)
    initial_end = next((e for e in ends if e >= min_end), None)
    complete = [e for e in ends if e <= last + pd.Timedelta(days=tail_tolerance_days)]
    if initial_end is None or not complete or complete[-1] <= initial_end:
        raise CustomRunError(
            f"Los datos ({first.date()} a {last.date()}) no alcanzan para un periodo inicial de "
            f"{min_initial_months} meses y al menos un semestre de prueba completo."
        )
    test_end = complete[-1]
    val_start = initial_end - pd.DateOffset(months=val_months) + pd.Timedelta(days=1)
    fmt = "%Y-%m-%d"
    return {
        "fit_start": first.strftime(fmt),
        "fit_end": (val_start - pd.Timedelta(days=1)).strftime(fmt),
        "val_start": val_start.strftime(fmt),
        "val_end": initial_end.strftime(fmt),
        "test_start": (initial_end + pd.Timedelta(days=1)).strftime(fmt),
        "test_end": test_end.strftime(fmt),
    }


@dataclass(frozen=True)
class SplitSummary:
    split: dict[str, str]
    n_fit: int
    n_val: int
    n_initial: int
    window_ids: list[str]
    window_sizes: list[int]
    n_excluded_tail: int
    warnings: list[str] = field(default_factory=list)


def summarize_split(ds: pd.DataFrame, split: dict[str, str], holdout_rows: int) -> SplitSummary:
    """Comprueba que la partición es utilizable y resume sus tamaños."""
    fit, val, initial = split_2021(ds, split)
    windows = test_windows(ds, split)
    tail = ds.loc[pd.Timestamp(split["test_end"]) + pd.Timedelta(days=1) :]
    if len(fit) == 0 or len(val) == 0:
        raise CustomRunError("El periodo inicial no deja filas para ajuste y validación.")
    if len(initial) <= holdout_rows:
        raise CustomRunError(
            f"El periodo inicial tiene {len(initial)} filas utilizables y el hold-out necesita más "
            f"de {holdout_rows}."
        )
    if len(windows) < 2:
        raise CustomRunError(
            f"Solo hay {len(windows)} semestre(s) de prueba completo(s); se necesitan al menos 2."
        )
    warns = []
    if len(windows) < 6:
        warns.append(
            f"Con {len(windows)} ventanas, el test de Wilcoxon no puede dar p < 0,05 (necesita ≥ 6)."
        )
    return SplitSummary(
        split=split,
        n_fit=len(fit),
        n_val=len(val),
        n_initial=len(initial),
        window_ids=[w.window_id for w in windows],
        window_sizes=[w.n for w in windows],
        n_excluded_tail=len(tail),
        warnings=warns,
    )


# --------------------------------------------------------------------------------------------
# Modelos
# --------------------------------------------------------------------------------------------


def unsafe_models_allowed() -> bool:
    return os.environ.get("ALLOW_UNSAFE_MODELS", "0") == "1"


def _type_allowed(name: str) -> bool:
    if any(fragment in name for fragment in _DENIED_FRAGMENTS):
        return False
    return name in _ALLOWED_BUILTINS or name.startswith(_ALLOWED_ROOTS)


def describe_model(model) -> str:
    """Nombre del estimador y solo los parámetros distintos de los valores por defecto."""
    steps = getattr(model, "steps", None)
    if isinstance(steps, list):  # Pipeline
        return " → ".join(describe_model(step) for _, step in steps)
    params = model.get_params(deep=False)
    try:
        defaults = type(model)().get_params(deep=False)
    except Exception:
        defaults = {}
    changed = [
        f"{k}={describe_model(v) if hasattr(v, 'get_params') else repr(v)}"
        for k, v in sorted(params.items())
        if k not in defaults or repr(defaults[k]) != repr(v)
    ]
    return f"{type(model).__name__}({', '.join(changed)})"


def load_model_bytes(data: bytes, filename: str, allow_unsafe: bool | None = None):
    """Carga un clasificador de scikit-learn subido por el usuario (FR-105).

    ``.skops``: se inspeccionan sus tipos antes de cargar y solo se aceptan clases de scikit-learn,
    numpy, scipy y tipos básicos. ``.pkl``/``.pickle``/``.joblib``: solo si ``allow_unsafe`` (por
    defecto, la variable de entorno ``ALLOW_UNSAFE_MODELS=1``), porque pickle ejecuta código.
    """
    from sklearn.base import clone, is_classifier

    allow_unsafe = unsafe_models_allowed() if allow_unsafe is None else allow_unsafe
    ext = Path(filename).suffix.lower()
    if ext == ".skops":
        import skops.io as sio

        try:
            types = sio.get_untrusted_types(data=data)
        except Exception as exc:
            raise CustomRunError(f"El archivo no es un .skops válido: {exc}") from exc
        denied = sorted(t for t in types if not _type_allowed(t))
        if denied:
            raise CustomRunError(
                "El modelo contiene tipos no permitidos (solo scikit-learn, numpy y scipy): "
                + ", ".join(denied[:6])
            )
        try:
            model = sio.loads(data, trusted=types)
        except Exception as exc:
            raise CustomRunError(f"No se pudo cargar el modelo: {exc}") from exc
    elif ext in (".pkl", ".pickle", ".joblib"):
        if not allow_unsafe:
            raise CustomRunError(
                "Los archivos pickle/joblib pueden ejecutar código al cargarse y están desactivados "
                "aquí. Guarda el modelo con skops (`skops.io.dump(modelo, 'modelo.skops')`) o, en tu "
                "propio equipo, arranca la app con ALLOW_UNSAFE_MODELS=1."
            )
        import joblib

        try:
            model = joblib.load(io.BytesIO(data))
        except Exception as exc:
            raise CustomRunError(f"No se pudo cargar el modelo: {exc}") from exc
    else:
        raise CustomRunError("Formato no soportado: sube un archivo .skops.")
    if not (hasattr(model, "fit") and hasattr(model, "predict")) or not is_classifier(model):
        raise CustomRunError(
            f"{type(model).__name__} no es un clasificador de scikit-learn (necesita fit y "
            "predict, y predecir la clase 'sube' = 1 / 'no sube' = 0)."
        )
    try:
        clone(model)
    except Exception as exc:
        raise CustomRunError(f"El modelo no se puede clonar para reentrenarlo: {exc}") from exc
    return model


def example_model():
    """Clasificador de ejemplo para probar la carga de modelos propios."""
    from sklearn.ensemble import GradientBoostingClassifier

    return GradientBoostingClassifier(n_estimators=100, max_depth=2, learning_rate=0.05)


def example_model_bytes() -> bytes:
    import skops.io as sio

    return sio.dumps(example_model())


# --------------------------------------------------------------------------------------------
# Ejecución
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ExperimentParams:
    alpha: float
    k_sigma: float
    window_rows: int

    @classmethod
    def from_config(cls, cfg: Config) -> ExperimentParams:
        return cls(
            alpha=float(cfg["drift"]["alpha"]),
            k_sigma=float(cfg["f1_trigger"]["k_sigma"]),
            window_rows=int(cfg["retrain"]["window_rows"]),
        )


def build_config(
    base: Config, split: dict[str, str], params: ExperimentParams, replicas: list[str]
) -> Config:
    raw = copy.deepcopy(base.raw)
    raw["split"] = dict(split)
    raw["drift"]["alpha"] = params.alpha
    raw["f1_trigger"]["k_sigma"] = params.k_sigma
    raw["retrain"]["window_rows"] = params.window_rows
    raw["run"]["replicas"] = list(replicas)
    return dataclasses.replace(base, raw=raw)


def run_custom_experiment(
    raw: pd.DataFrame,
    cfg: Config,
    replicas: list[tuple[str, object | None]],
    on_replica=None,
) -> dict[str, pd.DataFrame]:
    """Ejecuta el walk-forward para cada réplica ``(nombre, estimador | None)``.

    ``None`` usa la réplica oficial del mismo nombre (``logreg`` o ``rf``) con su rejilla de
    ``cfg``. ``on_replica(nombre)`` se llama antes de cada réplica (progreso en la interfaz).
    """
    if not replicas:
        raise CustomRunError("Selecciona al menos un modelo.")
    f = cfg["features"]
    ds = build_dataset(raw, f["n_lags"], tuple(f["ma_windows"]), f["vol_ma_window"])
    parts: dict[str, list[pd.DataFrame]] = {}
    for name, estimator in replicas:
        if on_replica is not None:
            on_replica(name)
        try:
            out = run_replica(name, ds, cfg, None, estimator=estimator)
        except CustomRunError:
            raise
        except Exception as exc:
            raise CustomRunError(f"La réplica {name} falló: {type(exc).__name__}: {exc}") from exc
        for key, df in out.items():
            parts.setdefault(key, []).append(df)
    tables = {key: pd.concat(dfs, ignore_index=True) for key, dfs in parts.items()}
    tables["comparisons"] = compare_groups(tables["window_metrics"])
    return tables


# --------------------------------------------------------------------------------------------
# Veredicto
# --------------------------------------------------------------------------------------------


@dataclass
class ReplicaVerdict:
    replica: str
    n_windows: int
    mean_f1: dict[str, float]
    best_policy: str | None
    significant: list[str]
    comparisons: pd.DataFrame
    retrains: dict[str, int]
    b_retrain_windows: int
    baseline_up_f1: float
    lines: list[str]


def _f(x: float) -> str:
    return "n/d" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.3f}"


def verdict(wm: pd.DataFrame, comp: pd.DataFrame, mv: pd.DataFrame) -> list[ReplicaVerdict]:
    """Qué política es más efectiva en cada réplica y con qué evidencia (FR-102)."""
    out: list[ReplicaVerdict] = []
    for replica in wm["replica"].unique():
        sub = wm[wm["replica"] == replica]
        n_windows = int(sub["window_id"].nunique())
        means = sub.groupby("group")["f1"].mean()
        mean_f1 = {g: float(means.get(g, float("nan"))) for g in POLICIES}
        valid = {g: v for g, v in mean_f1.items() if not math.isnan(v)}
        best = max(valid, key=valid.get) if valid else None
        c = comp[comp["replica"] == replica].reset_index(drop=True)
        sig = [r.comparison for r in c.itertuples() if bool(r.significant_at_0_05)]
        mvr = mv[(mv["replica"] == replica) & (mv["version"].astype(int) > 1)]
        retrains = {g: int((mvr["group"] == g).sum()) for g in ("B", "C")}
        b_rows = sub[sub["group"] == "B"]
        b_windows = int(b_rows["retrain_triggered"].astype(str).str.lower().eq("true").sum())
        up = float(means.get("siempre_sube", float("nan")))

        lines = []
        if best is not None:
            ranking = sorted(valid, key=valid.get, reverse=True)
            lines.append(
                "F1 medio por política: "
                + " · ".join(f"{POLICY_NAMES[g]} = {_f(valid[g])}" for g in ranking)
                + "."
            )
        if sig:
            details = []
            for r in c.itertuples():
                if r.comparison in sig:
                    g1, g2 = r.comparison.split("-")
                    winner, loser = (g1, g2) if r.mean_diff_f1 > 0 else (g2, g1)
                    details.append(
                        f"{POLICY_NAMES[winner]} supera a {POLICY_NAMES[loser]} "
                        f"(diferencia media {abs(r.mean_diff_f1):.3f}, p = {r.p_value:.4f})"
                    )
            lines.append(
                "Diferencias significativas (Wilcoxon, α = 0,05): " + "; ".join(details) + "."
            )
        else:
            lines.append(
                "Ninguna diferencia entre políticas es estadísticamente significativa (Wilcoxon "
                f"pareado, α = 0,05, n = {n_windows} ventanas)"
                + (
                    f"; descriptivamente, la de mayor F1 medio es {POLICY_NAMES[best]}."
                    if best
                    else "."
                )
            )
        if n_windows < 6:
            lines.append(f"Con {n_windows} ventanas, Wilcoxon no puede dar p < 0,05.")
        if n_windows and b_windows >= 0.75 * n_windows:
            lines.append(
                f"B reentrenó en {b_windows} de {n_windows} ventanas: con estas alarmas se comporta "
                "casi como C, así que el diseño no separa el efecto de monitorear del de reentrenar."
            )
        else:
            lines.append(
                f"B reentrenó en {b_windows} de {n_windows} ventanas; C, en todas "
                f"({retrains['C']} reentrenamientos)."
            )
        if best is not None and not math.isnan(up):
            if up > valid[best]:
                lines.append(
                    f"El baseline «siempre sube» (F1 medio {_f(up)}) supera a la mejor política: con "
                    "F1 de la clase «sube», ningún modelo supera el sesgo alcista del activo."
                )
            else:
                lines.append(
                    f"La mejor política supera al baseline «siempre sube» (F1 medio {_f(up)})."
                )
        out.append(
            ReplicaVerdict(
                replica=replica,
                n_windows=n_windows,
                mean_f1=mean_f1,
                best_policy=best,
                significant=sig,
                comparisons=c,
                retrains=retrains,
                b_retrain_windows=b_windows,
                baseline_up_f1=up,
                lines=lines,
            )
        )
    return out


# --------------------------------------------------------------------------------------------
# Descarga
# --------------------------------------------------------------------------------------------

_LIBS = ("scikit-learn", "pandas", "numpy", "scipy", "evidently", "skops")


def build_manifest(
    cfg: Config,
    data_sha256: str,
    data_label: str,
    models: dict[str, str],
    official_params: ExperimentParams,
) -> dict:
    params = ExperimentParams.from_config(cfg)
    libs = {}
    for lib in _LIBS:
        try:
            libs[lib] = metadata.version(lib)
        except metadata.PackageNotFoundError:
            libs[lib] = None
    return {
        "exploratory": params != official_params or data_label != "proyecto",
        "seed": cfg.seed,
        "data": {"label": data_label, "sha256": data_sha256},
        "split": cfg["split"],
        "params": dataclasses.asdict(params),
        "f1_trigger": {k: cfg["f1_trigger"][k] for k in ("holdout_rows", "n_bootstrap")},
        "models": models,
        "python": platform.python_version(),
        "libraries": libs,
    }


def results_zip(tables: dict[str, pd.DataFrame], manifest: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, df in tables.items():
            zf.writestr(f"{name}.csv", df.to_csv(index=False, lineterminator="\n"))
        zf.writestr(
            "manifest.json", json.dumps(manifest, indent=2, sort_keys=True, default=str) + "\n"
        )
    return buf.getvalue()


def as_bool(series: pd.Series) -> pd.Series:
    """Columnas booleanas leídas de CSV (``True``/``False``/vacío) como bool."""
    return series.astype(str).str.lower().eq("true")


__all__ = [
    "CustomRunError",
    "ExperimentParams",
    "ReplicaVerdict",
    "SplitSummary",
    "build_config",
    "as_bool",
    "build_manifest",
    "describe_model",
    "example_model",
    "example_model_bytes",
    "infer_split",
    "load_model_bytes",
    "normalize_prices",
    "results_zip",
    "run_custom_experiment",
    "sha256_bytes",
    "summarize_split",
    "unsafe_models_allowed",
    "verdict",
]
