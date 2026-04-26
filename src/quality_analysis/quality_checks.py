from __future__ import annotations

import pandas as pd

from quality_analysis.config import CORE_COLUMNS, NUTRIENT_BOUNDS


def missing_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Retourne le volume et le taux de valeurs manquantes par colonne."""
    return (
        pd.DataFrame(
            {
                "column": frame.columns,
                "missing_count": frame.isna().sum().values,
                "missing_rate": frame.isna().mean().values,
            }
        )
        .sort_values("missing_rate", ascending=False)
        .reset_index(drop=True)
    )


def required_columns_report(frame: pd.DataFrame, columns: list[str] | None = None) -> dict[str, list[str]]:
    """Indique les colonnes presentes et absentes pour le pipeline."""
    expected = columns or CORE_COLUMNS
    present = [column for column in expected if column in frame.columns]
    missing = [column for column in expected if column not in frame.columns]
    return {"present": present, "missing": missing}


def duplicate_rate(frame: pd.DataFrame, subset: list[str] | None = None) -> float:
    """Calcule le taux de doublons."""
    keys = [column for column in (subset or ["code"]) if column in frame.columns]
    if not keys or len(frame) == 0:
        return 0.0
    return float(frame.duplicated(subset=keys).mean())


def numeric_bounds_report(
    frame: pd.DataFrame,
    bounds: dict[str, tuple[float, float]] | None = None,
) -> pd.DataFrame:
    """Compte les valeurs hors bornes metier par variable nutritionnelle."""
    rows: list[dict[str, object]] = []
    for column, (lower, upper) in (bounds or NUTRIENT_BOUNDS).items():
        if column not in frame.columns:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        invalid = values.notna() & ~values.between(lower, upper)
        rows.append(
            {
                "column": column,
                "lower_bound": lower,
                "upper_bound": upper,
                "invalid_count": int(invalid.sum()),
                "invalid_rate": float(invalid.mean()) if len(values) else 0.0,
            }
        )
    return pd.DataFrame(rows)
