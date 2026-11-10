import dataclasses

import pandas as pd
import pytest

from msft_mlops.data import DataHashMismatch, DataValidationError, load_raw, validate_integrity


def test_real_dataset_loads_and_validates(raw):
    assert len(raw) == 1254
    validate_integrity(raw)
    assert raw["date"].min() == pd.Timestamp("2021-02-04")
    assert raw["date"].max() == pd.Timestamp("2026-02-02")


def test_wrong_hash_raises(config):
    bad = dataclasses.replace(
        config, raw={**config.raw, "data": {**config["data"], "sha256": "0" * 64}}
    )
    with pytest.raises(DataHashMismatch):
        load_raw(bad)


def test_integrity_detects_duplicates(raw):
    dup = pd.concat([raw, raw.iloc[[5]]]).sort_values("date").reset_index(drop=True)
    with pytest.raises(DataValidationError):
        validate_integrity(dup)


def test_integrity_detects_bad_high(raw):
    bad = raw.copy()
    bad.loc[10, "high"] = bad.loc[10, "low"] - 1
    with pytest.raises(DataValidationError):
        validate_integrity(bad)
