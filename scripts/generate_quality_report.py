from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from quality_analysis.config import CLEAN_DATA_PATH, SAMPLE_DATA_PATH  # noqa: E402
from quality_analysis.loaders import load_clean_dataset, load_sample_dataset  # noqa: E402
from quality_analysis.reporting import build_quality_report, write_report_files  # noqa: E402


def load_report_source():
    """Charge le dataset nettoye local, sinon l'echantillon versionne."""
    if CLEAN_DATA_PATH.exists():
        return load_clean_dataset(CLEAN_DATA_PATH), CLEAN_DATA_PATH
    return load_sample_dataset(SAMPLE_DATA_PATH), SAMPLE_DATA_PATH


def main() -> None:
    frame, source_path = load_report_source()
    source_label = source_path.relative_to(PROJECT_ROOT).as_posix()
    report = build_quality_report(frame, source_path=source_label)
    outputs = write_report_files(report)

    print(f"Source analysee : {source_label}")
    print(f"Score qualite : {report['quality_score']['score']}/100")
    print(f"Alertes : {len(report['alerts'])}")
    for label, path in outputs.items():
        print(f"Rapport {label} : {path}")


if __name__ == "__main__":
    main()
