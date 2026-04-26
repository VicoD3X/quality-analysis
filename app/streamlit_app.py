from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quality_analysis.config import QUALITY_REPORT_JSON_PATH  # noqa: E402
from quality_analysis.report_loader import (  # noqa: E402
    get_report_section,
    load_quality_report,
    validate_report_keys,
)
from quality_analysis.reporting import format_rate  # noqa: E402
from quality_analysis.visualization import (  # noqa: E402
    plot_missing_columns,
    plot_numeric_bounds,
    plot_nutrition_grade_distribution,
    plot_quality_score_dimensions,
)


MISSING_MESSAGE = "Donnée non disponible dans le rapport actuel."


st.set_page_config(
    page_title="Quality Analysis - OpenFoodFacts Data Quality",
    layout="wide",
)


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --qa-bg: #f7fafc;
            --qa-card: #ffffff;
            --qa-text: #102033;
            --qa-muted: #64748b;
            --qa-accent: #0f766e;
            --qa-border: #dbe5ef;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2.4rem;
            max-width: 1240px;
        }
        h1, h2, h3 {
            letter-spacing: -0.03em;
        }
        div[data-testid="stMetric"] {
            background: var(--qa-card);
            border: 1px solid var(--qa-border);
            border-radius: 18px;
            padding: 16px 18px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
        }
        .qa-note {
            background: #ecfeff;
            border: 1px solid #bae6fd;
            border-radius: 16px;
            padding: 14px 16px;
            color: #164e63;
        }
        .qa-card {
            background: #ffffff;
            border: 1px solid var(--qa-border);
            border-radius: 18px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def as_frame(records: Any) -> pd.DataFrame:
    if isinstance(records, list) and records:
        return pd.DataFrame(records)
    return pd.DataFrame()


def show_missing_data() -> None:
    st.info(MISSING_MESSAGE)


def metric_value(value: Any, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:,.2f}{suffix}".replace(",", " ")
    return f"{value}{suffix}"


def render_plot(figure) -> None:
    if figure is None:
        show_missing_data()
    else:
        st.pyplot(figure, clear_figure=True)


def load_report_or_stop() -> dict[str, Any] | None:
    try:
        return load_quality_report(QUALITY_REPORT_JSON_PATH)
    except FileNotFoundError:
        st.warning("Le rapport qualité n'a pas encore été généré.")
        st.code("python scripts/generate_quality_report.py", language="bash")
        st.stop()
    except ValueError as error:
        st.error(f"Le rapport qualité est invalide : {error}")
        st.stop()
    return None


def render_header(report: dict[str, Any]) -> None:
    metadata = get_report_section(report, "metadata", {})
    st.title("Quality Analysis - OpenFoodFacts Data Quality")
    st.markdown(
        """
        <div class="qa-note">
        Analyse exploratoire de qualité de données nutritionnelles OpenFoodFacts.
        L'interface lit le rapport JSON généré en amont et ne recalcule pas l'audit.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Source : "
        f"{metadata.get('source_path', 'n/a')} | "
        f"Généré : {metadata.get('generated_at', 'n/a')}"
    )


def render_kpis(report: dict[str, Any]) -> None:
    profile = get_report_section(report, "dataset_profile", {})
    quality = get_report_section(report, "quality_score", {})
    missing_values = get_report_section(report, "missing_values", {})

    col1, col2, col3, col4 = st.columns(4)
    missing_rate = missing_values.get("global_missing_rate")
    completeness = format_rate(1 - float(missing_rate)) if missing_rate is not None else "n/a"
    col1.metric("Score qualité", metric_value(quality.get("score"), "/100"))
    col2.metric("Produits analysés", metric_value(profile.get("row_count")))
    col3.metric("Colonnes", metric_value(profile.get("column_count")))
    col4.metric("Complétude globale", completeness)

    col5, col6, col7 = st.columns(3)
    duplicate_rate = profile.get("duplicate_rate")
    duplicate_rate_label = format_rate(float(duplicate_rate)) if duplicate_rate is not None else "n/a"
    col5.metric("Doublons", metric_value(profile.get("duplicate_count")))
    col6.metric("Taux doublons", duplicate_rate_label)
    col7.metric("Alertes", metric_value(len(get_report_section(report, "alerts", []))))


def render_profile(report: dict[str, Any]) -> None:
    st.subheader("Profil du dataset")
    profile = get_report_section(report, "dataset_profile", {})
    if not profile:
        show_missing_data()
        return

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Colonnes numériques**")
        numeric_columns = profile.get("numeric_columns", [])
        if numeric_columns:
            st.write(", ".join(numeric_columns))
        else:
            show_missing_data()
    with col2:
        st.markdown("**Colonnes catégorielles**")
        categorical_columns = profile.get("categorical_columns", [])
        if categorical_columns:
            st.write(", ".join(categorical_columns[:16]))
            if len(categorical_columns) > 16:
                st.caption(f"+ {len(categorical_columns) - 16} colonne(s) supplémentaire(s)")
        else:
            show_missing_data()


def render_missing_values(report: dict[str, Any]) -> None:
    st.subheader("Complétude")
    col1, col2 = st.columns([1, 1])
    with col1:
        render_plot(plot_missing_columns(report))
    with col2:
        missing = get_report_section(report, "missing_values", {})
        data = as_frame(missing.get("top_columns"))
        if data.empty:
            show_missing_data()
        else:
            data = data[["column", "missing_count", "missing_rate"]].head(12).copy()
            data["missing_rate"] = data["missing_rate"].map(lambda value: format_rate(float(value)))
            st.dataframe(data, hide_index=True, use_container_width=True)


def render_required_columns(report: dict[str, Any]) -> None:
    st.subheader("Colonnes attendues")
    required = get_report_section(report, "required_columns", {})
    if not required:
        show_missing_data()
        return

    present = required.get("present", [])
    missing = required.get("missing", [])
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"{len(present)} colonne(s) attendue(s) présente(s)")
        st.write(", ".join(present) if present else MISSING_MESSAGE)
    with col2:
        if missing:
            st.warning(f"{len(missing)} colonne(s) absente(s)")
            st.write(", ".join(missing))
        else:
            st.info("Aucune colonne attendue absente.")


def render_bounds_and_grades(report: dict[str, Any]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Valeurs hors bornes")
        render_plot(plot_numeric_bounds(report))
        bounds = as_frame(get_report_section(report, "numeric_bounds", []))
        if not bounds.empty:
            bounds = bounds[["column", "invalid_count", "invalid_rate"]].copy()
            bounds["invalid_rate"] = bounds["invalid_rate"].map(lambda value: format_rate(float(value)))
            st.dataframe(bounds, hide_index=True, use_container_width=True)
    with col2:
        st.subheader("Distribution Nutri-Grade")
        render_plot(plot_nutrition_grade_distribution(report))
        grades = as_frame(get_report_section(report, "nutrition_grade_distribution", []))
        if not grades.empty:
            grades["rate"] = grades["rate"].map(lambda value: format_rate(float(value)))
            st.dataframe(grades, hide_index=True, use_container_width=True)


def render_nutrients(report: dict[str, Any]) -> None:
    st.subheader("Moyennes nutritionnelles par grade")
    summary = as_frame(get_report_section(report, "nutrient_summary_by_grade", []))
    if summary.empty:
        show_missing_data()
        return
    st.dataframe(summary, hide_index=True, use_container_width=True)


def render_score_and_alerts(report: dict[str, Any]) -> None:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Score par dimension")
        render_plot(plot_quality_score_dimensions(report))
    with col2:
        st.subheader("Alertes qualité")
        alerts = get_report_section(report, "alerts", [])
        if not alerts:
            show_missing_data()
            return
        for alert in alerts:
            level = alert.get("level", "info")
            message = alert.get("message", MISSING_MESSAGE)
            if level == "high":
                st.error(message)
            elif level == "medium":
                st.warning(message)
            else:
                st.info(message)


def render_limitations(report: dict[str, Any]) -> None:
    st.subheader("Limites méthodologiques")
    limitations = get_report_section(report, "limitations", [])
    if not limitations:
        show_missing_data()
        return
    for limitation in limitations:
        st.markdown(f"- {limitation}")


def main() -> None:
    inject_style()
    report = load_report_or_stop()
    if report is None:
        return

    validation = validate_report_keys(report)
    render_header(report)

    if validation["missing"]:
        st.warning(
            "Certaines sections sont absentes du rapport : "
            + ", ".join(validation["missing"])
        )

    render_kpis(report)
    st.divider()
    render_profile(report)
    render_missing_values(report)
    render_required_columns(report)
    render_bounds_and_grades(report)
    render_nutrients(report)
    render_score_and_alerts(report)
    render_limitations(report)


if __name__ == "__main__":
    main()
