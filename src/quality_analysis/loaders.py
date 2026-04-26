from __future__ import annotations

from pathlib import Path

import pandas as pd

from quality_analysis.config import (
    CLEAN_DATA_PATH,
    EXPECTED_RAW_SEPARATOR,
    RAW_DATA_PATH,
    SAMPLE_DATA_PATH,
)


def load_raw_dataset(
    path: str | Path = RAW_DATA_PATH,
    usecols: list[str] | None = None,
    nrows: int | None = None,
) -> pd.DataFrame:
    """Charge le fichier brut OpenFoodFacts local."""
    return pd.read_csv(
        path,
        sep=EXPECTED_RAW_SEPARATOR,
        encoding="utf-8",
        on_bad_lines="skip",
        engine="python",
        usecols=usecols,
        nrows=nrows,
    )


def load_clean_dataset(
    path: str | Path = CLEAN_DATA_PATH,
    nrows: int | None = None,
) -> pd.DataFrame:
    """Charge l'export nettoye local s'il est disponible."""
    return pd.read_csv(path, nrows=nrows, low_memory=False)


def load_sample_dataset(path: str | Path = SAMPLE_DATA_PATH) -> pd.DataFrame:
    """Charge l'echantillon versionne pour les tests et demos legeres."""
    return pd.read_csv(path, low_memory=False)


def list_available_columns(path: str | Path = RAW_DATA_PATH, separator: str = EXPECTED_RAW_SEPARATOR) -> list[str]:
    """Retourne les colonnes disponibles sans charger tout le dataset."""
    with Path(path).open("r", encoding="utf-8", errors="replace") as file:
        return file.readline().rstrip("\n").split(separator)
