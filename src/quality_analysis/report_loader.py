from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from quality_analysis.config import QUALITY_REPORT_JSON_PATH
from quality_analysis.reporting import REQUIRED_REPORT_KEYS


def load_quality_report(path: str | Path = QUALITY_REPORT_JSON_PATH) -> dict[str, Any]:
    """Charge le rapport qualite JSON genere en phase 2."""
    report_path = Path(path)
    if not report_path.exists():
        raise FileNotFoundError(f"Rapport qualite introuvable : {report_path}")

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    if not isinstance(report, dict):
        raise ValueError("Le rapport qualite doit etre un objet JSON.")
    return report


def validate_report_keys(
    report: dict[str, Any],
    required_keys: list[str] | None = None,
) -> dict[str, list[str]]:
    """Retourne les sections presentes et absentes du rapport."""
    expected = required_keys or REQUIRED_REPORT_KEYS
    present = [key for key in expected if key in report]
    missing = [key for key in expected if key not in report]
    return {"present": present, "missing": missing}


def get_report_section(report: dict[str, Any], key: str, default: Any = None) -> Any:
    """Recupere une section sans faire planter l'interface si elle manque."""
    value = report.get(key, default)
    if value is None:
        return default
    return value
