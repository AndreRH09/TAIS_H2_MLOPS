"""Comparación entre grupos, resumen en Markdown y figuras (FR-019, FR-019a)."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .config import Config
from .windows import excluded_tail

EXPERIMENTAL = ["A", "B", "C"]
BASELINES = ["siempre_sube", "persistencia", "estratificado"]
COMPARISONS = [("B", "A"), ("C", "A"), ("B", "C")]
REPLICA_NAMES = {"logreg": "Regresión logística", "rf": "Random Forest"}


def compare_groups(wm: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """B−A, C−A y B−C sobre el F1 por ventana, por réplica (Wilcoxon pareado)."""
    rows = []
    for replica, sub in wm.groupby("replica", sort=False):
        piv = sub.pivot(index="window_id", columns="group", values="f1")
        for g1, g2 in COMPARISONS:
            pair = piv[[g1, g2]].dropna()
            diff = (pair[g1] - pair[g2]).to_numpy()
            n = len(diff)
            nonzero = diff[diff != 0]
            if len(nonzero) == 0:
                stat, p = float("nan"), float("nan")
            else:
                res = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
                stat, p = float(res.statistic), float(res.pvalue)
            rows.append(
                {
                    "replica": replica,
                    "comparison": f"{g1}-{g2}",
                    "n_effective": n,
                    "mean_diff_f1": float(diff.mean()) if n else float("nan"),
                    "windows_won": int((diff > 0).sum()),
                    "windows_lost": int((diff < 0).sum()),
                    "windows_tied": int((diff == 0).sum()),
                    "wilcoxon_statistic": stat,
                    "p_value": p,
                    "significant_at_0_05": bool(p < alpha) if not math.isnan(p) else False,
                }
            )
    return pd.DataFrame(rows)


def _fmt(x, nd: int = 3) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/d"
    if isinstance(x, (bool, np.bool_)):
        return "sí" if x else "no"
    if isinstance(x, (float, np.floating)):
        return f"{x:.{nd}f}"
    return str(x)


def _md_table(df: pd.DataFrame, index: bool = False) -> str:
    d = df.reset_index() if index else df
    head = "| " + " | ".join(str(c) for c in d.columns) + " |"
    sep = "|" + "|".join("---" for _ in d.columns) + "|"
    body = ["| " + " | ".join(_fmt(v) for v in row) + " |" for row in d.itertuples(index=False)]
    return "\n".join([head, sep, *body])


def _metric_table(sub: pd.DataFrame, metric: str) -> str:
    piv = sub.pivot(index="window_id", columns="group", values=metric)
    cols = [c for c in EXPERIMENTAL + BASELINES if c in piv.columns]
    piv = piv[cols]
    piv.loc["media"] = piv.mean(skipna=True)
    return _md_table(piv, index=True).replace("| window_id |", "| ventana |")


def write_summary(
    cfg: Config, ds: pd.DataFrame, wm, mv, drift, comp, tail: pd.DataFrame, path: Path
) -> None:
    out: list[str] = []
    out.append("# Resumen comparativo: modelo estático (A) vs. monitoreo (B) vs. periódico (C)\n")
    out.append(
        'Generado automáticamente por `msft-mlops report`. Clase positiva = "sube". Las métricas '
        "se esperan bajas (dirección diaria difícil de predecir); el interés está en las "
        "**diferencias** entre grupos. `n/d` = métrica indefinida (sin positivos reales o predichos), "
        "no un cero.\n"
    )
    out.append(f"- Semilla: `{cfg.seed}`; SHA-256 del dataset: `{cfg.data_sha256}`")
    out.append(
        f"- Ventanas de prueba: {wm['window_id'].nunique()} semestres "
        f"({wm['window_id'].min()} … {wm['window_id'].max()})"
    )
    out.append(
        f"- Tramo excluido (posterior a {cfg['split']['test_end']}): **{len(tail)} registros** "
        f"({tail.index.min().date()} … {tail.index.max().date()}), fuera de métricas, disparadores y "
        "comparaciones.\n"
    )
    for replica in wm["replica"].unique():
        sub = wm[wm["replica"] == replica]
        out.append(f"## Réplica: {REPLICA_NAMES.get(replica, replica)}\n")
        for metric, title in [("f1", "F1"), ("precision", "Precision"), ("recall", "Recall")]:
            out.append(f"### {title} por ventana\n")
            out.append(_metric_table(sub, metric) + "\n")
        out.append("### Diferencias de F1 por ventana\n")
        piv = sub.pivot(index="window_id", columns="group", values="f1")
        diffs = pd.DataFrame({f"{a}−{b}": piv[a] - piv[b] for a, b in COMPARISONS}, index=piv.index)
        out.append(_md_table(diffs, index=True).replace("| window_id |", "| ventana |") + "\n")
        out.append("### Reentrenamientos\n")
        vv = mv[(mv["replica"] == replica) & (mv["version"] > 1)]
        for g in ["B", "C"]:
            vg = vv[vv["group"] == g]
            out.append(f"- **Grupo {g}**: {len(vg)} reentrenamientos")
            for r in vg.itertuples():
                used = r.used_from_window if r.used_from_window else "sin ventana posterior"
                out.append(
                    f"  - tras {r.created_after_window} → versión {r.version} ({r.reason}); "
                    f"rige desde: {used}; F1_ref={r.f1_ref:.3f}, σ={r.sigma:.3f}"
                )
        b_rows = sub[sub["group"] == "B"]
        n_w = len(b_rows)
        out.append(
            f"\nObservación automática: en B se detectó deriva en {int(b_rows['drift_detected'].astype(bool).sum())} "
            f"de {n_w} ventanas y se activó el disparador de caída de F1 en "
            f"{int(b_rows['retrain_reason'].fillna('').str.contains('caida_f1').sum())}. "
            "Si B reentrena casi siempre, su política se aproxima a la de C y la diferencia B−C "
            "tiende a cero.\n"
        )
        out.append(
            "### Deriva de features por ventana (grupo B, vs. referencia de su versión vigente)\n"
        )
        b = sub[sub["group"] == "B"][
            ["window_id", "version", "drift_detected", "drift_min_p", "drift_threshold", "f1"]
        ]
        b = b.assign(version=b["version"].astype(int))
        out.append(b.rename(columns={"window_id": "ventana"}).pipe(_md_table) + "\n")
        out.append("### Contraste estadístico (Wilcoxon pareado sobre F1, α = 0,05)\n")
        out.append(_md_table(comp[comp["replica"] == replica].drop(columns="replica")) + "\n")
    out.append("## Amenazas a la validez\n")
    out.append(
        "- **Un activo y un periodo**: MSFT 2021–2026; no se generaliza a otros activos o regímenes.\n"
        "- **Potencia baja**: con n = 8 ventanas el test de Wilcoxon solo detecta diferencias muy "
        "consistentes (p mínimo bilateral = 0,0078); un resultado no significativo no implica igualdad.\n"
        "- **Bootstrap i.i.d.**: el σ del F1 remuestrea pares (y, ŷ) como independientes y no refleja "
        "la autocorrelación; puede subestimar o sobrestimar el umbral de caída.\n"
        "- **Hold-out corto**: 63 filas para estimar `F1_ref` y σ.\n"
        "- **Dos réplicas, no independientes**: LR y RF usan los mismos datos; no son muestras "
        "independientes del mundo.\n"
        "- **Precios ajustados por dividendos**: la validación externa debe compararse con el cierre "
        "ajustado (ver `reports/validacion_datos.md` si existe).\n"
        "- **F1 indefinido** (sin positivos predichos o reales) no dispara reentrenamiento en B y se "
        "excluye de las comparaciones pareadas.\n"
        "- **Múltiples comparaciones**: se hacen 3 contrastes por réplica sin corrección adicional.\n"
    )
    out.append("## Trazabilidad con la literatura\n")
    out.append(
        "| Parámetro | Valor | Respaldo (`literature-review/decisiones.md`) |\n|---|---|---|\n"
        "| Partición temporal sin barajado | 2021 ajuste/validación; 2022+ prueba | D1: [15], [16], [18], [19] |\n"
        "| Ventanas semestrales | 8 × ≈ 126 registros | D2: [13], [17] (compromiso propio, ver brecha) |\n"
        "| Clasificadores | LR y RF como réplicas | D3: [13], [19], [20], [22], [23] |\n"
        "| Baselines ingenuos | siempre sube, persistencia, estratificado | D4: [18], [22] |\n"
        "| Disparador | deriva KS+Bonferroni **o** `F1 < F1_ref − 2σ` | D5: [6], [9], [12] |\n"
        "| Reentrenamiento | último año (252 filas) | D6: [13] p. 3, [5], [6] |\n"
        '| Métricas | Precision, Recall, F1 (clase "sube") | D7: [17] |\n'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def plot_f1(wm: pd.DataFrame, mv: pd.DataFrame, reports_dir: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for replica in wm["replica"].unique():
        sub = wm[wm["replica"] == replica]
        piv = sub.pivot(index="window_id", columns="group", values="f1")
        fig, ax = plt.subplots(figsize=(9, 4.5))
        styles = {"A": ("tab:blue", "-"), "B": ("tab:red", "-"), "C": ("tab:green", "-")}
        for g in EXPERIMENTAL:
            c, ls = styles[g]
            ax.plot(piv.index, piv[g], marker="o", color=c, linestyle=ls, label=f"Grupo {g}")
        for g in BASELINES:
            ax.plot(piv.index, piv[g], linestyle=":", alpha=0.6, label=g.replace("_", " "))
        for g, color in [("B", "tab:red"), ("C", "tab:green")]:
            rt = mv[(mv["replica"] == replica) & (mv["group"] == g) & (mv["version"] > 1)]
            for w in rt["created_after_window"]:
                if g == "B" and w in piv.index:
                    ax.axvline(w, color=color, alpha=0.15, linewidth=6)
        ax.set_xlabel("Ventana de prueba")
        ax.set_ylabel("F1 (clase sube)")
        ax.set_title(
            f"F1 por ventana: {REPLICA_NAMES.get(replica, replica)} (banda roja = reentrena B)"
        )
        ax.legend(fontsize=8, ncol=2)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(reports_dir / f"f1_por_ventana_{replica}.png", dpi=130)
        plt.close(fig)


def build_reports(cfg: Config, ds: pd.DataFrame, results_dir: Path, reports_dir: Path) -> None:
    wm = pd.read_csv(results_dir / "window_metrics.csv", keep_default_na=True)
    mv = pd.read_csv(results_dir / "model_versions.csv", keep_default_na=False)
    mv["version"] = mv["version"].astype(int)
    for col in ("f1_ref", "sigma"):
        mv[col] = mv[col].astype(float)
    drift = pd.read_csv(results_dir / "drift_details.csv")
    comp = compare_groups(wm)
    comp.to_csv(results_dir / "comparisons.csv", index=False, lineterminator="\n")
    tail = excluded_tail(ds, cfg["split"])
    reports_dir.mkdir(parents=True, exist_ok=True)
    write_summary(cfg, ds, wm, mv, drift, comp, tail, reports_dir / "resumen.md")
    plot_f1(wm, mv, reports_dir)
