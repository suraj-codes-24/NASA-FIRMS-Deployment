import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthetic_data(n_samples=5000):
    """
    Generates synthetic training data mirroring the FIRMS telemetry and spatial enrichment.
    """
    np.random.seed(42)
    
    # Feature columns matching the ones used in ml_tasks.py
    # "brightness", "frp", "confidence", "pixel_area", "dist_to_industry_m", 
    # "persistence_hours", "recurrence_count", "spatial_cluster_size", "spread_rate", 
    # "month", "hour", "bright_t31", "brightness_ratio", "daynight", "industrial_type", "land_cover_class"
    
    data = []
    
    # Generate Industrial Fires (0)
    for _ in range(n_samples // 4):
        data.append({
            "brightness": np.random.normal(350, 20),
            "frp": np.random.normal(150, 50),
            "confidence": np.random.normal(90, 10),
            "pixel_area": np.random.normal(1.2, 0.2),
            "dist_to_industry_m": np.random.exponential(500), # close to industry
            "persistence_hours": np.random.uniform(0, 48),
            "recurrence_count": np.random.randint(1, 10),
            "spatial_cluster_size": np.random.randint(1, 5),
            "spread_rate": np.random.normal(0.5, 0.2),
            "month": np.random.randint(1, 13),
            "hour": np.random.randint(0, 24),
            "bright_t31": np.random.normal(300, 15),
            "daynight": np.random.choice(["D", "N"]),
            "industrial_type": np.random.choice(["refinery", "chemical", "manufacturing", "unknown"]),
            "land_cover_class": np.random.choice(["Urban", "Industrial", "Unknown"]),
            "target": 0
        })

    # Generate Forest Fires (1)
    for _ in range(n_samples // 4):
        data.append({
            "brightness": np.random.normal(330, 25),
            "frp": np.random.normal(200, 100),
            "confidence": np.random.normal(85, 15),
            "pixel_area": np.random.normal(1.5, 0.5),
            "dist_to_industry_m": np.random.normal(20000, 5000), # far from industry
            "persistence_hours": np.random.uniform(0, 120),
            "recurrence_count": np.random.randint(1, 3),
            "spatial_cluster_size": np.random.randint(2, 20),
            "spread_rate": np.random.normal(5.0, 2.0), # fast spread
            "month": np.random.randint(6, 10), # summer months
            "hour": np.random.randint(0, 24),
            "bright_t31": np.random.normal(290, 20),
            "daynight": np.random.choice(["D", "N"]),
            "industrial_type": "unknown",
            "land_cover_class": np.random.choice(["Forest", "Shrubland", "Grassland"]),
            "target": 1
        })

    # Generate Gas Flares (2)
    for _ in range(n_samples // 4):
        data.append({
            "brightness": np.random.normal(310, 10),
            "frp": np.random.normal(50, 20),
            "confidence": np.random.normal(95, 5),
            "pixel_area": np.random.normal(1.0, 0.1),
            "dist_to_industry_m": np.random.exponential(100), # very close to industry
            "persistence_hours": np.random.uniform(100, 5000), # Highly persistent
            "recurrence_count": np.random.randint(50, 200), # Highly recurrent
            "spatial_cluster_size": 1, # Isolated
            "spread_rate": 0.0, # Doesn't spread
            "month": np.random.randint(1, 13),
            "hour": np.random.randint(0, 24),
            "bright_t31": np.random.normal(305, 10),
            "daynight": np.random.choice(["D", "N"]),
            "industrial_type": np.random.choice(["refinery", "oil_gas"]),
            "land_cover_class": "Industrial",
            "target": 2
        })

    # Generate Agricultural Burns (3)
    for _ in range(n_samples // 4):
        data.append({
            "brightness": np.random.normal(305, 15),
            "frp": np.random.normal(40, 20),
            "confidence": np.random.normal(70, 15),
            "pixel_area": np.random.normal(1.0, 0.3),
            "dist_to_industry_m": np.random.normal(10000, 4000),
            "persistence_hours": np.random.uniform(0, 12),
            "recurrence_count": 1,
            "spatial_cluster_size": np.random.randint(1, 3),
            "spread_rate": np.random.normal(1.0, 0.5),
            "month": np.random.choice([3, 4, 5, 9, 10, 11]), # spring/fall
            "hour": np.random.randint(8, 18), # usually daytime
            "bright_t31": np.random.normal(295, 15),
            "daynight": "D",
            "industrial_type": "unknown",
            "land_cover_class": "Cropland",
            "target": 3
        })

    df = pd.DataFrame(data)
    df["brightness_ratio"] = df["brightness"] / df["bright_t31"]
    
    # Clip limits
    df["confidence"] = df["confidence"].clip(0, 100)
    df["dist_to_industry_m"] = df["dist_to_industry_m"].clip(0, None)
    
    return df


def train():
    logger.info("Generating synthetic telemetry data...")
    df = generate_synthetic_data(10000)
    
    feature_names = [
        "brightness", "frp", "confidence", "pixel_area", "dist_to_industry_m",
        "persistence_hours", "recurrence_count", "spatial_cluster_size", "spread_rate",
        "month", "hour", "bright_t31", "brightness_ratio",
        "daynight_encoded", "industrial_type_encoded", "land_cover_class_encoded"
    ]
    
    # Encode categorical features
    label_encoders = {}
    for col in ["daynight", "industrial_type", "land_cover_class"]:
        le = LabelEncoder()
        # Add 'unknown' so unseen variables in production don't crash the encoder
        unique_vals = list(df[col].unique())
        if "unknown" not in unique_vals:
            unique_vals.append("unknown")
        le.fit(unique_vals)
        
        # We need to map unseen values to unknown before transforming
        df[col] = df[col].apply(lambda x: x if x in le.classes_ else "unknown")
        df[col + "_encoded"] = le.transform(df[col])
        label_encoders[col] = le

    X = df[feature_names].values.astype(np.float32)
    y = df["target"].values
    
    target_encoder = LabelEncoder()
    y_enc = target_encoder.fit_transform(y)
    
    logger.info("Training Random Forest ensemble...")
    # Simulate a VotingClassifier using two Random Forests with different seeds/parameters
    rf1 = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf2 = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=123)
    
    ensemble = VotingClassifier(estimators=[('rf1', rf1), ('rf2', rf2)], voting='soft')
    ensemble.fit(X, y_enc)
    
    # Evaluate
    y_pred = ensemble.predict(X)
    logger.info("\n" + classification_report(y_enc, y_pred, target_names=["Industrial", "Forest", "Gas Flare", "Agri"]))
    
    # Prepare artifact
    label_names = {
        0: 'INDUSTRIAL_FIRE',
        1: 'FOREST_FIRE',
        2: 'GAS_FLARE',
        3: 'AGRICULTURAL_BURN',
        4: 'MINING_THERMAL',
        5: 'UNCLASSIFIED'
    }
    
    artifact = {
        "version": "v1.1-random-forest",
        "ensemble": ensemble,
        "feature_names": feature_names,
        "label_encoders": label_encoders,
        "target_encoder": target_encoder,
        "label_names": label_names
    }
    
    # Determine save path
    base_dir = os.path.dirname(os.path.dirname(__file__)) # goes up to NASA-FIRMS
    model_dir = os.path.join(base_dir, "data", "models")
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, "classifier_v1.joblib")
    
    logger.info(f"Exporting model artifact to {model_path}...")
    joblib.dump(artifact, model_path)
    logger.info("ML Training pipeline complete! The model is now ready for production.")

if __name__ == "__main__":
    train()
