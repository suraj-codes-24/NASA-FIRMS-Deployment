"""
IGNIS — Semi-Supervised Labeling Pipeline

Phase 3: Assigns fire classification labels to enriched FIRMS hotspots
using the rule-based labeling strategy from §6.2 and the classification
decision flow from §3.3.

Labeling Strategy (from document):
- Rule-based: OSM proximity → Industrial Fire / Gas Flare
- Land-cover: Forest cover + spatial spread → Forest Fire
- Seasonal: Cropland + Oct-Dec/Apr-May → Agricultural Burn
- VIIRS Nightfire: Known flare catalog → Gas Flare
- Remaining: Unclassified

Class balance strategy (user decision: "do the best"):
- Undersample Unclassified to ~5000
- SMOTE minority classes to ~3000 each
- Class weights during training
"""

import logging
import os
import sys
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("ignis.labeling")

# Label encoding (matches §3.2)
LABELS = {
    "industrial_fire": 0,
    "forest_fire": 1,
    "gas_flare": 2,
    "agricultural_burn": 3,
    "mining_thermal": 4,
    "unclassified": 5,
}

# Thresholds from §3.3 Classification Decision Flow
CONFIDENCE_THRESHOLD = 50           # §3.3: Confidence > 50%
INDUSTRIAL_PROXIMITY_M = 2000       # §3.3: Within 2km of industrial facility
PERSISTENCE_THRESHOLD_HOURS = 48    # §3.3: Persistent > 48hrs
FRP_INDUSTRIAL_THRESHOLD = 100      # §3.3: FRP > 100 MW
FRP_URBAN_THRESHOLD = 50            # §3.3: FRP > 50 MW

# Agricultural burn seasons (India)
AGRI_BURN_MONTHS = [4, 5, 10, 11, 12]   # §3.3: Oct-Dec / Apr-May

# Mining-associated facility types
MINING_TYPES = {"mine", "quarry", "mine_shaft", "mining", "coal"}

# Refinery/gas facility types
REFINERY_TYPES = {
    "refinery", "oil_refinery", "petroleum", "petrochemical",
    "gas_processing", "lng_terminal", "gas", "oil_field",
    "offshore_platform", "petroleum_well", "chemical",
}

# Power plant types
POWER_TYPES = {"power_plant", "power", "coal_generator", "generator"}

# Industrial types (general)
INDUSTRIAL_GENERAL = {"industrial", "factory", "works", "storage_tank", "railway"}


def load_known_flares(flare_csv_path: str) -> pd.DataFrame:
    """Load the known gas flare reference locations."""
    if not os.path.exists(flare_csv_path):
        logger.warning(f"Known flares file not found: {flare_csv_path}")
        return pd.DataFrame()
    
    flares = pd.read_csv(flare_csv_path)
    logger.info(f"  Loaded {len(flares)} known gas flare locations")
    return flares


def is_near_known_flare(lat: float, lon: float, flares: pd.DataFrame, radius_km: float = 5.0) -> bool:
    """Check if a hotspot is within radius_km of a known gas flare location."""
    if flares.empty:
        return False
    
    # Simple distance check (approximate, good enough for 5km)
    dlat = (flares["lat"] - lat) * 111.0
    dlon = (flares["lon"] - lon) * 111.0 * np.cos(np.radians(lat))
    dist = np.sqrt(dlat**2 + dlon**2)
    
    return (dist < radius_km).any()


def apply_classification_rules(hotspots: pd.DataFrame, flares: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the classification decision flow from §3.3.
    
    Flow:
    1. Confidence > 50? → No → Unclassified
    2. Within 2km of industrial facility?
       → Yes: Persistent > 48hrs? → Gas Flare
              FRP > 100MW? → Industrial Fire
              else → Mining/Thermal
       → No: Land cover type?
              Forest → Spatial spread? → Forest Fire
              Cropland → Seasonal? → Agricultural Burn
              Urban → FRP > 50MW? → Possible Industrial Fire
              else → Unclassified
    """
    logger.info("Applying classification rules from §3.3...")
    
    hotspots = hotspots.copy()
    n = len(hotspots)
    
    # Initialize all as unclassified
    hotspots["ml_label"] = LABELS["unclassified"]
    
    # Step 1: Filter by confidence
    # VIIRS confidence was mapped: l=30, n=50, h=90
    # MODIS confidence: 0-100
    low_conf = hotspots["confidence"] < CONFIDENCE_THRESHOLD
    hotspots.loc[low_conf, "ml_label"] = LABELS["unclassified"]
    logger.info(f"  Low confidence (<{CONFIDENCE_THRESHOLD}): {low_conf.sum():,}")
    
    # Work with confident hotspots only
    conf_mask = ~low_conf
    
    # Step 2: Near industrial facility (within 2km)
    near_industry = conf_mask & (hotspots["dist_to_industry_m"] <= INDUSTRIAL_PROXIMITY_M)
    
    # 2a: Near industry + persistent > 48hrs → Gas Flare
    gas_flare_mask = (
        near_industry &
        (hotspots["persistence_hours"] >= PERSISTENCE_THRESHOLD_HOURS) &
        hotspots["industrial_type"].str.lower().isin(REFINERY_TYPES | POWER_TYPES)
    )
    hotspots.loc[gas_flare_mask, "ml_label"] = LABELS["gas_flare"]
    logger.info(f"  Gas Flare (persistent near refinery): {gas_flare_mask.sum():,}")
    
    # 2b: Near industry + high FRP → Industrial Fire
    industrial_fire_mask = (
        near_industry &
        ~gas_flare_mask &
        (hotspots["frp"] >= FRP_INDUSTRIAL_THRESHOLD)
    )
    hotspots.loc[industrial_fire_mask, "ml_label"] = LABELS["industrial_fire"]
    logger.info(f"  Industrial Fire (high FRP near industry): {industrial_fire_mask.sum():,}")
    
    # 2c: Near mining facility → Mining/Thermal
    mining_mask = (
        near_industry &
        ~gas_flare_mask &
        ~industrial_fire_mask &
        hotspots["industrial_type"].str.lower().isin(MINING_TYPES)
    )
    hotspots.loc[mining_mask, "ml_label"] = LABELS["mining_thermal"]
    logger.info(f"  Mining/Thermal (near mine): {mining_mask.sum():,}")
    
    # 2d: Near industry but not classified above + low FRP → Mining/Thermal
    remaining_near = (
        near_industry &
        ~gas_flare_mask &
        ~industrial_fire_mask &
        ~mining_mask &
        (hotspots["frp"] < FRP_INDUSTRIAL_THRESHOLD)
    )
    hotspots.loc[remaining_near, "ml_label"] = LABELS["mining_thermal"]
    logger.info(f"  Mining/Thermal (low FRP near industry): {remaining_near.sum():,}")
    
    # Step 3: Not near industry → check other factors
    not_near = conf_mask & ~near_industry
    
    # 3a: Spatial spread + cluster → Forest Fire
    # High cluster size suggests spreading fire
    forest_fire_mask = (
        not_near &
        (hotspots["spatial_cluster_size"] >= 5) &
        (hotspots["spread_rate"] > 0.01) &  # Some spatial expansion
        ~hotspots["month"].isin(AGRI_BURN_MONTHS)  # Not in burn season
    )
    hotspots.loc[forest_fire_mask, "ml_label"] = LABELS["forest_fire"]
    logger.info(f"  Forest Fire (spread + cluster): {forest_fire_mask.sum():,}")
    
    # 3b: Seasonal cropland burning → Agricultural Burn
    agri_burn_mask = (
        not_near &
        ~forest_fire_mask &
        hotspots["month"].isin(AGRI_BURN_MONTHS) &
        (hotspots["frp"] < FRP_URBAN_THRESHOLD) &  # Low FRP typical of stubble
        (hotspots["persistence_hours"] < PERSISTENCE_THRESHOLD_HOURS)  # Short-lived
    )
    hotspots.loc[agri_burn_mask, "ml_label"] = LABELS["agricultural_burn"]
    logger.info(f"  Agricultural Burn (seasonal, low FRP): {agri_burn_mask.sum():,}")
    
    # 3c: Not near industry, high FRP → Possible Industrial Fire
    urban_fire_mask = (
        not_near &
        ~forest_fire_mask &
        ~agri_burn_mask &
        (hotspots["frp"] >= FRP_URBAN_THRESHOLD) &
        (hotspots["land_cover_class"].isin(["Industrial", "Urban"]))
    )
    hotspots.loc[urban_fire_mask, "ml_label"] = LABELS["industrial_fire"]
    logger.info(f"  Industrial Fire (urban, high FRP): {urban_fire_mask.sum():,}")
    
    # Step 4: VIIRS Nightfire cross-reference
    if not flares.empty:
        logger.info("  Cross-referencing with known gas flare locations...")
        from sklearn.neighbors import BallTree
        
        unclassified_mask = hotspots["ml_label"] == LABELS["unclassified"]
        unclass_idx = hotspots.index[unclassified_mask]
        
        flare_check_count = 0
        if len(unclass_idx) > 0:
            flares_rad = np.radians(flares[["lat", "lon"]].values)
            unclass_rad = np.radians(hotspots.loc[unclass_idx, ["latitude", "longitude"]].values)
            
            tree = BallTree(flares_rad, metric="haversine")
            radius_rad = 5.0 / 6371.0
            
            counts = tree.query_radius(unclass_rad, r=radius_rad, count_only=True)
            matched_indices = unclass_idx[counts > 0]
            
            hotspots.loc[matched_indices, "ml_label"] = LABELS["gas_flare"]
            flare_check_count = len(matched_indices)
            
        logger.info(f"  Nightfire-matched Gas Flares: {flare_check_count:,}")
    
    # Summary
    label_counts = hotspots["ml_label"].value_counts().sort_index()
    logger.info("=" * 40)
    logger.info("LABELING SUMMARY")
    label_names = {v: k for k, v in LABELS.items()}
    for label_id, count in label_counts.items():
        name = label_names.get(label_id, "unknown")
        pct = 100 * count / n
        logger.info(f"  {label_id} ({name}): {count:,} ({pct:.1f}%)")
    logger.info("=" * 40)
    
    return hotspots


def balance_dataset(
    hotspots: pd.DataFrame,
    target_minority: int = 3000,
    target_majority: int = 5000,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Balance the dataset for ML training.
    
    Strategy (user decision: "do the best"):
    - Undersample Unclassified (label 5) to target_majority
    - Undersample other majority classes if needed
    - Keep all minority class samples
    - Final balancing via SMOTE will be done during training
    """
    logger.info("Balancing dataset for training...")
    
    balanced_dfs = []
    label_counts = hotspots["ml_label"].value_counts().sort_index()
    label_names = {v: k for k, v in LABELS.items()}
    
    for label_id, count in label_counts.items():
        name = label_names.get(label_id, "unknown")
        subset = hotspots[hotspots["ml_label"] == label_id]
        
        if label_id == LABELS["unclassified"]:
            # Heavily undersample unclassified
            if count > target_majority:
                subset = subset.sample(n=target_majority, random_state=random_state)
                logger.info(f"  {name}: {count:,} → {target_majority:,} (undersampled)")
            else:
                logger.info(f"  {name}: {count:,} (kept all)")
        else:
            # Keep all minority class samples
            logger.info(f"  {name}: {count:,} (kept all)")
        
        balanced_dfs.append(subset)
    
    balanced = pd.concat(balanced_dfs, ignore_index=True)
    balanced = balanced.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    logger.info(f"  Balanced dataset: {len(balanced):,} records")
    
    return balanced


def extract_ml_features(hotspots: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the final 16 ML features + label for training.
    Matches §5.3 feature specification exactly.
    """
    feature_cols = [
        "latitude",             # For reference (not used as feature)
        "longitude",            # For reference (not used as feature)
        "brightness",           # Feature #1
        "frp",                  # Feature #2
        "confidence",           # Feature #3
        "daynight",             # Feature #4
        "pixel_area",           # Feature #5
        "dist_to_industry_m",   # Feature #6
        "industrial_type",      # Feature #7
        "land_cover_class",     # Feature #8
        "persistence_hours",    # Feature #9
        "recurrence_count",     # Feature #10
        "spatial_cluster_size", # Feature #11
        "spread_rate",          # Feature #12
        "month",                # Feature #13
        "hour",                 # Feature #14
        "bright_t31",           # Feature #15
        "brightness_ratio",     # Feature #16
        "ml_label",             # Target
    ]
    
    available = [c for c in feature_cols if c in hotspots.columns]
    missing = [c for c in feature_cols if c not in hotspots.columns]
    
    if missing:
        logger.warning(f"  Missing columns: {missing}")
    
    return hotspots[available].copy()


def run_labeling_pipeline(
    enriched_csv_path: str,
    flare_csv_path: str,
    output_full_path: str,
    output_training_path: str,
) -> pd.DataFrame:
    """
    Full labeling pipeline: load enriched data → apply rules → balance → save.
    """
    logger.info("=" * 60)
    logger.info("SEMI-SUPERVISED LABELING PIPELINE")
    logger.info("=" * 60)
    
    # Load enriched data
    logger.info(f"Loading enriched data from {os.path.basename(enriched_csv_path)}...")
    hotspots = pd.read_csv(enriched_csv_path, low_memory=False)
    logger.info(f"  Loaded {len(hotspots):,} records")
    
    # Load known flares
    flares = load_known_flares(flare_csv_path)
    
    # Apply classification rules
    hotspots = apply_classification_rules(hotspots, flares)
    
    # Save full labeled dataset
    os.makedirs(os.path.dirname(output_full_path), exist_ok=True)
    hotspots.to_csv(output_full_path, index=False)
    logger.info(f"  Full labeled data saved: {output_full_path}")
    
    # Balance for training
    balanced = balance_dataset(hotspots)
    
    # Extract ML features
    training_data = extract_ml_features(balanced)
    
    # Save training dataset
    training_data.to_csv(output_training_path, index=False)
    size_mb = os.path.getsize(output_training_path) / (1024 * 1024)
    logger.info(f"  Training dataset saved: {output_training_path} ({size_mb:.1f} MB)")
    logger.info(f"  Training records: {len(training_data):,}")
    
    # Final label distribution
    logger.info("FINAL TRAINING LABEL DISTRIBUTION:")
    label_names = {v: k for k, v in LABELS.items()}
    for label_id, count in training_data["ml_label"].value_counts().sort_index().items():
        name = label_names.get(label_id, "unknown")
        pct = 100 * count / len(training_data)
        logger.info(f"  {label_id} ({name}): {count:,} ({pct:.1f}%)")
    
    return training_data


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    data_dir = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\suraj\Desktop\NASA-FIRMS\data"
    
    enriched_csv = os.path.join(data_dir, "processed", "firms_enriched.csv")
    flare_csv = os.path.join(data_dir, "nightfire", "india_known_flares_reference.csv")
    output_full = os.path.join(data_dir, "processed", "firms_labeled_full.csv")
    output_training = os.path.join(data_dir, "processed", "ignis_training_data.csv")
    
    if not os.path.exists(enriched_csv):
        print(f"ERROR: Enriched data not found at {enriched_csv}")
        print("Run spatial_enrichment.py first!")
        sys.exit(1)
    
    df = run_labeling_pipeline(enriched_csv, flare_csv, output_full, output_training)
    print(f"\nDone! {len(df):,} training records saved")
