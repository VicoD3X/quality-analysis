# Rapport qualité OpenFoodFacts

## Metadata

- Source : `data/processed/openfoodfacts-cleaned.csv`
- Génération : `2026-04-26T03:55:57+00:00`
- Version rapport : `1.0`

## Profil dataset

- Lignes : `115804`
- Colonnes : `30`
- Valeurs manquantes globales : `0.0%`
- Doublons : `44`
- Taux de doublons : `<0.1%`

## Score qualité

Score global : `99.99/100`

| Dimension | Score |
| --- | --- |
| completeness | 100.0 |
| required_columns | 100.0 |
| numeric_bounds | 100.0 |
| duplicates | 99.96 |
| nutrition_grades | 100.0 |


## Alertes

- `medium` - Colonne 'carbohydrates_100g' : 1 valeur(s) hors bornes nutritionnelles.
- `medium` - Colonne 'sugars_100g' : 4 valeur(s) hors bornes nutritionnelles.
- `medium` - Colonne 'proteins_100g' : 1 valeur(s) hors bornes nutritionnelles.
- `medium` - 44 doublon(s) détecté(s) (<0.1%).

## Valeurs manquantes - top 10

| Colonne | Volume | Taux |
| --- | --- | --- |
| code | 0 | 0.0% |
| creator | 0 | 0.0% |
| created_t | 0 | 0.0% |
| created_datetime | 0 | 0.0% |
| last_modified_t | 0 | 0.0% |
| last_modified_datetime | 0 | 0.0% |
| product_name | 0 | 0.0% |
| brands | 0 | 0.0% |
| brands_tags | 0 | 0.0% |
| countries | 0 | 0.0% |


## Bornes numériques

| Colonne | Invalides | Taux |
| --- | --- | --- |
| energy_100g | 0 | 0.0% |
| fat_100g | 0 | 0.0% |
| saturated-fat_100g | 0 | 0.0% |
| carbohydrates_100g | 1 | <0.1% |
| sugars_100g | 4 | <0.1% |
| fiber_100g | 0 | 0.0% |
| proteins_100g | 1 | <0.1% |
| salt_100g | 0 | 0.0% |
| sodium_100g | 0 | 0.0% |
| nutrition-score-fr_100g | 0 | 0.0% |


## Distribution Nutri-Grade

| Grade | Volume | Taux |
| --- | --- | --- |
| a | 26253 | 22.7% |
| b | 24311 | 21.0% |
| c | 25622 | 22.1% |
| d | 26410 | 22.8% |
| e | 13208 | 11.4% |


## Limites

- Le score qualité est heuristique et non réglementaire.
- Les bornes nutritionnelles restent des contrôles techniques simples.
- Le rapport dépend du fichier local utilisé au moment de la génération.
- L'échantillon versionné sert à la démonstration, pas à une conclusion métier.
