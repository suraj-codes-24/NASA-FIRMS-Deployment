"""
IGNIS — ML Model Loading & Prediction Module

Handles loading the trained ensemble classifier and performing inference
on new hotspot data. The model artifact is a joblib dictionary containing:
- ensemble: VotingClassifier (RF + XGBoost + LightGBM)
- feature_names: list of feature column names
- label_encoders: dict of LabelEncoder objects for categoricals
- target_encoder: LabelEncoder for the target variable
- label_names: dict mapping int → class name string
- version: model version string
"""

import logging
import os
import numpy as np
import pandas as pd
import joblib

from app.models.spatial import MLClassificationEnum

logger = logging.getLogger("ignis.ml.model")

# Default model path
MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data", "models",
)
DEFAULT_MODEL_PATH = os.path.join(MODEL_DIR, "classifier_v1.joblib")

# Class label → Enum mapping
LABEL_TO_ENUM = {
    0: MLClassificationEnum.INDUSTRIAL_FIRE,
    1: MLClassificationEnum.FOREST_FIRE,
    2: MLClassificationEnum.GAS_FLARE,
    3: MLClassificationEnum.AGRICULTURAL_BURN,
    4: MLClassificationEnum.MINING_THERMAL,
    5: MLClassificationEnum.UNCLASSIFIED,
}

_cached_model = None


def load_model(path: str = DEFAULT_MODEL_PATH):
    """Load the ensemble model artifact from disk (cached)."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model
    if not os.path.exists(path):
        logger.error(f"Model file not found: {path}")
        return None
    try:
        _cached_model = joblib.load(path)
        logger.info(f"Loaded model v{_cached_model.get('version', '?')} from {path}")
        return _cached_model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return None


def predict(feature_df: pd.DataFrame, model_artifact: dict = None):
    """
    Run inference on a DataFrame of features.

    Returns:
        labels: list[MLClassificationEnum]
        confidences: list[float]  (0-100 scale)
        probabilities: np.ndarray  (raw probability matrix)
    """
    if model_artifact is None:
        model_artifact = load_model()
    if model_artifact is None:
        # Fallback: return Unclassified for everything
        n = len(feature_df)
        return (
            [MLClassificationEnum.UNCLASSIFIED] * n,
            [0.0] * n,
            np.zeros((n, 6)),
        )

    ensemble = model_artifact["ensemble"]
    feature_names = model_artifact["feature_names"]
    label_encoders = model_artifact["label_encoders"]
    target_encoder = model_artifact["target_encoder"]

    df = feature_df.copy()

    # Encode categorical columns
    for col, le in label_encoders.items():
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("unknown")
            known = set(le.classes_)
            df[col] = df[col].apply(lambda x: x if x in known else "unknown")
            if "unknown" not in le.classes_:
                le.classes_ = np.append(le.classes_, "unknown")
            df[col + "_encoded"] = le.transform(df[col])

    # Build feature matrix
    X = df[feature_names].values.astype(np.float32)

    # Soft-voting: average probabilities across estimators
    n_classes = len(target_encoder.classes_)
    probs = np.zeros((len(X), n_classes))
    for est in ensemble.estimators_:
        probs += est.predict_proba(X)
    probs /= len(ensemble.estimators_)

    y_pred_enc = np.argmax(probs, axis=1)
    max_probs = np.max(probs, axis=1)
    y_pred = target_encoder.inverse_transform(y_pred_enc)

    labels = [LABEL_TO_ENUM.get(int(y), MLClassificationEnum.UNCLASSIFIED) for y in y_pred]
    confidences = (max_probs * 100.0).tolist()

    return labels, confidences, probs
