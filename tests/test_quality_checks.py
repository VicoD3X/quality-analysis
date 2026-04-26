from __future__ import annotations

import pandas as pd

from quality_analysis.quality_checks import (
    duplicate_rate,
    missing_summary,
    numeric_bounds_report,
    required_columns_report,
)


def test_missing_summary_orders_missing_rates():
    frame = pd.DataFrame({"complete": [1, 2], "missing": [None, 2]})

    result = missing_summary(frame)

    assert result.iloc[0]["column"] == "missing"
    assert result.iloc[0]["missing_rate"] == 0.5


def test_required_columns_report_lists_missing_columns():
    frame = pd.DataFrame({"code": ["1"], "product_name": ["A"]})

    result = required_columns_report(frame, ["code", "product_name", "nutrition_grade_fr"])

    assert result["present"] == ["code", "product_name"]
    assert result["missing"] == ["nutrition_grade_fr"]


def test_duplicate_rate_uses_available_key():
    frame = pd.DataFrame({"code": ["1", "1", "2"]})

    assert duplicate_rate(frame) == 1 / 3


def test_numeric_bounds_report_counts_invalid_values():
    frame = pd.DataFrame({"salt_100g": [0.5, -1, 120]})

    result = numeric_bounds_report(frame)

    assert result.loc[result["column"] == "salt_100g", "invalid_count"].iloc[0] == 2
