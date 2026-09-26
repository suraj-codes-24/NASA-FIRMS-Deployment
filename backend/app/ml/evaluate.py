"""
IGNIS — ML Model Evaluation Module (backend/app/ml/evaluate.py)

Provides functions to evaluate a trained IGNIS classifier against
the performance targets defined in §6.4:
  - Overall accuracy  > 85%
  - Macro F1-Score    > 0.82
  - Industrial Fire Recall > 90%
  - Gas Flare Precision    > 90%

Usage:
    python -m backend.app.ml.evaluate --model data/models/classifier_v1.joblib --data data/firms_enriched_v2.csv
"""

import logging
import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

logger = logging.getLogger("ignis.ml.evaluate")

# §6.4 targets
TARGETS = {
    "overall_accuracy": 0.85,
    "macro_f1": 0.82,
    "industrial_fire_recall": 0.90,
    "gas_flare_precision": 0.90,
}

LABEL_NAMES = {
    0: "Industrial Fire",
    1: "Forest Fire",
    2: "Gas Flare",
    3: "Agricultural Burn",
    4: "Mining/Thermal",
    5: "Unclassified",
}


def evaluate_model(model_path: str, data_path: str, test_size: float = 0.15) -> dict:
    """
    Evaluate a trained model against the spec targets.

    Args:
        model_path: Path to the joblib model artifact.
        data_path: Path to the labeled CSV dataset.
        test_size: Fraction of data to hold out for evaluation.

    Returns:
        dict with metrics, per-class report, pass/fail flags, and confusion matrix.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data not found: {data_path}")

    # Load model
    artifact = joblib.load(model_path)
    ensemble = artifact["ensemble"]
    feature_names = artifact["feature_names"]
    label_encoders = artifact["label_encoders"]
    target_encoder = artifact["target_encoder"]

    logger.info(f"Loaded model v{artifact.get('version', '?')} with {len(feature_names)} features")

    # Load data
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} rows from {data_path}")

    if "label" not in df.columns:
        raise ValueError("Dataset must contain a 'label' column")

    # Encode categoricals
    for col, le in label_encoders.items():
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("unknown")
            known = set(le.classes_)
            df[col] = df[col].apply(lambda x: x if x in known else "unknown")
            if "unknown" not in le.classes_:
                le.classes_ = np.append(le.classes_, "unknown")
            df[col + "_encoded"] = le.transform(df[col])

    # Prepare features and target
    y_true_str = df["label"].values
    y_true_enc = target_encoder.transform(y_true_str)

    X = df[feature_names].values.astype(np.float32)

    # Split for evaluation (use same seed as training for reproducibility)
    _, X_test, _, y_test = train_test_split(
        X, y_true_enc, test_size=test_size, random_state=42, stratify=y_true_enc
    )

    # Predict
    n_classes = len(target_encoder.classes_)
    probs = np.zeros((len(X_test), n_classes))
    for est in ensemble.estimators_:
        probs += est.predict_proba(X_test)
    probs /= len(ensemble.estimators_)
    y_pred = np.argmax(probs, axis=1)

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    # Per-class metrics
    class_report = classification_report(
        y_test, y_pred,
        target_names=[LABEL_NAMES[i] for i in range(n_classes)],
        output_dict=True,
        zero_division=0,
    )

    # Industrial Fire recall (class 0)
    industrial_recall = recall_score(y_test, y_pred, labels=[0], average="micro", zero_division=0)

    # Gas Flare precision (class 2)
    gas_flare_precision = precision_score(y_test, y_pred, labels=[2], average="micro", zero_division=0)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # Pass/fail checks
    results = {
        "overall_accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "industrial_fire_recall": round(industrial_recall, 4),
        "gas_flare_precision": round(gas_flare_precision, 4),
        "test_samples": len(X_test),
        "confusion_matrix": cm.tolist(),
        "classification_report": class_report,
        "targets": TARGETS,
        "passes": {
            "overall_accuracy": accuracy >= TARGETS["overall_accuracy"],
            "macro_f1": macro_f1 >= TARGETS["macro_f1"],
            "industrial_fire_recall": industrial_recall >= TARGETS["industrial_fire_recall"],
            "gas_flare_precision": gas_flare_precision >= TARGETS["gas_flare_precision"],
        },
    }

    results["all_targets_met"] = all(results["passes"].values())

    # Log results
    logger.info("=" * 50)
    logger.info("EVALUATION RESULTS")
    logger.info("=" * 50)
    logger.info(f"  Overall Accuracy:       {accuracy:.4f}  (target: {TARGETS['overall_accuracy']})  {'✅' if results['passes']['overall_accuracy'] else '❌'}")
    logger.info(f"  Macro F1:               {macro_f1:.4f}  (target: {TARGETS['macro_f1']})  {'✅' if results['passes']['macro_f1'] else '❌'}")
    logger.info(f"  Industrial Fire Recall: {industrial_recall:.4f}  (target: {TARGETS['industrial_fire_recall']})  {'✅' if results['passes']['industrial_fire_recall'] else '❌'}")
    logger.info(f"  Gas Flare Precision:    {gas_flare_precision:.4f}  (target: {TARGETS['gas_flare_precision']})  {'✅' if results['passes']['gas_flare_precision'] else '❌'}")
    logger.info(f"  All targets met: {'✅ YES' if results['all_targets_met'] else '❌ NO'}")

    return results


def save_evaluation_report(results: dict, output_path: str = "data/models/evaluation_report.json"):
    """Save evaluation results to a JSON file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Evaluation report saved to {output_path}")


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Evaluate IGNIS ML model")
    parser.add_argument("--model", default="data/models/classifier_v1.joblib", help="Model artifact path")
    parser.add_argument("--data", required=True, help="Path to labeled CSV dataset")
    parser.add_argument("--output", default="data/models/evaluation_report.json", help="Report output path")
    args = parser.parse_args()

    results = evaluate_model(args.model, args.data)
    save_evaluation_report(results, args.output)
