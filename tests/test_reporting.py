from __future__ import annotations

import json

import pandas as pd

from quality_analysis.reporting import (
    REQUIRED_REPORT_KEYS,
    build_quality_report,
    render_markdown_report,
    write_json_report,
    write_report_files,
)


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "code": ["1", "1", "2"],
            "product_name": ["A", "A", "B"],
            "nutrition_grade_fr": ["a", None, "e"],
            "energy_100g": [100.0, 4500.0, None],
            "fat_100g": [1.0, 2.0, 3.0],
            "sugars_100g": [1.0, 20.0, 40.0],
        }
    )


def test_quality_report_contains_expected_keys():
    report = build_quality_report(sample_frame(), source_path="sample.csv")

    assert set(REQUIRED_REPORT_KEYS) <= set(report)
    assert report["metadata"]["source_path"] == "sample.csv"


def test_markdown_report_generates_without_error():
    report = build_quality_report(sample_frame())

    markdown = render_markdown_report(report)

    assert "# Rapport qualité OpenFoodFacts" in markdown
    assert "Score global" in markdown


def test_json_report_writes_valid_json(tmp_path):
    report = build_quality_report(sample_frame())
    output_path = tmp_path / "quality_report.json"

    write_json_report(report, output_path)

    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["quality_score"]["score"] == report["quality_score"]["score"]


def test_report_files_are_generated(tmp_path):
    report = build_quality_report(sample_frame())

    outputs = write_report_files(
        report,
        json_path=tmp_path / "quality_report.json",
        markdown_path=tmp_path / "quality_report.md",
        html_path=tmp_path / "quality_report.html",
    )

    assert outputs["json"].exists()
    assert outputs["markdown"].exists()
    assert outputs["html"].exists()


def test_report_alerts_detect_basic_quality_issues():
    report = build_quality_report(sample_frame())
    categories = {alert["category"] for alert in report["alerts"]}

    assert "required_columns" in categories
    assert "duplicates" in categories
    assert "numeric_bounds" in categories
