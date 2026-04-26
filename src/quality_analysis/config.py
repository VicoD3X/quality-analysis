from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "openfoodfacts-products.tsv"
CLEAN_DATA_PATH = DATA_DIR / "processed" / "openfoodfacts-cleaned.csv"
SAMPLE_DATA_PATH = DATA_DIR / "sample" / "openfoodfacts-cleaned-sample.csv"

EXPECTED_RAW_SEPARATOR = "\t"
GRADE_ORDER = ["a", "b", "c", "d", "e"]

CORE_COLUMNS = [
    "code",
    "product_name",
    "brands",
    "countries_fr",
    "ingredients_text",
    "additives_n",
    "nutrition_grade_fr",
    "energy_100g",
    "fat_100g",
    "saturated-fat_100g",
    "carbohydrates_100g",
    "sugars_100g",
    "fiber_100g",
    "proteins_100g",
    "salt_100g",
    "sodium_100g",
    "nutrition-score-fr_100g",
]

NUMERIC_NUTRITION_COLUMNS = [
    "additives_n",
    "energy_100g",
    "fat_100g",
    "saturated-fat_100g",
    "carbohydrates_100g",
    "sugars_100g",
    "fiber_100g",
    "proteins_100g",
    "salt_100g",
    "sodium_100g",
    "nutrition-score-fr_100g",
]

NUTRIENT_BOUNDS = {
    "energy_100g": (0, 3700),
    "fat_100g": (0, 100),
    "saturated-fat_100g": (0, 100),
    "carbohydrates_100g": (0, 100),
    "sugars_100g": (0, 100),
    "fiber_100g": (0, 100),
    "proteins_100g": (0, 100),
    "salt_100g": (0, 100),
    "sodium_100g": (0, 40),
    "nutrition-score-fr_100g": (-15, 40),
}
