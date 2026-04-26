from __future__ import annotations

from matplotlib.figure import Figure

from quality_analysis.visualization import (
    plot_missing_columns,
    plot_numeric_bounds,
    plot_nutrition_grade_distribution,
    plot_quality_score_dimensions,
)


def test_plot_nutrition_grade_distribution_returns_figure():
    report = {
        "nutrition_grade_distribution": [
            {"grade": "a", "count": 10, "rate": 0.5},
            {"grade": "b", "count": 10, "rate": 0.5},
        ]
    }

    figure = plot_nutrition_grade_distribution(report)

    assert isinstance(figure, Figure)


def test_plot_missing_columns_returns_figure():
    report = {
        "missing_values": {
            "top_columns": [
                {"column": "product_name", "missing_count": 2, "missing_rate": 0.2},
                {"column": "brands", "missing_count": 1, "missing_rate": 0.1},
            ]
        }
    }

    figure = plot_missing_columns(report)

    assert isinstance(figure, Figure)


def test_plot_numeric_bounds_returns_none_without_invalid_values():
    report = {
        "numeric_bounds": [
            {"column": "sugars_100g", "invalid_count": 0, "invalid_rate": 0.0},
        ]
    }

    figure = plot_numeric_bounds(report)

    assert figure is None


def test_plot_quality_score_dimensions_returns_figure():
    report = {
        "quality_score": {
            "dimensions": {
                "completeness": 98.0,
                "duplicates": 99.0,
            }
        }
    }

    figure = plot_quality_score_dimensions(report)

    assert isinstance(figure, Figure)


def test_visualization_handles_missing_sections():
    report = {}

    assert plot_nutrition_grade_distribution(report) is None
    assert plot_missing_columns(report) is None
    assert plot_numeric_bounds(report) is None
    assert plot_quality_score_dimensions(report) is None
