from __future__ import annotations

import pandas as pd

from quality_analysis.analysis import (
    anova_by_grade,
    nutrient_summary_by_grade,
    nutrition_grade_distribution,
    pca_explained_variance,
)


def test_nutrition_grade_distribution_counts_grades():
    frame = pd.DataFrame({"nutrition_grade_fr": ["a", "a", "b", "e"]})

    result = nutrition_grade_distribution(frame)

    assert result["count"].sum() == 4


def test_nutrient_summary_by_grade_computes_means():
    frame = pd.DataFrame(
        {
            "nutrition_grade_fr": ["a", "a", "b"],
            "sugars_100g": [1.0, 3.0, 10.0],
        }
    )

    result = nutrient_summary_by_grade(frame, columns=["sugars_100g"])

    assert result.loc[result["nutrition_grade_fr"] == "a", "sugars_100g"].iloc[0] == 2.0


def test_anova_by_grade_returns_statistic():
    frame = pd.DataFrame(
        {
            "nutrition_grade_fr": ["a", "a", "b", "b", "c", "c"],
            "sugars_100g": [1, 2, 8, 9, 15, 16],
        }
    )

    result = anova_by_grade(frame, "sugars_100g")

    assert result["f_statistic"] > 0
    assert 0 <= result["p_value"] <= 1


def test_pca_explained_variance_returns_requested_components():
    frame = pd.DataFrame(
        {
            "energy_100g": [100, 200, 300, 400],
            "fat_100g": [1, 2, 3, 4],
            "sugars_100g": [3, 2, 1, 0],
        }
    )

    result = pca_explained_variance(frame, ["energy_100g", "fat_100g", "sugars_100g"])

    assert len(result) == 2
    assert sum(result) <= 1.01
