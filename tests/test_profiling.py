from __future__ import annotations

import pandas as pd

from quality_analysis.profiling import dataset_profile, duplicate_profile, nutrition_grade_profile


def test_dataset_profile_returns_core_metrics():
    frame = pd.DataFrame(
        {
            "code": ["1", "1", "2"],
            "nutrition_grade_fr": ["a", "b", None],
            "energy_100g": [100.0, None, 300.0],
            "product_name": ["A", "A", "B"],
        }
    )

    result = dataset_profile(frame)

    assert result["row_count"] == 3
    assert result["column_count"] == 4
    assert 0 < result["global_missing_rate"] < 1
    assert result["duplicate_count"] == 1
    assert "energy_100g" in result["numeric_columns"]
    assert "product_name" in result["categorical_columns"]


def test_duplicate_profile_handles_missing_subset():
    frame = pd.DataFrame({"product_name": ["A", "A"]})

    result = duplicate_profile(frame)

    assert result["duplicate_count"] == 0
    assert result["duplicate_rate"] == 0.0


def test_nutrition_grade_profile_counts_missing_values():
    frame = pd.DataFrame({"nutrition_grade_fr": ["a", "a", None]})

    result = nutrition_grade_profile(frame)

    missing = [row for row in result if row["grade"] == "missing"][0]
    assert missing["count"] == 1
