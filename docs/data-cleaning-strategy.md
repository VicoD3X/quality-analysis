# Stratégie de nettoyage

## Objectif

Le dataset OpenFoodFacts contient beaucoup de colonnes, de valeurs manquantes et de valeurs nutritionnelles parfois incohérentes. La stratégie consiste à produire un sous-ensemble plus fiable pour l'analyse.

## Règles principales

- Supprimer les colonnes trop incomplètes.
- Garder les colonnes nutritionnelles utiles à l'analyse.
- Normaliser `nutrition_grade_fr`.
- Contrôler les valeurs pour 100 g avec des bornes simples.
- Supprimer les doublons d'identification disponibles.
- Imputer les valeurs numériques restantes par médiane.

## Bornes métier utilisées

Les bornes sont volontairement simples :

- nutriments pour 100 g : entre `0` et `100` ;
- énergie : entre `0` et `3700` kJ pour 100 g ;
- sodium : entre `0` et `40` g ;
- score nutritionnel : entre `-15` et `40`.

Ces seuils servent à retirer les incohérences les plus visibles. Ils doivent être revus si l'objectif devient réglementaire ou scientifique.
