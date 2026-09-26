"""
Unit tests for backend/app/ml/features.py
"""
import pytest
import pandas as pd
import numpy as np


def test_feature_count():
    """The feature engineering pipeline must produce exactly 16 features per §5.3."""
    from app.ml.features import ALL_FEATURE_NAMES
    assert len(ALL_FEATURE_NAMES) >= 16, f"Feature pipeline must produce at least 16 features, got {len(ALL_FEATURE_NAMES)}"


def test_brightness_ratio_computation():
    """brightness_ratio = brightness / bright_t31 should be computed correctly."""
    from app.ml.features import build_feature_matrix

    hotspot_data = {
        "brightness": [400.0],
        "bright_t31": [300.0],
        "frp": [150.0],
        "confidence": [80.0],
        "daynight": ["D"],
        "scan": [1.0],
        "track": [1.0],
        "acq_date": ["2024-06-15T10:00:00"],
        "land_cover_class": ["urban"],
        "dist_to_industry_m": [500.0],
        "industrial_type": ["refinery"],
        "persistence_hours": [24.0],
        "recurrence_count": [5],
        "spatial_cluster_size": [3],
    }
    df = pd.DataFrame(hotspot_data)
    features = build_feature_matrix(df)

    expected = 400.0 / 300.0
    assert abs(features["brightness_ratio"].iloc[0] - expected) < 0.01


def test_pixel_area_calculation():
    """pixel_area = scan × track."""
    from app.ml.features import compute_pixel_area

    df = pd.DataFrame({"scan": [2.0], "track": [1.5]})
    result = compute_pixel_area(df)
    assert abs(result["pixel_area"].iloc[0] - 3.0) < 0.01


def test_time_features_extraction():
    """Month and hour should be extracted from acq_date."""
    from app.ml.features import compute_time_features

    df = pd.DataFrame({"acq_date": ["2024-06-15T14:30:00"]})
    result = compute_time_features(df)
    assert result["month"].iloc[0] == 6
    assert result["hour"].iloc[0] == 14


def test_fill_defaults():
    """Missing enrichment columns should be filled with defaults."""
    from app.ml.features import fill_defaults

    df = pd.DataFrame({"brightness": [350.0]})
    result = fill_defaults(df)
    assert result["dist_to_industry_m"].iloc[0] == 99999.0
    assert result["persistence_hours"].iloc[0] == 0.0
    assert result["industrial_type"].iloc[0] == "unknown"
