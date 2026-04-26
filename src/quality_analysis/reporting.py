from __future__ import annotations

import json
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

from quality_analysis.analysis import nutrient_summary_by_grade
from quality_analysis.config import (
    QUALITY_REPORT_HTML_PATH,
    QUALITY_REPORT_JSON_PATH,
    QUALITY_REPORT_MD_PATH,
)
from quality_analysis.profiling import dataset_profile, duplicate_profile
from quality_analysis.quality_checks import (
    missing_summary,
    numeric_bounds_report,
    required_columns_report,
)
from quality_analysis.scoring import quality_score


REQUIRED_REPORT_KEYS = [
    "metadata",
    "dataset_profile",
    "missing_values",
    "required_columns",
    "duplicate_rate",
    "numeric_bounds",
    "nutrition_grade_distribution",
    "nutrient_summary_by_grade",
    "quality_score",
    "alerts",
    "limitations",
]


def format_rate(value: float) -> str:
    """Formate un taux pour les rapports lisibles."""
    if value == 0:
        return "0.0%"
    if abs(value) < 0.001:
        return "<0.1%"
    return f"{value:.1%}"


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if hasattr(value, "item"):
        return _json_safe(value.item())
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def dataframe_to_records(frame: pd.DataFrame, limit: int | None = None) -> list[dict[str, Any]]:
    """Convertit un DataFrame en liste de dictionnaires serialisable."""
    data = frame.head(limit) if limit else frame
    records = data.where(pd.notna(data), None).to_dict(orient="records")
    return [_json_safe(record) for record in records]


def build_alerts(
    frame: pd.DataFrame,
    required_columns: dict[str, list[str]],
    missing_values: pd.DataFrame,
    bounds: pd.DataFrame,
    duplicates: dict[str, object],
    grade_distribution: list[dict[str, object]],
) -> list[dict[str, str]]:
    """Construit des alertes simples a partir des controles qualite."""
    alerts: list[dict[str, str]] = []

    if required_columns["missing"]:
        alerts.append(
            {
                "level": "high",
                "category": "required_columns",
                "message": (
                    "Colonnes attendues absentes : "
                    + ", ".join(required_columns["missing"])
                ),
            }
        )

    high_missing = missing_values[missing_values["missing_rate"] >= 0.40]
    for row in high_missing.head(8).to_dict(orient="records"):
        alerts.append(
            {
                "level": "medium",
                "category": "missing_values",
                "message": (
                    f"Colonne '{row['column']}' très incomplète "
                    f"({format_rate(row['missing_rate'])} de valeurs manquantes)."
                ),
            }
        )

    invalid_bounds = bounds[bounds["invalid_count"] > 0] if not bounds.empty else bounds
    for row in invalid_bounds.to_dict(orient="records"):
        alerts.append(
            {
                "level": "medium",
                "category": "numeric_bounds",
                "message": (
                    f"Colonne '{row['column']}' : {row['invalid_count']} valeur(s) "
                    "hors bornes nutritionnelles."
                ),
            }
        )

    duplicate_rate_value = float(duplicates.get("duplicate_rate", 0.0))
    if duplicate_rate_value > 0:
        alerts.append(
            {
                "level": "medium",
                "category": "duplicates",
                "message": (
                    f"{duplicates['duplicate_count']} doublon(s) détecté(s) "
                    f"({format_rate(duplicate_rate_value)})."
                ),
            }
        )

    grade_rows = [row for row in grade_distribution if row["grade"] != "missing"]
    grade_total = sum(int(row["count"]) for row in grade_rows)
    missing_grade = next(
        (row for row in grade_distribution if row["grade"] == "missing"),
        None,
    )
    if "nutrition_grade_fr" not in frame.columns or grade_total == 0:
        alerts.append(
            {
                "level": "high",
                "category": "nutrition_grade",
                "message": "Aucun Nutri-Grade exploitable dans le dataset.",
            }
        )
    elif missing_grade:
        alerts.append(
            {
                "level": "medium",
                "category": "nutrition_grade",
                "message": (
                    f"{missing_grade['count']} produit(s) sans Nutri-Grade "
                    "dans l'export analysé."
                ),
            }
        )

    if grade_rows:
        dominant_grade = max(grade_rows, key=lambda row: float(row["rate"]))
        if float(dominant_grade["rate"]) >= 0.70:
            alerts.append(
                {
                    "level": "low",
                    "category": "nutrition_grade",
                    "message": (
                        f"Nutri-Grade '{dominant_grade['grade']}' très dominant "
                        f"({format_rate(float(dominant_grade['rate']))})."
                    ),
                }
            )

    if not alerts:
        alerts.append(
            {
                "level": "info",
                "category": "quality",
                "message": "Aucune alerte majeure sur les contrôles simples.",
            }
        )
    return alerts


def build_quality_report(frame: pd.DataFrame, source_path: str | Path | None = None) -> dict[str, Any]:
    """Genere le rapport qualite structure."""
    profile = dataset_profile(frame)
    missing_values = missing_summary(frame)
    required_columns = required_columns_report(frame)
    duplicates = duplicate_profile(frame)
    bounds = numeric_bounds_report(frame)
    grade_distribution = profile["nutrition_grade_distribution"]

    if "nutrition_grade_fr" in frame.columns:
        nutrient_summary = nutrient_summary_by_grade(frame)
    else:
        nutrient_summary = pd.DataFrame()

    alerts = build_alerts(
        frame=frame,
        required_columns=required_columns,
        missing_values=missing_values,
        bounds=bounds,
        duplicates=duplicates,
        grade_distribution=grade_distribution,
    )

    report = {
        "metadata": {
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "source_path": str(source_path) if source_path else None,
            "report_version": "1.0",
        },
        "dataset_profile": profile,
        "missing_values": {
            "global_missing_rate": profile["global_missing_rate"],
            "top_columns": dataframe_to_records(missing_values, limit=20),
        },
        "required_columns": required_columns,
        "duplicate_rate": duplicates,
        "numeric_bounds": dataframe_to_records(bounds),
        "nutrition_grade_distribution": grade_distribution,
        "nutrient_summary_by_grade": dataframe_to_records(nutrient_summary),
        "quality_score": quality_score(frame),
        "alerts": alerts,
        "limitations": [
            "Le score qualité est heuristique et non réglementaire.",
            "Les bornes nutritionnelles restent des contrôles techniques simples.",
            "Le rapport dépend du fichier local utilisé au moment de la génération.",
            "L'échantillon versionné sert à la démonstration, pas à une conclusion métier.",
        ],
    }
    return _json_safe(report)


def validate_report(report: dict[str, Any]) -> None:
    """Verifie la presence des sections principales du rapport."""
    missing_keys = [key for key in REQUIRED_REPORT_KEYS if key not in report]
    if missing_keys:
        raise ValueError("Sections absentes du rapport : " + ", ".join(missing_keys))


def write_json_report(report: dict[str, Any], path: str | Path = QUALITY_REPORT_JSON_PATH) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    if not rows:
        return "_Donnée non disponible._\n"
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join([header_line, separator, *body]) + "\n"


def render_markdown_report(report: dict[str, Any]) -> str:
    """Rend le rapport en Markdown lisible."""
    validate_report(report)
    metadata = report["metadata"]
    profile = report["dataset_profile"]
    score = report["quality_score"]

    missing_rows = [
        [
            row["column"],
            row["missing_count"],
            format_rate(float(row["missing_rate"])),
        ]
        for row in report["missing_values"]["top_columns"][:10]
    ]
    bound_rows = [
        [
            row["column"],
            row["invalid_count"],
            format_rate(float(row["invalid_rate"])),
        ]
        for row in report["numeric_bounds"]
    ]
    grade_rows = [
        [
            row["grade"],
            row["count"],
            format_rate(float(row["rate"])),
        ]
        for row in report["nutrition_grade_distribution"]
    ]
    dimension_rows = [
        [name, value]
        for name, value in score["dimensions"].items()
    ]

    alerts = "\n".join(
        f"- `{alert['level']}` - {alert['message']}" for alert in report["alerts"]
    )
    limitations = "\n".join(f"- {item}" for item in report["limitations"])

    return "\n".join(
        [
            "# Rapport qualité OpenFoodFacts",
            "",
            "## Metadata",
            "",
            f"- Source : `{metadata['source_path']}`",
            f"- Génération : `{metadata['generated_at']}`",
            f"- Version rapport : `{metadata['report_version']}`",
            "",
            "## Profil dataset",
            "",
            f"- Lignes : `{profile['row_count']}`",
            f"- Colonnes : `{profile['column_count']}`",
            (
                "- Valeurs manquantes globales : "
                f"`{format_rate(float(profile['global_missing_rate']))}`"
            ),
            f"- Doublons : `{profile['duplicate_count']}`",
            f"- Taux de doublons : `{format_rate(float(profile['duplicate_rate']))}`",
            "",
            "## Score qualité",
            "",
            f"Score global : `{score['score']}/100`",
            "",
            _markdown_table(["Dimension", "Score"], dimension_rows),
            "",
            "## Alertes",
            "",
            alerts,
            "",
            "## Valeurs manquantes - top 10",
            "",
            _markdown_table(["Colonne", "Volume", "Taux"], missing_rows),
            "",
            "## Bornes numériques",
            "",
            _markdown_table(["Colonne", "Invalides", "Taux"], bound_rows),
            "",
            "## Distribution Nutri-Grade",
            "",
            _markdown_table(["Grade", "Volume", "Taux"], grade_rows),
            "",
            "## Limites",
            "",
            limitations,
            "",
        ]
    )


def write_markdown_report(
    report: dict[str, Any],
    path: str | Path = QUALITY_REPORT_MD_PATH,
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(report), encoding="utf-8")
    return output_path


def render_html_report(report: dict[str, Any]) -> str:
    """Rend une version HTML statique simple du rapport."""
    validate_report(report)
    profile = report["dataset_profile"]
    score = report["quality_score"]

    def list_items(items: list[str]) -> str:
        return "".join(f"<li>{escape(item)}</li>" for item in items)

    alert_items = "".join(
        (
            f"<li><strong>{escape(alert['level'])}</strong> - "
            f"{escape(alert['message'])}</li>"
        )
        for alert in report["alerts"]
    )
    dimension_items = "".join(
        f"<li>{escape(name)} : {value}/100</li>"
        for name, value in score["dimensions"].items()
    )

    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Rapport qualité OpenFoodFacts</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #172033; }}
    main {{ max-width: 980px; margin: auto; }}
    section {{ border: 1px solid #d9e2ec; border-radius: 14px; padding: 18px; margin: 18px 0; }}
    .score {{ font-size: 42px; font-weight: 800; color: #0f766e; }}
    code {{ background: #eef4f8; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
<main>
  <h1>Rapport qualité OpenFoodFacts</h1>
  <section>
    <h2>Score qualité</h2>
    <div class="score">{score["score"]}/100</div>
    <ul>{dimension_items}</ul>
  </section>
  <section>
    <h2>Profil dataset</h2>
    <p>Lignes : <code>{profile["row_count"]}</code></p>
    <p>Colonnes : <code>{profile["column_count"]}</code></p>
    <p>Valeurs manquantes globales : <code>{format_rate(float(profile["global_missing_rate"]))}</code></p>
    <p>Doublons : <code>{profile["duplicate_count"]}</code></p>
  </section>
  <section>
    <h2>Alertes</h2>
    <ul>{alert_items}</ul>
  </section>
  <section>
    <h2>Limites</h2>
    <ul>{list_items(report["limitations"])}</ul>
  </section>
</main>
</body>
</html>
"""


def write_html_report(report: dict[str, Any], path: str | Path = QUALITY_REPORT_HTML_PATH) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html_report(report), encoding="utf-8")
    return output_path


def write_report_files(
    report: dict[str, Any],
    json_path: str | Path = QUALITY_REPORT_JSON_PATH,
    markdown_path: str | Path = QUALITY_REPORT_MD_PATH,
    html_path: str | Path = QUALITY_REPORT_HTML_PATH,
) -> dict[str, Path]:
    """Exporte les trois formats du rapport qualite."""
    validate_report(report)
    return {
        "json": write_json_report(report, json_path),
        "markdown": write_markdown_report(report, markdown_path),
        "html": write_html_report(report, html_path),
    }
