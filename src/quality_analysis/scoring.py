from __future__ import annotations

import pandas as pd

from quality_analysis.config import CORE_COLUMNS, GRADE_ORDER
from quality_analysis.profiling import global_missing_rate
from quality_analysis.quality_checks import duplicate_rate, numeric_bounds_report, required_columns_report


QUALITY_SCORE_WEIGHTS = {
    "completeness": 0.30,
    "required_columns": 0.20,
    "numeric_bounds": 0.20,
    "duplicates": 0.15,
    "nutrition_grades": 0.15,
}


def clamp_score(value: float) -> float:
    """Contraint un score entre 0 et 100."""
    return max(0.0, min(100.0, float(value)))


def completeness_score(frame: pd.DataFrame) -> float:
    """Score de completude globale."""
    return clamp_score((1.0 - global_missing_rate(frame)) * 100.0)


def required_columns_score(frame: pd.DataFrame, columns: list[str] | None = None) -> float:
    """Score de presence des colonnes attendues."""
    expected = columns or CORE_COLUMNS
    if not expected:
        return 100.0
    report = required_columns_report(frame, columns=expected)
    return clamp_score(len(report["present"]) / len(expected) * 100.0)


def numeric_bounds_score(frame: pd.DataFrame) -> float:
    """Score de validite des bornes nutritionnelles."""
    report = numeric_bounds_report(frame)
    if report.empty:
        return 100.0
    invalid_rate = float(report["invalid_rate"].mean())
    return clamp_score((1.0 - invalid_rate) * 100.0)


def duplicate_score(frame: pd.DataFrame) -> float:
    """Score penalise par le taux de doublons."""
    return clamp_score((1.0 - duplicate_rate(frame)) * 100.0)


def nutrition_grade_score(frame: pd.DataFrame, grade_col: str = "nutrition_grade_fr") -> float:
    """Score simple de coherence des Nutri-Grades disponibles."""
    if frame.empty:
        return 100.0
    if grade_col not in frame.columns:
        return 0.0
    grades = frame[grade_col].astype("string").str.lower()
    valid_rate = float(grades.isin(GRADE_ORDER).mean())
    return clamp_score(valid_rate * 100.0)


def quality_score(frame: pd.DataFrame) -> dict[str, object]:
    """Calcule un score qualite heuristique et explicable.

    Ce score sert uniquement au pilotage du nettoyage. Il n'a pas de valeur
    scientifique, reglementaire ou nutritionnelle.
    """
    dimensions = {
        "completeness": completeness_score(frame),
        "required_columns": required_columns_score(frame),
        "numeric_bounds": numeric_bounds_score(frame),
        "duplicates": duplicate_score(frame),
        "nutrition_grades": nutrition_grade_score(frame),
    }
    score = sum(dimensions[name] * weight for name, weight in QUALITY_SCORE_WEIGHTS.items())
    return {
        "score": round(clamp_score(score), 2),
        "dimensions": {name: round(value, 2) for name, value in dimensions.items()},
        "weights": QUALITY_SCORE_WEIGHTS,
        "interpretation": (
            "Score heuristique entre 0 et 100 pour suivre la qualite technique "
            "du dataset. Il ne constitue pas une validation scientifique."
        ),
    }
