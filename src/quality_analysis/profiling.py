from __future__ import annotations

import pandas as pd

from quality_analysis.config import GRADE_ORDER


def global_missing_rate(frame: pd.DataFrame) -> float:
    """Calcule le taux global de valeurs manquantes du dataset."""
    if frame.empty or len(frame.columns) == 0:
        return 0.0
    return float(frame.isna().mean().mean())


def column_type_profile(frame: pd.DataFrame) -> dict[str, list[str]]:
    """Separe les colonnes numeriques et categorielles."""
    numeric_columns = frame.select_dtypes(include="number").columns.tolist()
    categorical_columns = [column for column in frame.columns if column not in numeric_columns]
    return {
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
    }


def duplicate_profile(frame: pd.DataFrame, subset: list[str] | None = None) -> dict[str, float | int | list[str]]:
    """Retourne le volume et le taux de doublons."""
    keys = [column for column in (subset or ["code"]) if column in frame.columns]
    if frame.empty or not keys:
        return {"subset": keys, "duplicate_count": 0, "duplicate_rate": 0.0}

    duplicates = frame.duplicated(subset=keys)
    return {
        "subset": keys,
        "duplicate_count": int(duplicates.sum()),
        "duplicate_rate": float(duplicates.mean()),
    }


def nutrition_grade_profile(frame: pd.DataFrame, grade_col: str = "nutrition_grade_fr") -> list[dict[str, object]]:
    """Calcule la distribution des Nutri-Grades si la colonne est disponible."""
    if grade_col not in frame.columns or frame.empty:
        return []

    grades = frame[grade_col].astype("string").str.lower()
    total = len(frame)
    rows: list[dict[str, object]] = []
    for grade in GRADE_ORDER:
        count = int((grades == grade).sum())
        rows.append(
            {
                "grade": grade,
                "count": count,
                "rate": float(count / total) if total else 0.0,
            }
        )

    missing_count = int(frame[grade_col].isna().sum())
    if missing_count:
        rows.append(
            {
                "grade": "missing",
                "count": missing_count,
                "rate": float(missing_count / total) if total else 0.0,
            }
        )
    return rows


def dataset_profile(frame: pd.DataFrame, grade_col: str = "nutrition_grade_fr") -> dict[str, object]:
    """Construit un profil general du dataset."""
    column_types = column_type_profile(frame)
    duplicates = duplicate_profile(frame)
    return {
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "global_missing_rate": global_missing_rate(frame),
        "duplicate_count": duplicates["duplicate_count"],
        "duplicate_rate": duplicates["duplicate_rate"],
        "numeric_columns": column_types["numeric_columns"],
        "categorical_columns": column_types["categorical_columns"],
        "nutrition_grade_distribution": nutrition_grade_profile(frame, grade_col=grade_col),
    }
