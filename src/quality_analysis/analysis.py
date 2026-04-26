from __future__ import annotations

import pandas as pd
from scipy.stats import f_oneway
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from quality_analysis.config import GRADE_ORDER, NUMERIC_NUTRITION_COLUMNS


def nutrition_grade_distribution(frame: pd.DataFrame, grade_col: str = "nutrition_grade_fr") -> pd.DataFrame:
    """Compte les produits par Nutri-Grade."""
    distribution = frame[grade_col].value_counts(dropna=False).rename_axis(grade_col).reset_index(name="count")
    distribution[grade_col] = pd.Categorical(distribution[grade_col], categories=GRADE_ORDER, ordered=True)
    return distribution.sort_values(grade_col).reset_index(drop=True)


def nutrient_summary_by_grade(
    frame: pd.DataFrame,
    grade_col: str = "nutrition_grade_fr",
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Calcule les moyennes nutritionnelles par Nutri-Grade."""
    numeric_columns = [column for column in (columns or NUMERIC_NUTRITION_COLUMNS) if column in frame.columns]
    return frame.groupby(grade_col, observed=True)[numeric_columns].mean().round(2).reset_index()


def anova_by_grade(
    frame: pd.DataFrame,
    variable: str,
    grade_col: str = "nutrition_grade_fr",
) -> dict[str, float | str]:
    """Calcule une ANOVA simple par Nutri-Grade pour une variable numerique."""
    data = frame[[grade_col, variable]].dropna()
    groups = [group[variable].values for _, group in data.groupby(grade_col, observed=True)]
    if len(groups) < 2:
        raise ValueError("Au moins deux groupes sont necessaires pour calculer une ANOVA.")
    statistic, p_value = f_oneway(*groups)
    return {"variable": variable, "f_statistic": float(statistic), "p_value": float(p_value)}


def pca_explained_variance(frame: pd.DataFrame, columns: list[str], n_components: int = 2) -> list[float]:
    """Retourne la variance expliquee d'une PCA sur des colonnes numeriques."""
    data = frame[columns].dropna()
    if data.empty:
        raise ValueError("Aucune donnee disponible pour la PCA.")
    scaled = StandardScaler().fit_transform(data)
    pca = PCA(n_components=min(n_components, len(columns)))
    pca.fit(scaled)
    return [float(value) for value in pca.explained_variance_ratio_]
