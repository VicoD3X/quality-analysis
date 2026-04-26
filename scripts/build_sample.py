"""Cree un echantillon versionnable depuis le dataset nettoye local."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def main() -> None:
    from quality_analysis.config import CLEAN_DATA_PATH, SAMPLE_DATA_PATH
    from quality_analysis.export import export_csv
    from quality_analysis.loaders import load_clean_dataset

    cleaned = load_clean_dataset(CLEAN_DATA_PATH)
    sample = cleaned.sample(n=min(1200, len(cleaned)), random_state=42).sort_values("code")
    output_path = export_csv(sample, SAMPLE_DATA_PATH)
    print(f"Echantillon exporte : {output_path}")
    print(f"Dimensions : {sample.shape[0]} lignes, {sample.shape[1]} colonnes")


if __name__ == "__main__":
    main()
