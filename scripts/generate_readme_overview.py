from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from quality_analysis.config import (  # noqa: E402
    CLEAN_DATA_PATH,
    CORE_COLUMNS,
    GRADE_ORDER,
    RAW_DATA_PATH,
    SAMPLE_DATA_PATH,
)
from quality_analysis.loaders import load_raw_dataset  # noqa: E402


OUTPUT_PATH = PROJECT_ROOT / "docs" / "screenshots" / "quality-overview.png"


def load_clean_or_sample() -> pd.DataFrame:
    if CLEAN_DATA_PATH.exists():
        return pd.read_csv(CLEAN_DATA_PATH, low_memory=False)
    return pd.read_csv(SAMPLE_DATA_PATH, low_memory=False)


def load_raw_for_missing_profile() -> pd.DataFrame | None:
    if not RAW_DATA_PATH.exists():
        return None
    return load_raw_dataset(RAW_DATA_PATH, usecols=CORE_COLUMNS)


def plot_grade_distribution(ax, clean_frame: pd.DataFrame) -> None:
    grade_counts = (
        clean_frame["nutrition_grade_fr"]
        .astype("string")
        .str.lower()
        .value_counts()
        .reindex(GRADE_ORDER, fill_value=0)
    )
    ax.bar(grade_counts.index.str.upper(), grade_counts.values, color="#0f766e")
    ax.set_title("Distribution Nutri-Grade", loc="left", fontweight="bold")
    ax.set_xlabel("Grade")
    ax.set_ylabel("Produits")
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def plot_missing_comparison(ax, clean_frame: pd.DataFrame, raw_frame: pd.DataFrame | None) -> None:
    clean_missing = clean_frame.isna().mean() * 100
    if raw_frame is None:
        raw_missing = clean_missing.copy()
        title_suffix = "echantillon"
    else:
        raw_missing = raw_frame.isna().mean() * 100
        title_suffix = "brut vs nettoye"

    columns = raw_missing.reindex(CORE_COLUMNS).sort_values(ascending=False).head(8).index.tolist()
    raw_values = raw_missing.reindex(columns).fillna(0)
    clean_values = clean_missing.reindex(columns).fillna(0)

    y_positions = range(len(columns))
    offset = 0.18
    ax.barh(
        [position + offset for position in y_positions],
        raw_values,
        height=0.34,
        color="#f59e0b",
        label="Brut",
    )
    ax.barh(
        [position - offset for position in y_positions],
        clean_values,
        height=0.34,
        color="#0f766e",
        label="Nettoye",
    )

    # Les valeurs nettoyees a 0% sont affichees par un marqueur, sinon la barre disparait.
    for position, value in zip(y_positions, clean_values, strict=True):
        ax.scatter(max(float(value), 0.05), position - offset, color="#0f766e", s=32, zorder=3)
        label_x = max(float(value), 0.05) + 1.2
        ax.text(label_x, position - offset, f"{value:.1f}%", va="center", fontsize=8, color="#0f766e")

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(columns)
    ax.invert_yaxis()
    ax.set_title(f"Valeurs manquantes - {title_suffix}", loc="left", fontweight="bold")
    ax.set_xlabel("Taux de valeurs manquantes (%)")
    ax.set_xlim(0, max(10.0, float(raw_values.max()) * 1.25))
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color="#e2e8f0", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def plot_nutrient_summary(ax, clean_frame: pd.DataFrame) -> None:
    nutrient_columns = ["sugars_100g", "fat_100g", "salt_100g"]
    available = [column for column in nutrient_columns if column in clean_frame.columns]
    summary = (
        clean_frame.groupby("nutrition_grade_fr", observed=True)[available]
        .mean()
        .reindex(GRADE_ORDER)
        .round(2)
    )
    summary.plot(ax=ax, marker="o", linewidth=2)
    ax.set_title("Moyennes nutritionnelles par grade", loc="left", fontweight="bold")
    ax.set_xlabel("Nutri-Grade")
    ax.set_ylabel("Valeur moyenne pour 100 g")
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)


def main() -> None:
    clean_frame = load_clean_or_sample()
    raw_frame = load_raw_for_missing_profile()

    plt.style.use("default")
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.8), gridspec_kw={"width_ratios": [1.0, 1.35, 1.15]})
    fig.patch.set_facecolor("white")

    plot_grade_distribution(axes[0], clean_frame)
    plot_missing_comparison(axes[1], clean_frame, raw_frame)
    plot_nutrient_summary(axes[2], clean_frame)

    fig.suptitle(
        "Quality Analysis - synthese OpenFoodFacts",
        x=0.02,
        y=1.02,
        ha="left",
        fontsize=16,
        fontweight="bold",
    )
    fig.tight_layout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches="tight")
    print(f"Visuel README genere : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
