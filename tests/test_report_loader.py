from __future__ import annotations

import json

import pytest

from quality_analysis.report_loader import (
    get_report_section,
    load_quality_report,
    validate_report_keys,
)


def test_load_quality_report_reads_json_file(tmp_path):
    report_path = tmp_path / "quality_report.json"
    report_path.write_text(json.dumps({"metadata": {"source_path": "sample.csv"}}), encoding="utf-8")

    report = load_quality_report(report_path)

    assert report["metadata"]["source_path"] == "sample.csv"


def test_load_quality_report_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_quality_report(tmp_path / "missing.json")


def test_validate_report_keys_detects_missing_sections():
    report = {"metadata": {}, "dataset_profile": {}}

    result = validate_report_keys(report, required_keys=["metadata", "alerts"])

    assert result["present"] == ["metadata"]
    assert result["missing"] == ["alerts"]


def test_get_report_section_returns_default_for_missing_key():
    report = {"metadata": {}}

    result = get_report_section(report, "alerts", default=[])

    assert result == []
