"""Registro de runs y versiones de modelo (Principio II).

``MlflowTracker`` usa MLflow con backend SQLite local; ``NullTracker`` se usa en tests rápidos.
Las métricas canónicas de la comparación se escriben aparte en ``results/*.csv``.
"""

from __future__ import annotations

import warnings
from typing import Any


class NullTracker:
    def start_replica(self, replica: str, params: dict[str, Any]) -> None:
        pass

    def log_window(self, group: str, window_id: str, metrics: dict, tags: dict) -> None:
        pass

    def register_version(self, group: str, version: int, model: Any, tags: dict) -> None:
        pass

    def end_replica(self) -> None:
        pass


class MlflowTracker(NullTracker):
    def __init__(self, tracking_uri: str = "sqlite:///mlflow.db", experiment: str = "msft-mlops"):
        import mlflow

        warnings.filterwarnings("ignore")
        self.mlflow = mlflow
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment)
        self.replica = ""

    def start_replica(self, replica, params):
        self.replica = replica
        self.mlflow.start_run(run_name=f"replica-{replica}")
        self.mlflow.log_params({k: str(v) for k, v in params.items()})

    def log_window(self, group, window_id, metrics, tags):
        with self.mlflow.start_run(run_name=f"{group}/{window_id}", nested=True):
            self.mlflow.set_tags(
                {
                    "replica": self.replica,
                    "group": group,
                    "window": window_id,
                    **{k: str(v) for k, v in tags.items()},
                }
            )
            clean = {k: float(v) for k, v in metrics.items() if v == v}  # omite NaN
            self.mlflow.log_metrics(clean)

    def register_version(self, group, version, model, tags):
        name = f"msft-{self.replica}-{group}"
        with self.mlflow.start_run(run_name=f"{group}/v{version}", nested=True):
            self.mlflow.set_tags(
                {
                    "replica": self.replica,
                    "group": group,
                    "version": str(version),
                    **{k: str(v) for k, v in tags.items()},
                }
            )
            # Modelos generados por este mismo experimento: se confía en el tipo Tree de sklearn.
            self.mlflow.sklearn.log_model(
                model,
                name="model",
                registered_model_name=name,
                skops_trusted_types=["sklearn.tree._tree.Tree"],
            )

    def end_replica(self):
        self.mlflow.end_run()
