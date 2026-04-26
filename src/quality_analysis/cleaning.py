from __future__ import annotations

import numpy as np
import pandas as pd

from quality_analysis.config import CORE_COLUMNS, GRADE_ORDER, NUTRIENT_BOUNDS


def remove_high_missing_columns(frame: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Supprime les colonnes dont le taux de valeurs manquantes depasse le seuil."""
    missing_rate = frame.isna().mean()
    columns_to_keep = missing_rate[missing_rate <= threshold].index
    return frame.loc[:, columns_to_keep].copy()


def select_core_columns(frame: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Garde les colonnes utiles au cadrage nutritionnel si elles existent."""
    selected = [column for column in (columns or CORE_COLUMNS) if column in frame.columns]
    return frame.loc[:, selected].copy()


def normalize_nutrition_grade(frame: pd.DataFrame, grade_col: str = "nutrition_grade_fr") -> pd.DataFrame:
    """Normalise le Nutri-Grade en lettres minuscules a-e."""
    result = frame.copy()
    if grade_col in result.columns:
        result[grade_col] = result[grade_col].astype("string").str.lower().str.strip()
        result = result[result[grade_col].isin(GRADE_ORDER)].copy()
    return result


def apply_numeric_bounds(
    frame: pd.DataFrame,
    bounds: dict[str, tuple[float, float]] | None = None,
) -> pd.DataFrame:
    """Remplace par NaN les valeurs nutritionnelles hors bornes metier simples."""
    result = frame.copy()
    for column, (lower, upper) in (bounds or NUTRIENT_BOUNDS).items():
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors="coerce")
            result.loc[~result[column].between(lower, upper), column] = np.nan
    return result


def remove_duplicates(frame: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """Supprime les doublons sur les colonnes d'identification disponibles."""
    keys = [column for column in (subset or ["code", "product_name", "brands"]) if column in frame.columns]
    return frame.drop_duplicates(subset=keys or None).copy()


def impute_numeric_median(frame: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Impute les colonnes numeriques par mediane."""
    result = frame.copy()
    numeric_columns = columns or result.select_dtypes(include="number").columns.tolist()
    for column in numeric_columns:
        if column in result.columns:
            median = result[column].median()
            result[column] = result[column].fillna(0 if pd.isna(median) else median)
    return result


def build_clean_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    """Pipeline minimal et reproductible inspire du notebook exploratoire."""
    cleaned = select_core_columns(frame)
    cleaned = normalize_nutrition_grade(cleaned)
    cleaned = apply_numeric_bounds(cleaned)
    cleaned = remove_duplicates(cleaned)
    cleaned = impute_numeric_median(cleaned)
    return cleaned.reset_index(drop=True)
