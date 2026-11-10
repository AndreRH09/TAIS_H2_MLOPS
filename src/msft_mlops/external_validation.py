"""Validación del CSV contra una fuente externa independiente: Yahoo Finance (FR-002).

El dataset está ajustado por dividendos, así que se compara contra el cierre ajustado
(``auto_adjust=True``). Requiere red y el grupo opcional ``validation`` (``yfinance``).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import Config
from .data import load_raw, sha256_file


def download_yahoo(ticker: str, start: str, end: str, cache: Path) -> pd.DataFrame:
    import yfinance as yf

    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df is None or df.empty:
        raise RuntimeError("Yahoo Finance no devolvió datos")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index().rename(columns=str.lower)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, index=False)
    return df


def compare(local: pd.DataFrame, ext: pd.DataFrame, price_tol: float, vol_tol: float) -> dict:
    l_dates, e_dates = set(local["date"]), set(ext["date"])
    merged = local.merge(ext, on="date", suffixes=("", "_ext"))
    out = {
        "n_local": len(local),
        "n_ext": len(ext),
        "only_local": sorted(l_dates - e_dates),
        "only_ext": sorted(e_dates - l_dates),
        "n_common": len(merged),
    }
    # Yahoo reajusta por dividendos posteriores a la descarga de Kaggle: aparece un factor
    # multiplicativo constante que no altera rendimientos ni features relativas. Se estima
    # (mediana) y se mide la desviación respecto de ese factor.
    factor = float((merged["close"] / merged["close_ext"]).median())
    out["adjustment_factor"] = factor
    for col in ("close", "open", "high", "low"):
        rel = (merged[col] / (merged[f"{col}_ext"] * factor) - 1.0).abs().astype(float)
        out[f"{col}_max_rel"] = float(rel.max())
        out[f"{col}_mean_rel"] = float(rel.mean())
        out[f"{col}_n_over_tol"] = int((rel > price_tol).sum())
    vrel = ((merged["volume"] - merged["volume_ext"]).abs() / merged["volume_ext"]).astype(float)
    out["volume_max_rel"] = float(vrel.max())
    out["volume_mean_rel"] = float(vrel.mean())
    out["volume_n_over_tol"] = int((vrel > vol_tol).sum())
    crel = (merged["close"] / (merged["close_ext"] * factor) - 1.0).abs()
    worst = sorted(zip(merged["date"], crel, strict=True), key=lambda x: -x[1])[:5]
    out["worst_close_dates"] = [(d.date(), float(r)) for d, r in worst]
    vworst = sorted(zip(merged["date"], vrel, strict=True), key=lambda x: -x[1])[:3]
    out["worst_volume_dates"] = [(d.date(), float(r)) for d, r in vworst]
    return out


def write_report(path: Path, res: dict | None, cfg: Config, error: str | None = None) -> None:
    v = cfg["validation"]
    lines = ["# Validación externa del dataset (FR-002)\n"]
    lines.append(f"- Dataset: `{cfg['data']['path']}` (SHA-256 `{cfg.data_sha256}`)")
    lines.append(
        f"- Fuente externa: Yahoo Finance vía `yfinance`, ticker `{v['ticker']}`, precios ajustados"
    )
    lines.append(
        f"- Tolerancias: precio {v['price_rel_tol']:.2%}, volumen {v['volume_rel_tol']:.2%}\n"
    )
    if res is None:
        lines.append("## Resultado\n")
        lines.append(f"**La validación NO se pudo realizar.** Motivo: {error}\n")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    ok = (
        not res["only_local"]
        and not res["only_ext"]
        and all(res[f"{c}_n_over_tol"] == 0 for c in ("close", "open", "high", "low"))
        and res["volume_n_over_tol"] == 0
    )
    lines.append("## Resultado\n")
    lines.append(
        f"**{'Sin discrepancias sobre la tolerancia' if ok else 'Hay discrepancias sobre la tolerancia'}.**\n"
    )
    lines.append(
        f"- Fechas: local {res['n_local']}, externa {res['n_ext']}, comunes {res['n_common']}"
    )
    lines.append(
        f"- Solo en el dataset: {[d.date().isoformat() for d in res['only_local']] or 'ninguna'}"
    )
    lines.append(
        f"- Solo en la fuente externa: {[d.date().isoformat() for d in res['only_ext']] or 'ninguna'}\n"
    )
    lines.append(
        f"- Factor de ajuste constante (dataset / Yahoo, mediana del cierre): **{res['adjustment_factor']:.6f}**. "
        "Yahoo reajusta por los dividendos pagados después de la descarga del dataset; el factor es "
        "multiplicativo y constante, por lo que no altera rendimientos ni features relativas. "
        "Las diferencias de la tabla se miden **después** de aplicarlo.\n"
    )
    lines.append(
        "| Campo | Diferencia relativa máx. | Media | Filas sobre tolerancia |\n|---|---|---|---|"
    )
    for c in ("close", "open", "high", "low", "volume"):
        lines.append(
            f"| {c} | {res[f'{c}_max_rel']:.4%} | {res[f'{c}_mean_rel']:.4%} | {res[f'{c}_n_over_tol']} |"
        )
    lines.append(
        "\nMayores diferencias de cierre: "
        + ", ".join(f"{d} ({r:.3%})" for d, r in res["worst_close_dates"])
    )
    lines.append(
        "\nMayores diferencias de volumen: "
        + ", ".join(f"{d} ({r:.2%})" for d, r in res["worst_volume_dates"])
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_validation(cfg: Config, reports_dir: Path) -> int:
    local = load_raw(cfg)
    v = cfg["validation"]
    cache = cfg.root / "data" / "external" / "msft_yahoo.csv"
    start = local["date"].min().strftime("%Y-%m-%d")
    end = (local["date"].max() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    report_path = reports_dir / "validacion_datos.md"
    try:
        ext = download_yahoo(v["ticker"], start, end, cache)
    except Exception as exc:  # red caída, paquete ausente, etc.: se deja constancia explícita
        write_report(report_path, None, cfg, error=f"{type(exc).__name__}: {exc}")
        print(f"[validate-data] no se pudo validar: {exc}")
        return 4
    print(f"[validate-data] SHA-256 de la copia externa: {sha256_file(cache)}")
    res = compare(local, ext, float(v["price_rel_tol"]), float(v["volume_rel_tol"]))
    write_report(report_path, res, cfg)
    bad = (
        res["only_local"]
        or res["only_ext"]
        or any(res[f"{c}_n_over_tol"] for c in ("close", "open", "high", "low"))
        or res["volume_n_over_tol"]
    )
    print(f"[validate-data] informe en {report_path} ({'con' if bad else 'sin'} discrepancias)")
    return 4 if bad else 0
