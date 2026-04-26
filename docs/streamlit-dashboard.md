# Interface Streamlit locale

## Rôle

L'interface Streamlit sert à visualiser rapidement le rapport qualité généré par le moteur Python du projet. Elle ne recalcule pas l'audit depuis le CSV : elle lit uniquement `reports/quality_report.json`.

## Source des données

La source affichée est le rapport produit par :

```bash
python scripts/generate_quality_report.py
```

Le script utilise `data/processed/openfoodfacts-cleaned.csv` si ce fichier existe localement. Sinon, il utilise l'échantillon versionné `data/sample/openfoodfacts-cleaned-sample.csv`.

## Sections du dashboard

- score qualité global ;
- profil du dataset ;
- complétude et colonnes les plus manquantes ;
- colonnes attendues présentes ou absentes ;
- valeurs hors bornes nutritionnelles ;
- distribution des Nutri-Grades ;
- moyennes nutritionnelles par grade ;
- alertes qualité ;
- limites méthodologiques.

## Lancement

```bash
pip install -r requirements-app.txt
python scripts/generate_quality_report.py
streamlit run app/streamlit_app.py
```

## Limites

Cette interface est une démonstration locale portfolio. Elle ne constitue pas un service en production, ne fournit pas d'API et ne remplace pas une validation scientifique ou réglementaire des données nutritionnelles.
