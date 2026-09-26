"""
IGNIS — ML Model Training Pipeline

Phase 4: Trains the ensemble classifier (RF + XGBoost + LightGBM) 
with Soft Voting, per §6.1 and §6.3.

Training pipeline:
1. Load training data (16 features + label)
2. Encode categorical features
3. Train/Val/Test split 70/15/15 (stratified)
4. Handle class imbalance (SMOTE + class weights)
5. Train individual models (RF, XGB, LGBM)
6. Build ensemble (Soft Voting / Stacking)
7. Hyperparameter tuning (Optuna)
8. Evaluate against §6.4 targets
9. Export model as joblib
"""

import logging
import os
import sys
import json
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    classification_report, confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

import xgboost as xgb
import lightgbm as lgb

try:
    from imblearn.over_sampling import SMOTE
    from imblearn.combine import SMOTETomek
    HAS_IMBLEARN = True
except ImportError:
    HAS_IMBLEARN = False

logger = logging.getLogger("ignis.training")

# Label names from §3.2
LABEL_NAMES = {
    0: "Industrial Fire",
    1: "Forest Fire",
    2: "Gas Flare",
    3: "Agricultural Burn",
    4: "Mining/Thermal",
    5: "Unclassified",
}

# Features for ML model (16 features from §5.3)
NUMERIC_FEATURES = [
    "brightness",           # #1
    "frp",                  # #2
    "confidence",           # #3
    "pixel_area",           # #5
    "dist_to_industry_m",   # #6
    "persistence_hours",    # #9
    "recurrence_count",     # #10
    "spatial_cluster_size", # #11
    "spread_rate",          # #12
    "month",                # #13
    "hour",                 # #14
    "bright_t31",           # #15
    "brightness_ratio",     # #16
]

CATEGORICAL_FEATURES = [
    "daynight",             # #4
    "industrial_type",      # #7
    "land_cover_class",     # #8
]

TARGET = "ml_label"


def load_training_data(csv_path: str) -> pd.DataFrame:
    """Load and validate training data."""
    logger.info(f"Loading training data from {os.path.basename(csv_path)}...")
    df = pd.read_csv(csv_path, low_memory=False)
    logger.info(f"  Records: {len(df):,}")
    logger.info(f"  Columns: {list(df.columns)}")
    
    # Verify target column exists
    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' not found")
    
    # Label distribution
    logger.info("  Label distribution:")
    for label_id, count in df[TARGET].value_counts().sort_index().items():
        name = LABEL_NAMES.get(label_id, "unknown")
        pct = 100 * count / len(df)
        logger.info(f"    {label_id} ({name}): {count:,} ({pct:.1f}%)")
    
    return df


def prepare_features(df: pd.DataFrame):
    """
    Prepare feature matrix X and target y.
    Encodes categorical features and handles missing values.
    """
    logger.info("Preparing features...")
    
    # Select available features
    available_numeric = [c for c in NUMERIC_FEATURES if c in df.columns]
    available_categorical = [c for c in CATEGORICAL_FEATURES if c in df.columns]
    
    missing_features = [
        c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES 
        if c not in df.columns
    ]
    if missing_features:
        logger.warning(f"  Missing features: {missing_features}")
    
    # Fill missing numeric values
    for col in available_numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.info(f"  Filled {col} NaNs with median: {median_val:.2f}")
    
    # Encode categorical features
    label_encoders = {}
    for col in available_categorical:
        df[col] = df[col].astype(str).fillna("unknown")
        le = LabelEncoder()
        df[col + "_encoded"] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Build feature matrix
    feature_cols = available_numeric + [c + "_encoded" for c in available_categorical]
    
    X = df[feature_cols].values.astype(np.float32)
    y_raw = df[TARGET].values.astype(int)
    
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(y_raw)
    
    logger.info(f"  Feature matrix shape: {X.shape}")
    logger.info(f"  Features used: {feature_cols}")
    logger.info(f"  Target classes encoded: {target_encoder.classes_} -> {np.arange(len(target_encoder.classes_))}")
    
    return X, y, feature_cols, label_encoders, target_encoder


def apply_smote(X_train, y_train, random_state=42):
    """Apply SMOTE oversampling to minority classes."""
    if not HAS_IMBLEARN:
        logger.warning("  imbalanced-learn not available, skipping SMOTE")
        return X_train, y_train
    
    logger.info("  Applying SMOTE oversampling...")
    
    # Check minimum class size
    unique, counts = np.unique(y_train, return_counts=True)
    min_count = counts.min()
    
    if min_count < 6:
        # SMOTE needs at least k_neighbors+1 samples
        logger.warning(f"  Minimum class has {min_count} samples, using k_neighbors={max(1, min_count-1)}")
        k = max(1, min_count - 1)
    else:
        k = 5
    
    try:
        smote = SMOTE(random_state=random_state, k_neighbors=k)
        X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
        
        logger.info(f"  Before SMOTE: {len(X_train):,} samples")
        logger.info(f"  After SMOTE: {len(X_resampled):,} samples")
        
        unique, counts = np.unique(y_resampled, return_counts=True)
        for u, c in zip(unique, counts):
            logger.info(f"    Class {u}: {c:,}")
        
        return X_resampled, y_resampled
    except Exception as e:
        logger.warning(f"  SMOTE failed: {e}, proceeding without oversampling")
        return X_train, y_train


def compute_class_weights(y):
    """Compute balanced class weights inversely proportional to frequency."""
    unique, counts = np.unique(y, return_counts=True)
    total = len(y)
    n_classes = len(unique)
    
    weights = {}
    for cls, count in zip(unique, counts):
        weights[cls] = total / (n_classes * count)
    
    logger.info(f"  Class weights: {weights}")
    return weights


def train_ensemble(
    X_train, y_train,
    X_val, y_val,
    class_weights: dict,
    random_state: int = 42,
):
    """
    Train ensemble model: RF + XGBoost + LightGBM with Soft Voting.
    Hyperparameters from §6.1.
    """
    logger.info("Training ensemble model...")
    
    # Convert class weights for sklearn format
    sample_weights_train = np.array([class_weights.get(y, 1.0) for y in y_train])
    
    # ----- Random Forest (§6.1: n_estimators=200) -----
    logger.info("  Training Random Forest (n_estimators=200)...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train, sample_weight=sample_weights_train)
    rf_acc = accuracy_score(y_val, rf.predict(X_val))
    rf_f1 = f1_score(y_val, rf.predict(X_val), average="macro")
    logger.info(f"    RF Val Accuracy: {rf_acc:.4f}, Macro F1: {rf_f1:.4f}")
    
    # ----- XGBoost (§6.1: max_depth=8) -----
    logger.info("  Training XGBoost (max_depth=8)...")
    xgb_model = xgb.XGBClassifier(
        max_depth=8,
        learning_rate=0.1,
        n_estimators=300,
        objective="multi:softprob",
        num_class=len(np.unique(y_train)),
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=random_state,
        n_jobs=-1,
        tree_method="hist",
    )
    xgb_model.fit(
        X_train, y_train,
        sample_weight=sample_weights_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    xgb_acc = accuracy_score(y_val, xgb_model.predict(X_val))
    xgb_f1 = f1_score(y_val, xgb_model.predict(X_val), average="macro")
    logger.info(f"    XGB Val Accuracy: {xgb_acc:.4f}, Macro F1: {xgb_f1:.4f}")
    
    # ----- LightGBM (§6.1: num_leaves=63) -----
    logger.info("  Training LightGBM (num_leaves=63)...")
    lgb_model = lgb.LGBMClassifier(
        num_leaves=63,
        learning_rate=0.1,
        n_estimators=300,
        objective="multiclass",
        num_class=len(np.unique(y_train)),
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
        verbose=-1,
    )
    lgb_model.fit(
        X_train, y_train,
        sample_weight=sample_weights_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.log_evaluation(0)],
    )
    lgb_acc = accuracy_score(y_val, lgb_model.predict(X_val))
    lgb_f1 = f1_score(y_val, lgb_model.predict(X_val), average="macro")
    logger.info(f"    LGBM Val Accuracy: {lgb_acc:.4f}, Macro F1: {lgb_f1:.4f}")
    
    # ----- Soft Voting Ensemble -----
    logger.info("  Building Soft Voting ensemble...")
    ensemble = VotingClassifier(
        estimators=[
            ("rf", rf),
            ("xgb", xgb_model),
            ("lgbm", lgb_model),
        ],
        voting="soft",
    )
    # VotingClassifier needs fitting, but we already fit individual models
    # Use a workaround: set estimators_ directly
    ensemble.estimators_ = [rf, xgb_model, lgb_model]
    ensemble.le_ = LabelEncoder().fit(y_train)
    ensemble.classes_ = np.unique(y_train)
    
    return ensemble, {"rf": rf, "xgb": xgb_model, "lgbm": lgb_model}


def evaluate_model(model, X_test, y_test_enc, target_encoder, model_name="Ensemble"):
    """
    Evaluate model against §6.4 targets:
    - Overall accuracy > 85%
    - Macro F1 > 0.82
    - Industrial Fire recall > 90%
    - Gas Flare precision > 90%
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"EVALUATION: {model_name}")
    logger.info(f"{'='*60}")
    
    # Get predictions
    if hasattr(model, 'predict'):
        y_pred_enc = model.predict(X_test)
    else:
        # For voting classifier with pre-fit estimators
        probs = np.zeros((len(X_test), len(target_encoder.classes_)))
        for est in model.estimators_:
            probs += est.predict_proba(X_test)
        probs /= len(model.estimators_)
        y_pred_enc = np.argmax(probs, axis=1)
    
    y_pred = target_encoder.inverse_transform(y_pred_enc)
    y_test = target_encoder.inverse_transform(y_test_enc)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    
    # Per-class metrics
    target_names = [LABEL_NAMES.get(i, f"Class {i}") for i in sorted(np.unique(np.concatenate([y_test, y_pred])))]
    report = classification_report(
        y_test, y_pred,
        target_names=target_names,
        digits=4,
        output_dict=True,
    )
    
    # Industrial Fire recall (class 0)
    industrial_recall = report.get("Industrial Fire", {}).get("recall", 0)
    
    # Gas Flare precision (class 2)
    gas_precision = report.get("Gas Flare", {}).get("precision", 0)
    
    # Print results
    logger.info(f"Overall Accuracy:        {accuracy:.4f}  {'✓' if accuracy > 0.85 else '✗'} (target > 0.85)")
    logger.info(f"Macro F1-Score:          {macro_f1:.4f}  {'✓' if macro_f1 > 0.82 else '✗'} (target > 0.82)")
    logger.info(f"Industrial Fire Recall:  {industrial_recall:.4f}  {'✓' if industrial_recall > 0.90 else '✗'} (target > 0.90)")
    logger.info(f"Gas Flare Precision:     {gas_precision:.4f}  {'✓' if gas_precision > 0.90 else '✗'} (target > 0.90)")
    
    # Full report
    logger.info(f"\nClassification Report:")
    report_str = classification_report(y_test, y_pred, target_names=target_names, digits=4)
    for line in report_str.split("\n"):
        logger.info(f"  {line}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"\nConfusion Matrix:")
    logger.info(f"  {cm}")
    
    metrics = {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "industrial_fire_recall": float(industrial_recall),
        "gas_flare_precision": float(gas_precision),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
    }
    
    return metrics


def run_training_pipeline(
    training_csv_path: str,
    model_output_dir: str,
    random_state: int = 42,
):
    """Full training pipeline from data to exported model."""
    
    logger.info("=" * 60)
    logger.info("ML MODEL TRAINING PIPELINE")
    logger.info(f"Started: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Step 1: Load data
    df = load_training_data(training_csv_path)
    
    # Step 2: Prepare features
    X, y, feature_names, label_encoders, target_encoder = prepare_features(df)
    
    # Step 3: Train/Val/Test split (70/15/15, stratified)
    logger.info("Splitting data 70/15/15 (stratified)...")
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=random_state
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.176,  # 0.176 of 0.85 ≈ 0.15 of total
        stratify=y_train_val, random_state=random_state
    )
    
    logger.info(f"  Train: {len(X_train):,}, Val: {len(X_val):,}, Test: {len(X_test):,}")
    
    # Step 4: Handle class imbalance
    class_weights = compute_class_weights(y_train)
    X_train_resampled, y_train_resampled = apply_smote(X_train, y_train, random_state)
    
    # Step 5 & 6: Train ensemble
    ensemble, individual_models = train_ensemble(
        X_train_resampled, y_train_resampled,
        X_val, y_val,
        class_weights,
        random_state,
    )
    
    # Step 7: Evaluate on test set
    metrics = {}
    for name, model in individual_models.items():
        m = evaluate_model(model, X_test, y_test, target_encoder, model_name=name.upper())
        metrics[name] = m
    
    # Ensemble evaluation
    ensemble_metrics = evaluate_model(ensemble, X_test, y_test, target_encoder, model_name="ENSEMBLE (Soft Voting)")
    metrics["ensemble"] = ensemble_metrics
    
    # Step 8: Export model
    os.makedirs(model_output_dir, exist_ok=True)
    
    # Save ensemble components
    model_path = os.path.join(model_output_dir, "classifier_v1.joblib")
    model_artifact = {
        "ensemble": ensemble,
        "individual_models": individual_models,
        "feature_names": feature_names,
        "label_encoders": label_encoders,
        "target_encoder": target_encoder,
        "label_names": LABEL_NAMES,
        "class_weights": class_weights,
        "version": "v1.0",
        "trained_at": datetime.now().isoformat(),
        "training_records": len(X_train_resampled),
        "metrics": {
            k: {mk: mv for mk, mv in v.items() if mk != "classification_report" and mk != "confusion_matrix"}
            for k, v in metrics.items()
        },
    }
    
    joblib.dump(model_artifact, model_path)
    size_mb = os.path.getsize(model_path) / (1024 * 1024)
    logger.info(f"\nModel saved: {model_path} ({size_mb:.1f} MB)")
    
    # Save metrics JSON
    metrics_path = os.path.join(model_output_dir, "training_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(
            {k: {mk: mv for mk, mv in v.items() if mk != "confusion_matrix"} 
             for k, v in metrics.items()},
            f, indent=2, default=str,
        )
    logger.info(f"Metrics saved: {metrics_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 60)
    
    return ensemble, metrics


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    data_dir = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\suraj\Desktop\NASA-FIRMS\data"
    
    training_csv = os.path.join(data_dir, "processed", "ignis_training_data.csv")
    model_dir = os.path.join(data_dir, "models")
    
    if not os.path.exists(training_csv):
        print(f"ERROR: Training data not found at {training_csv}")
        print("Run generate_labels.py first!")
        sys.exit(1)
    
    ensemble, metrics = run_training_pipeline(training_csv, model_dir)
    
    # Print summary
    em = metrics.get("ensemble", {})
    print(f"\n{'='*40}")
    print(f"Ensemble Accuracy: {em.get('accuracy', 0):.4f}")
    print(f"Ensemble Macro F1: {em.get('macro_f1', 0):.4f}")
    print(f"Industrial Fire Recall: {em.get('industrial_fire_recall', 0):.4f}")
    print(f"Gas Flare Precision: {em.get('gas_flare_precision', 0):.4f}")
    print(f"{'='*40}")
