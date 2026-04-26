from __future__ import annotations

import pandas as pd

from quality_analysis.scoring import quality_score


def test_quality_score_stays_between_zero_and_one_hundred():
    frame = pd.DataFrame(
        {
            "code": ["1", "1", "2"],
            "nutrition_grade_fr": ["a", "z", None],
            "energy_100g": [100.0, -10.0, 4500.0],
            "fat_100g": [1.0, 2.0, None],
        }
    )

    result = quality_score(frame)

    assert 0 <= result["score"] <= 100
    assert set(result["dimensions"]) == {
        "completeness",
        "required_columns",
        "numeric_bounds",
        "duplicates",
        "nutrition_grades",
    }


def test_quality_score_rewards_clean_small_dataset():
    frame = pd.DataFrame(
        {
            "code": ["1", "2"],
            "product_name": ["A", "B"],
            "brands": ["x", "y"],
            "countries_fr": ["France", "France"],
            "ingredients_text": ["eau", "sucre"],
            "additives_n": [0, 1],
            "nutrition_grade_fr": ["a", "b"],
            "energy_100g": [100, 200],
            "fat_100g": [1, 2],
            "saturated-fat_100g": [0.5, 1],
            "carbohydrates_100g": [10, 20],
            "sugars_100g": [1, 5],
            "fiber_100g": [2, 3],
            "proteins_100g": [4, 5],
            "salt_100g": [0.1, 0.2],
            "sodium_100g": [0.04, 0.08],
            "nutrition-score-fr_100g": [-1, 5],
        }
    )

    result = quality_score(frame)

    assert result["score"] > 95
