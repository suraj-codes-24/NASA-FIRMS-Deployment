"""
IGNIS — Data Preprocessing & Harmonization Pipeline

Phase 1: Cleans, validates, and harmonizes NASA FIRMS data from multiple
sensors (MODIS, VIIRS-SNPP, VIIRS-NOAA20) into a single unified format.

Key operations:
- Harmonize column names (MODIS brightness/bright_t31 ↔ VIIRS bright_ti4/bright_ti5)
- Map VIIRS categorical confidence (l/n/h) → numeric (30/50/90)
- Validate lat/lon within India bounding box
- Remove duplicates
- Add derived columns (pixel_area, source_sensor)
"""

import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger("ignis.preprocessing")

# India bounding box: min_lon, min_lat, max_lon, max_lat
INDIA_BBOX = (68.0, 6.0, 97.5, 37.5)

# VIIRS categorical confidence → numeric mapping (FIRMS standard)
VIIRS_CONFIDENCE_MAP = {"l": 30, "n": 50, "h": 90}

# Unified column schema after harmonization
UNIFIED_COLUMNS = [
    "latitude", "longitude", "brightness", "scan", "track",
    "acq_date", "acq_time", "satellite", "instrument", "confidence",
    "version", "bright_t31", "frp", "daynight", "type", "source_sensor",
    "pixel_area",
]


def load_firms_csv(filepath: str) -> pd.DataFrame:
    """
    Load a single FIRMS CSV file with appropriate dtypes.
    
    Args:
        filepath: Path to the FIRMS CSV file
        
    Returns:
        Raw DataFrame as loaded from CSV
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"FIRMS data file not found: {filepath}")

    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    logger.info(f"Loading {os.path.basename(filepath)} ({size_mb:.1f} MB)...")

    df = pd.read_csv(
        filepath,
        dtype={
            "latitude": float,
            "longitude": float,
            "scan": float,
            "track": float,
            "satellite": str,
            "instrument": str,
            "confidence": str,  # Keep as string initially (VIIRS uses l/n/h)
            "version": str,
            "frp": float,
            "daynight": str,
            "type": str,
        },
        parse_dates=["acq_date"],
        low_memory=False,
    )

    logger.info(f"  Loaded {len(df):,} records, {len(df.columns)} columns")
    return df


def identify_sensor(df: pd.DataFrame, filepath: str) -> str:
    """
    Identify the sensor type from column names and filename.
    
    MODIS uses: brightness, bright_t31
    VIIRS uses: bright_ti4, bright_ti5
    """
    cols = set(df.columns)
    fname = os.path.basename(filepath).lower()

    if "brightness" in cols and "bright_t31" in cols:
        return "MODIS"
    elif "bright_ti4" in cols and "bright_ti5" in cols:
        if "noaa20" in fname or "n20" in fname:
            return "VIIRS-NOAA20"
        else:
            return "VIIRS-SNPP"
    else:
        # Fallback: check filename
        if "modis" in fname:
            return "MODIS"
        elif "noaa20" in fname:
            return "VIIRS-NOAA20"
        else:
            return "VIIRS-SNPP"


def harmonize_columns(df: pd.DataFrame, sensor: str) -> pd.DataFrame:
    """
    Harmonize column names so MODIS and VIIRS data share the same schema.
    
    MODIS columns: brightness, bright_t31
    VIIRS columns: bright_ti4 → brightness, bright_ti5 → bright_t31
    """
    df = df.copy()

    if sensor.startswith("VIIRS"):
        rename_map = {}
        if "bright_ti4" in df.columns:
            rename_map["bright_ti4"] = "brightness"
        if "bright_ti5" in df.columns:
            rename_map["bright_ti5"] = "bright_t31"
        if rename_map:
            df = df.rename(columns=rename_map)
            logger.info(f"  Harmonized VIIRS columns: {rename_map}")

    # Add source sensor column
    df["source_sensor"] = sensor

    return df


def map_confidence_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert confidence values to numeric.
    
    - MODIS confidence is already numeric (0-100)
    - VIIRS confidence is categorical: l=30, n=50, h=90
    """
    df = df.copy()

    def convert_confidence(val):
        if pd.isna(val):
            return 0
        val_str = str(val).strip().lower()
        if val_str in VIIRS_CONFIDENCE_MAP:
            return VIIRS_CONFIDENCE_MAP[val_str]
        try:
            return int(float(val_str))
        except (ValueError, TypeError):
            return 0

    df["confidence"] = df["confidence"].apply(convert_confidence)
    df["confidence"] = df["confidence"].astype(int)

    logger.info(f"  Confidence range: {df['confidence'].min()} - {df['confidence'].max()}")
    return df


def compute_pixel_area(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute pixel area from scan × track dimensions.
    Feature #5 from §5.3: scan × track (spatial extent).
    """
    df = df.copy()
    df["pixel_area"] = df["scan"] * df["track"]
    return df


def validate_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and filter coordinates within India bounding box.
    Removes records with invalid or out-of-bounds coordinates.
    """
    initial_count = len(df)
    min_lon, min_lat, max_lon, max_lat = INDIA_BBOX

    # Remove null coordinates
    df = df.dropna(subset=["latitude", "longitude"])

    # Validate geographic bounds
    valid_geo = (
        (df["latitude"] >= -90) & (df["latitude"] <= 90) &
        (df["longitude"] >= -180) & (df["longitude"] <= 180)
    )
    df = df[valid_geo]

    # Filter to India bounding box
    in_india = (
        (df["latitude"] >= min_lat) & (df["latitude"] <= max_lat) &
        (df["longitude"] >= min_lon) & (df["longitude"] <= max_lon)
    )
    df = df[in_india]

    removed = initial_count - len(df)
    if removed > 0:
        logger.info(f"  Removed {removed:,} records outside India bbox")
    logger.info(f"  Valid records within India: {len(df):,}")

    return df


def validate_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate data quality: remove records with invalid/missing critical fields.
    """
    initial_count = len(df)
    df = df.copy()

    # Remove records with missing critical fields
    critical_cols = ["latitude", "longitude", "brightness", "frp", "acq_date"]
    for col in critical_cols:
        if col in df.columns:
            df = df.dropna(subset=[col])

    # Remove negative FRP values
    if "frp" in df.columns:
        df = df[df["frp"] >= 0]

    # Remove unrealistic brightness temperatures (< 200K or > 600K)
    if "brightness" in df.columns:
        df = df[(df["brightness"] >= 200) & (df["brightness"] <= 600)]

    # Validate daynight is D or N
    if "daynight" in df.columns:
        df["daynight"] = df["daynight"].str.strip().str.upper()
        df = df[df["daynight"].isin(["D", "N"])]

    removed = initial_count - len(df)
    if removed > 0:
        logger.info(f"  Removed {removed:,} records with quality issues")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate detections.
    A duplicate is defined as same lat, lon, acq_date, acq_time, satellite.
    """
    initial_count = len(df)
    dedup_cols = ["latitude", "longitude", "acq_date", "acq_time", "satellite"]
    existing_cols = [c for c in dedup_cols if c in df.columns]

    df = df.drop_duplicates(subset=existing_cols, keep="first")

    removed = initial_count - len(df)
    if removed > 0:
        logger.info(f"  Removed {removed:,} duplicate records")
    logger.info(f"  Final record count: {len(df):,}")

    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract time-based features for ML:
    - month (Feature #13 from §5.3)
    - hour (Feature #14 from §5.3)
    """
    df = df.copy()

    # Ensure acq_date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["acq_date"]):
        df["acq_date"] = pd.to_datetime(df["acq_date"], errors="coerce")

    # Extract month
    df["month"] = df["acq_date"].dt.month

    # Extract hour from acq_time (HHMM format stored as integer)
    df["acq_time"] = pd.to_numeric(df["acq_time"], errors="coerce").fillna(0).astype(int)
    df["hour"] = df["acq_time"] // 100  # HHMM → HH

    # Clamp hour to valid range
    df["hour"] = df["hour"].clip(0, 23)

    return df


def compute_brightness_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute brightness ratio (Feature #16 from §5.3).
    brightness_ratio = brightness / bright_t31
    """
    df = df.copy()

    # Avoid division by zero
    df["brightness_ratio"] = np.where(
        df["bright_t31"] > 0,
        df["brightness"] / df["bright_t31"],
        1.0
    )

    return df


def process_single_file(filepath: str) -> pd.DataFrame:
    """
    Full preprocessing pipeline for a single FIRMS CSV file.
    
    Steps:
    1. Load CSV
    2. Identify sensor type
    3. Harmonize column names
    4. Map confidence to numeric
    5. Validate coordinates (India bbox)
    6. Validate data quality
    7. Compute derived features
    8. Remove duplicates
    """
    logger.info(f"Processing: {os.path.basename(filepath)}")

    # Step 1: Load
    df = load_firms_csv(filepath)

    # Step 2: Identify sensor
    sensor = identify_sensor(df, filepath)
    logger.info(f"  Sensor identified: {sensor}")

    # Step 3: Harmonize columns
    df = harmonize_columns(df, sensor)

    # Step 4: Map confidence
    df = map_confidence_to_numeric(df)

    # Step 5: Validate coordinates
    df = validate_coordinates(df)

    # Step 6: Quality validation
    df = validate_data_quality(df)

    # Step 7: Derived features
    df = compute_pixel_area(df)
    df = add_time_features(df)
    df = compute_brightness_ratio(df)

    # Step 8: Remove duplicates
    df = remove_duplicates(df)

    return df


def preprocess_all_firms_data(
    data_dir: str,
    output_path: Optional[str] = None,
    include_historical: bool = True,
) -> pd.DataFrame:
    """
    Process and merge all FIRMS CSV files from the data directory.
    
    Args:
        data_dir: Path to the directory containing FIRMS CSV files
        output_path: Optional path to save the unified CSV
        include_historical: Whether to include historical data files
        
    Returns:
        Unified, harmonized DataFrame with all FIRMS data
    """
    firms_dir = os.path.join(data_dir, "firms")

    if not os.path.exists(firms_dir):
        raise FileNotFoundError(f"FIRMS directory not found: {firms_dir}")

    # Find all FIRMS CSV files
    csv_files = sorted([
        os.path.join(firms_dir, f)
        for f in os.listdir(firms_dir)
        if f.endswith(".csv")
    ])

    if not include_historical:
        csv_files = [f for f in csv_files if "historical" not in os.path.basename(f).lower()]

    logger.info(f"Found {len(csv_files)} FIRMS CSV files to process")

    # Process each file
    processed_dfs = []
    for filepath in csv_files:
        try:
            df = process_single_file(filepath)
            processed_dfs.append(df)
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")
            continue

    if not processed_dfs:
        raise ValueError("No FIRMS data files were successfully processed")

    # Merge all DataFrames
    logger.info("Merging all processed files...")
    unified = pd.concat(processed_dfs, ignore_index=True)

    # Final deduplication across all files
    logger.info("Final cross-file deduplication...")
    initial = len(unified)
    dedup_cols = ["latitude", "longitude", "acq_date", "acq_time", "satellite"]
    existing_cols = [c for c in dedup_cols if c in unified.columns]
    unified = unified.drop_duplicates(subset=existing_cols, keep="first")
    logger.info(f"  Removed {initial - len(unified):,} cross-file duplicates")

    # Sort by date
    unified = unified.sort_values("acq_date").reset_index(drop=True)

    # Summary
    logger.info("=" * 60)
    logger.info("UNIFIED FIRMS DATA SUMMARY")
    logger.info(f"  Total records: {len(unified):,}")
    logger.info(f"  Date range: {unified['acq_date'].min()} to {unified['acq_date'].max()}")
    logger.info(f"  Sensors: {unified['source_sensor'].value_counts().to_dict()}")
    logger.info(f"  Confidence range: {unified['confidence'].min()} - {unified['confidence'].max()}")
    logger.info(f"  FRP range: {unified['frp'].min():.2f} - {unified['frp'].max():.2f} MW")
    logger.info(f"  Columns: {list(unified.columns)}")
    logger.info("=" * 60)

    # Save if output path provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        unified.to_csv(output_path, index=False)
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"  Saved to: {output_path} ({size_mb:.1f} MB)")

    return unified


# ----- CLI Entry Point -----
if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    data_dir = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\suraj\Desktop\NASA-FIRMS\data"
    output_path = os.path.join(data_dir, "processed", "firms_unified.csv")

    include_hist = "--no-historical" not in sys.argv

    df = preprocess_all_firms_data(
        data_dir=data_dir,
        output_path=output_path,
        include_historical=include_hist,
    )

    print(f"\nDone! {len(df):,} records saved to {output_path}")
