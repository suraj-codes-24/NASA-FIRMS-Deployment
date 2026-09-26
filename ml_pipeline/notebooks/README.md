# ML Pipeline Notebooks

This directory contains Jupyter notebooks used during the exploratory data analysis (EDA), feature engineering validation, and model selection phases.

## Available Notebooks (Expected)

1. `01_eda_firms_data.ipynb` - Exploratory Data Analysis of NASA FIRMS active fire datasets, checking for class imbalance and distribution of FRP/Brightness.
2. `02_spatial_enrichment.ipynb` - Validation of PostGIS/Geopandas spatial joins between OSM industrial infrastructure and FIRMS hotspots.
3. `03_feature_engineering.ipynb` - Derivation of temporal and spatial features.
4. `04_model_training_evaluation.ipynb` - Iterative training of RF, XGBoost, and LightGBM models, checking F1-score performance against the 6-class taxonomy.

*Note: For the hackathon, the final training pipeline is formalized in `ml_pipeline/scripts/train_model.py`.*
