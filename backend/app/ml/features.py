"""
IGNIS — ML Feature Engineering Module

Computes the 16 engineered features per hotspot as specified in §5.3 / §8.2:
brightness, frp, confidence, daynight, pixel_area, dist_to_nearest_industrial,
industrial_type, land_cover_class, persistence_hours, recurrence_count,
spatial_cluster_size, spread_rate, month, hour, bright_t31, brightness_ratio
"""

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger("ignis.ml.features")

# Feature names expected by the trained model
FEATURE_NAMES_NUMERIC = [
    "brightness", "frp", "confidence", "pixel_area",
    "dist_to_industry_m", "persistence_hours", "recurrence_count",
    "spatial_cluster_size", "spread_rate", "month", "hour",
    "bright_t31", "brightness_ratio",
]

FEATURE_NAMES_CATEGORICAL = [
    "daynight", "industrial_type", "land_cover_class"
]

ALL_FEATURE_NAMES = FEATURE_NAMES_NUMERIC + FEATURE_NAMES_CATEGORICAL


def harmonize_modis_viirs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Harmonize column differences between MODIS and VIIRS CSV schemas.
    MODIS uses: brightness, bright_t31
    VIIRS uses: bright_ti4, bright_ti5
    """
    if "bright_ti4" in df.columns and "brightness" not in df.columns:
        df["brightness"] = df["bright_ti4"]
    if "bright_ti5" in df.columns and "bright_t31" not in df.columns:
        df["bright_t31"] = df["bright_ti5"]

    # VIIRS confidence is categorical (n/l/h), MODIS is numeric (0-100)
    if "confidence" in df.columns:
        conf_map = {"l": 30.0, "n": 50.0, "h": 90.0}
        df["confidence"] = df["confidence"].apply(
            lambda x: conf_map.get(str(x).strip().lower(), float(x))
            if not str(x).replace(".", "").isdigit()
            else float(x)
        )
    return df


def compute_pixel_area(df: pd.DataFrame) -> pd.DataFrame:
    """Compute pixel area from scan × track if available."""
    if "scan" in df.columns and "track" in df.columns:
        df["pixel_area"] = df["scan"].astype(float) * df["track"].astype(float)
    elif "pixel_area" not in df.columns:
        df["pixel_area"] = 1.0
    return df


def compute_brightness_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """brightness / bright_t31 — higher ratio suggests intense combustion."""
    df["brightness_ratio"] = np.where(
        df["bright_t31"] > 0,
        df["brightness"] / df["bright_t31"],
        1.0,
    )
    return df


def compute_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract month and hour from acquisition datetime."""
    if "acq_date" in df.columns:
        dt = pd.to_datetime(df["acq_date"], errors="coerce")
        df["month"] = dt.dt.month.fillna(1).astype(int)
        if "acq_time" in df.columns:
            time_str = df["acq_time"].astype(str).str.zfill(4)
            df["hour"] = time_str.str[:2].astype(int)
        else:
            df["hour"] = dt.dt.hour.fillna(12).astype(int)
    else:
        df["month"] = 1
        df["hour"] = 12
    return df


def encode_daynight(df: pd.DataFrame) -> pd.DataFrame:
    """Binary encode daynight: D=1, N=0."""
    df["daynight"] = df["daynight"].map({"D": 1, "N": 0}).fillna(0).astype(int)
    return df


def fill_defaults(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing enrichment columns with sensible defaults."""
    defaults = {
        "dist_to_industry_m": 99999.0,
        "industrial_type": "unknown",
        "land_cover_class": "Unknown",
        "persistence_hours": 0.0,
        "recurrence_count": 1,
        "spatial_cluster_size": 1,
        "spread_rate": 0.0,
    }
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val
        else:
            df[col] = df[col].fillna(val)
    return df


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full pipeline: harmonize → compute derived features → fill defaults.
    Returns a DataFrame containing exactly the 16 features.
    """
    df = harmonize_modis_viirs(df)
    df = compute_pixel_area(df)
    df = compute_brightness_ratio(df)
    df = compute_time_features(df)
    df = fill_defaults(df)

    # Ensure all columns exist
    for col in ALL_FEATURE_NAMES:
        if col not in df.columns:
            df[col] = 0 if col in FEATURE_NAMES_NUMERIC else "unknown"

    return df[ALL_FEATURE_NAMES]
