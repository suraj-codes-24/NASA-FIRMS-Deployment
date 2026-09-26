"""
IGNIS — ML Training Module (backend/app/ml/train.py)

Provides a high-level API for triggering model training from the backend.
The actual training implementation lives in ml_pipeline/scripts/train_model.py.

Usage (from project root):
    python -m backend.app.ml.train --data data/firms_enriched_v2.csv --output data/models/classifier_v1.joblib

Or programmatically:
    from backend.app.ml.train import train_model
    metrics = train_model("data/firms_enriched_v2.csv", "data/models/classifier_v1.joblib")
"""

import logging
import os
import sys

logger = logging.getLogger("ignis.ml.train")

# Ensure ml_pipeline is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


def train_model(data_path: str, output_path: str = "data/models/classifier_v1.joblib", use_smote: bool = True) -> dict:
    """
    Train the IGNIS ensemble classifier.

    Args:
        data_path: Path to the enriched FIRMS CSV (must contain 16 features + 'label' column).
        output_path: Path to save the joblib model artifact.
        use_smote: Whether to apply SMOTE oversampling for class imbalance.

    Returns:
        dict: Training metrics (accuracy, f1, per-class precision/recall).
    """
    # Import the full training pipeline
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "ml_pipeline", "scripts"))
    try:
        from train_model import main as run_training
    except ImportError:
        logger.error("Cannot import ml_pipeline/scripts/train_model.py. Ensure it exists.")
        raise

    # Run training
    logger.info(f"Starting model training with data: {data_path}")
    logger.info(f"Output model path: {output_path}")
    logger.info(f"SMOTE enabled: {use_smote}")

    metrics = run_training(data_path, output_path, use_smote=use_smote)

    logger.info("Training complete.")
    logger.info(f"  Accuracy: {metrics.get('accuracy', 'N/A')}")
    logger.info(f"  Macro F1: {metrics.get('macro_f1', 'N/A')}")

    return metrics


def get_model_info(model_path: str = "data/models/classifier_v1.joblib") -> dict:
    """
    Get metadata about a trained model artifact without loading the full model.
    """
    import joblib

    if not os.path.exists(model_path):
        return {"exists": False, "path": model_path}

    artifact = joblib.load(model_path)
    return {
        "exists": True,
        "path": model_path,
        "version": artifact.get("version", "unknown"),
        "n_features": len(artifact.get("feature_names", [])),
        "feature_names": artifact.get("feature_names", []),
        "n_estimators": len(artifact.get("ensemble", {}).estimators_) if hasattr(artifact.get("ensemble"), "estimators_") else 0,
        "file_size_mb": round(os.path.getsize(model_path) / (1024 * 1024), 1),
    }


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Train IGNIS ensemble classifier")
    parser.add_argument("--data", required=True, help="Path to enriched FIRMS CSV")
    parser.add_argument("--output", default="data/models/classifier_v1.joblib", help="Output model path")
    parser.add_argument("--no-smote", action="store_true", help="Disable SMOTE oversampling")
    args = parser.parse_args()

    metrics = train_model(args.data, args.output, use_smote=not args.no_smote)
    print(f"\nFinal Metrics: {metrics}")
