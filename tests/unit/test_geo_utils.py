"""
Unit tests for backend/app/utils/geo_utils.py
"""
import pytest


def test_haversine_distance_zero():
    """Same point should yield distance ≈ 0."""
    from app.utils.geo_utils import haversine_distance
    d = haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
    assert d < 0.01, "Same coordinates should be ~0 km apart"


def test_haversine_distance_known():
    """Delhi to Mumbai ≈ 1150 km."""
    from app.utils.geo_utils import haversine_distance
    d = haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
    assert 1100 < d < 1200, f"Delhi-Mumbai should be ~1150km, got {d:.0f}km"


def test_point_in_bbox():
    """Point within India bbox should return True."""
    from app.utils.geo_utils import point_in_bbox
    # Mumbai
    assert point_in_bbox(19.07, 72.87, 68.0, 6.0, 97.5, 37.5) is True
    # Outside India (London)
    assert point_in_bbox(51.5, -0.12, 68.0, 6.0, 97.5, 37.5) is False
