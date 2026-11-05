"""Features relativas y etiqueta (FR-004, FR-005, FR-006a).

Toda feature de la fila *t* usa solo ``close`` y ``volume`` hasta *t* (ventanas hacia atrás).
La etiqueta ``y`` de *t* es la dirección del cierre de *t+1* y nunca entra en las features.
"""

from __future__ import annotations

import pandas as pd

DEFAULT_LAGS = 4
DEFAULT_MA = (5, 10, 20)
DEFAULT_VOL_MA = 20


def feature_columns(n_lags: int = DEFAULT_LAGS, ma_windows=DEFAULT_MA) -> list[str]:
    return (
        ["ret_0"]
        + [f"ret_{i}" for i in range(1, n_lags + 1)]
        + [f"ma{w}_rel" for w in ma_windows]
        + ["vol_rel"]
    )


FEATURE_COLUMNS = feature_columns()


def build_dataset(
    df: pd.DataFrame,
    n_lags: int = DEFAULT_LAGS,
    ma_windows=DEFAULT_MA,
    vol_ma_window: int = DEFAULT_VOL_MA,
) -> pd.DataFrame:
    """Devuelve índice ``date``, las K features y ``y``. Sin NaN y sin relleno."""
    d = df.sort_values("date").set_index("date")
    close, volume = d["close"], d["volume"]
    out = pd.DataFrame(index=d.index)
    ret = close.pct_change()
    out["ret_0"] = ret
    for i in range(1, n_lags + 1):
        out[f"ret_{i}"] = ret.shift(i)
    for w in ma_windows:
        out[f"ma{w}_rel"] = close / close.rolling(w).mean() - 1.0
    out["vol_rel"] = volume / volume.rolling(vol_ma_window).mean() - 1.0
    # Etiqueta: único uso de información posterior a t (cierre de t+1).
    nxt = close.shift(-1)
    out["y"] = (nxt > close).astype("float")
    out.loc[nxt.isna(), "y"] = float("nan")
    out = out.dropna()
    out["y"] = out["y"].astype(int)
    return out


def split_xy(ds: pd.DataFrame, columns: list[str] | None = None):
    cols = columns or [c for c in ds.columns if c != "y"]
    return ds[cols], ds["y"]
