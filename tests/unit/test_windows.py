import pandas as pd

from msft_mlops.windows import excluded_tail, last_year_training, split_2021
from msft_mlops.windows import test_windows as make_windows


def test_eight_semester_windows(ds, config):
    ws = make_windows(ds, config["split"])
    assert [w.window_id for w in ws] == [f"{y}-H{h}" for y in range(2022, 2026) for h in (1, 2)]
    for w in ws:
        assert 120 <= w.n <= 130


def test_windows_consecutive_no_overlap(ds, config):
    ws = make_windows(ds, config["split"])
    for a, b in zip(ws, ws[1:], strict=False):
        assert a.end < b.start
    assert sum(w.n for w in ws) == len(ds.loc["2022-01-01":"2025-12-31"])


def test_tail_excluded_size(ds, config):
    tail = excluded_tail(ds, config["split"])
    assert tail.index.min() >= pd.Timestamp("2026-01-01")
    assert 18 <= len(tail) <= 24


def test_split_2021_is_temporal(ds, config):
    fit, val, initial = split_2021(ds, config["split"])
    assert fit.index.max() < val.index.min()
    assert initial.index.max() < pd.Timestamp("2022-01-01")
    assert len(initial) == len(fit) + len(val)


def test_last_year_excludes_last_window_row(ds, config):
    w = make_windows(ds, config["split"])[0]
    tr = last_year_training(ds, w, 252)
    assert len(tr) == 252
    assert tr.index.max() < w.end
