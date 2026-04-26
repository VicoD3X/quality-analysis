"""Reconstruit un dataset nettoye OpenFoodFacts a partir du brut local."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def main() -> None:
    from quality_analysis.cleaning import build_clean_dataset
    from quality_analysis.config import CLEAN_DATA_PATH, CORE_COLUMNS
    from quality_analysis.export import export_csv
    from quality_analysis.loaders import load_raw_dataset

    print("Chargement du dataset brut OpenFoodFacts...")
    raw = load_raw_dataset(usecols=lambda column: column in CORE_COLUMNS)
    print(f"Dataset brut charge : {raw.shape[0]:,} lignes, {raw.shape[1]} colonnes".replace(",", " "))

    print("Nettoyage et application des regles qualite...")
    cleaned = build_clean_dataset(raw)
    output_path = export_csv(cleaned, CLEAN_DATA_PATH)
    print(f"Dataset nettoye exporte : {output_path}")
    print(f"Dimensions finales : {cleaned.shape[0]:,} lignes, {cleaned.shape[1]} colonnes".replace(",", " "))


if __name__ == "__main__":
    main()
