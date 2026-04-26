# Notes sur le notebook

## Etat

Le notebook `01_openfoodfacts_quality_analysis.ipynb` est lisible et contient une analyse complète avec sorties.

## Rôle

Il documente la démarche initiale :

- compréhension du fichier brut ;
- nettoyage ;
- analyse des valeurs manquantes ;
- visualisations nutritionnelles ;
- PCA ;
- ANOVA ;
- CCA ;
- LDA.

## Positionnement

Le notebook reste exploratoire. La phase 1 extrait uniquement les fonctions stabilisées nécessaires à un pipeline léger et testable.

## Données

Le notebook attend le fichier brut local dans `data/raw/openfoodfacts-products.tsv` ou le fichier nettoyé dans `data/processed/openfoodfacts-cleaned.csv`, selon les cellules exécutées.
