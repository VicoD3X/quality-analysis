from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_csv(frame: pd.DataFrame, path: str | Path) -> Path:
    """Exporte un DataFrame en CSV en creant le dossier cible."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return output_path
