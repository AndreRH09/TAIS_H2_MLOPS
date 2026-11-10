"""Línea de comandos: ``msft-mlops run | validate-data | report | eval-recent``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from .config import load_config
from .data import DataHashMismatch, DataValidationError, load_raw, validate_integrity
from .features import build_dataset
from .results_io import write_results
from .tracking import MlflowTracker, NullTracker
from .walk_forward import run_replica


def run_experiment(
    config_path: str | Path = "config/experiment.toml",
    results_dir: str | Path = "results",
    tracker=None,
    reports_dir: str | Path | None = "reports",
) -> dict:
    cfg = load_config(config_path)
    raw = load_raw(cfg)
    warnings = validate_integrity(raw)
    for msg in warnings:
        print(f"[aviso datos] {msg}")
    f = cfg["features"]
    ds = build_dataset(raw, f["n_lags"], tuple(f["ma_windows"]), f["vol_ma_window"])
    tracker = tracker if tracker is not None else NullTracker()
    parts: dict[str, list[pd.DataFrame]] = {}
    for replica in cfg.replicas:
        print(f"[run] réplica {replica} ...")
        out = run_replica(replica, ds, cfg, tracker)
        for name, df in out.items():
            parts.setdefault(name, []).append(df)
    tables = {name: pd.concat(dfs, ignore_index=True) for name, dfs in parts.items()}
    results_dir = Path(results_dir)
    manifest = write_results(tables, results_dir, cfg.seed, cfg.data_sha256)
    if reports_dir is not None:
        from .report import build_reports

        build_reports(cfg, ds, results_dir, Path(reports_dir))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="msft-mlops")
    parser.add_argument("--config", default="config/experiment.toml")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--reports-dir", default="reports")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run", help="Ejecuta el experimento completo")
    sub.add_parser("validate-data", help="Valida el CSV contra Yahoo Finance (requiere red)")
    sub.add_parser("report", help="Regenera reports/ desde results/")
    sub.add_parser("eval-recent", help="Evalúa el tramo reciente (julio 2025 - enero 2026)")
    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            run_experiment(args.config, args.results_dir, MlflowTracker(), args.reports_dir)
            print(f"[run] listo: {args.results_dir}/ y {args.reports_dir}/")
        elif args.command == "eval-recent":
            from .recent_evaluation import run_recent_evaluation

            run_recent_evaluation(args.config, args.results_dir, args.reports_dir)
            print(f"[eval-recent] listo: {args.results_dir}/ y {args.reports_dir}/")
        elif args.command == "report":
            from .report import build_reports

            cfg = load_config(args.config)
            raw = load_raw(cfg)
            f = cfg["features"]
            ds = build_dataset(raw, f["n_lags"], tuple(f["ma_windows"]), f["vol_ma_window"])
            build_reports(cfg, ds, Path(args.results_dir), Path(args.reports_dir))
        elif args.command == "validate-data":
            from .external_validation import run_validation

            return run_validation(load_config(args.config), Path(args.reports_dir))
    except DataHashMismatch as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except DataValidationError as exc:
        print(f"ERROR de validación de datos: {exc}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
