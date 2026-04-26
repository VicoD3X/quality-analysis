from __future__ import annotations

import pandas as pd

from quality_analysis.cleaning import (
    apply_numeric_bounds,
    build_clean_dataset,
    impute_numeric_median,
    normalize_nutrition_grade,
    remove_high_missing_columns,
)


def test_remove_high_missing_columns_drops_columns_above_threshold():
    frame = pd.DataFrame({"keep": [1, 2, None], "drop": [None, None, 3]})

    result = remove_high_missing_columns(frame, threshold=0.5)

    assert result.columns.tolist() == ["keep"]


def test_apply_numeric_bounds_replaces_invalid_values_with_nan():
    frame = pd.DataFrame({"sugars_100g": [5, -1, 101]})

    result = apply_numeric_bounds(frame)

    assert result["sugars_100g"].isna().sum() == 2


def test_impute_numeric_median_fills_missing_values():
    frame = pd.DataFrame({"energy_100g": [100.0, None, 300.0]})

    result = impute_numeric_median(frame)

    assert result["energy_100g"].tolist() == [100.0, 200.0, 300.0]


def test_build_clean_dataset_keeps_valid_nutrition_grades():
    frame = pd.DataFrame(
        {
            "code": ["1", "2", "2"],
            "product_name": ["A", "B", "B"],
            "brands": ["x", "y", "y"],
            "nutrition_grade_fr": ["A", "z", "B"],
            "energy_100g": [100, 200, 300],
            "sugars_100g": [1, 2, 3],
        }
    )

    result = build_clean_dataset(normalize_nutrition_grade(frame))

    assert set(result["nutrition_grade_fr"]) <= {"a", "b", "c", "d", "e"}
    assert len(result) == 2
