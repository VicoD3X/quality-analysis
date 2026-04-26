from __future__ import annotations

from typing import Any

import matplotlib
import pandas as pd
from matplotlib.figure import Figure

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402


ACCENT = "#0f766e"
MUTED = "#64748b"
GRID = "#e2e8f0"


def _empty_if_no_records(records: Any) -> pd.DataFrame:
    if not isinstance(records, list) or not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def _style_axes(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED)
    ax.grid(axis="x", color=GRID, linewidth=0.8, alpha=0.7)


def plot_nutrition_grade_distribution(report: dict[str, Any]) -> Figure | None:
    """Cree un graphique de distribution des Nutri-Grades."""
    data = _empty_if_no_records(report.get("nutrition_grade_distribution"))
    if data.empty or not {"grade", "count"}.issubset(data.columns):
        return None

    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.bar(data["grade"].astype(str).str.upper(), data["count"], color=ACCENT)
    ax.set_title("Distribution des Nutri-Grades", loc="left", fontweight="bold")
    ax.set_xlabel("Nutri-Grade")
    ax.set_ylabel("Nombre de produits")
    _style_axes(ax)
    fig.tight_layout()
    return fig


def plot_missing_columns(report: dict[str, Any], limit: int = 10) -> Figure | None:
    """Cree un graphique des colonnes les plus incompletes."""
    missing = report.get("missing_values", {})
    data = _empty_if_no_records(missing.get("top_columns"))
    if data.empty or not {"column", "missing_rate"}.issubset(data.columns):
        return None

    data = data.sort_values("missing_rate", ascending=True).tail(limit)
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.barh(data["column"], data["missing_rate"] * 100, color="#2563eb")
    ax.set_title("Colonnes les plus manquantes", loc="left", fontweight="bold")
    ax.set_xlabel("Valeurs manquantes (%)")
    ax.set_xlim(0, max(1.0, float(data["missing_rate"].max()) * 110))
    _style_axes(ax)
    fig.tight_layout()
    return fig


def plot_numeric_bounds(report: dict[str, Any]) -> Figure | None:
    """Cree un graphique des valeurs hors bornes par variable."""
    data = _empty_if_no_records(report.get("numeric_bounds"))
    if data.empty or not {"column", "invalid_count"}.issubset(data.columns):
        return None

    data = data[data["invalid_count"] > 0].sort_values("invalid_count", ascending=True)
    if data.empty:
        return None

    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.barh(data["column"], data["invalid_count"], color="#dc2626")
    ax.set_title("Valeurs hors bornes nutritionnelles", loc="left", fontweight="bold")
    ax.set_xlabel("Nombre de valeurs invalides")
    _style_axes(ax)
    fig.tight_layout()
    return fig


def plot_quality_score_dimensions(report: dict[str, Any]) -> Figure | None:
    """Cree un graphique du score qualite par dimension."""
    quality_score = report.get("quality_score", {})
    dimensions = quality_score.get("dimensions")
    if not isinstance(dimensions, dict) or not dimensions:
        return None

    data = pd.DataFrame(
        {
            "dimension": list(dimensions.keys()),
            "score": list(dimensions.values()),
        }
    ).sort_values("score", ascending=True)

    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.barh(data["dimension"], data["score"], color=ACCENT)
    ax.set_title("Score qualité par dimension", loc="left", fontweight="bold")
    ax.set_xlabel("Score / 100")
    ax.set_xlim(0, 100)
    _style_axes(ax)
    fig.tight_layout()
    return fig
