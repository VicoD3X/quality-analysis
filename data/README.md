# Données

Ce dossier sépare les données locales lourdes des fichiers versionnables.

## Données brutes

Le fichier brut OpenFoodFacts doit être placé ici :

```text
data/raw/openfoodfacts-products.tsv
```

Il est séparé par tabulation et n'est pas versionné dans Git.

## Données traitées

Le dataset nettoyé local est attendu ici :

```text
data/processed/openfoodfacts-cleaned.csv
```

Il peut être reconstruit avec :

```bash
python scripts/build_clean_dataset.py
```

## Echantillon versionné

Le dépôt contient un échantillon léger :

```text
data/sample/openfoodfacts-cleaned-sample.csv
```

Il sert aux tests, aux exemples et à la compréhension rapide du schéma sans versionner le dataset complet.
