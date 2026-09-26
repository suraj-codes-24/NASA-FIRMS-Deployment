"""
IGNIS — Geospatial Utilities

Coordinate validation, distance calculations, and CRS helpers.
All distance calculations use geographic (not planar) coordinates.
"""

import math
from typing import Tuple, Optional

from app.utils.constants import INDIA_BBOX


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate that coordinates are within valid geographic bounds.
    
    Args:
        lat: Latitude in degrees (-90 to 90)
        lon: Longitude in degrees (-180 to 180)
    
    Returns:
        True if coordinates are valid
    """
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def is_within_india(lat: float, lon: float) -> bool:
    """
    Check if coordinates fall within India's bounding box.
    
    Bounding box: 68.0°E, 6.0°N to 97.5°E, 37.5°N
    """
    min_lon, min_lat, max_lon, max_lat = INDIA_BBOX
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def haversine_distance_km(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points using the
    Haversine formula. Uses geographic coordinates (WGS84).
    
    Args:
        lat1, lon1: First point (degrees)
        lat2, lon2: Second point (degrees)
    
    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth's mean radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def format_bbox_for_firms(bbox: Tuple[float, float, float, float]) -> str:
    """
    Format bounding box for NASA FIRMS API call.
    FIRMS expects: min_lon,min_lat,max_lon,max_lat
    """
    return ",".join(str(x) for x in bbox)


def snap_to_grid(lat: float, lon: float, grid_size: float = 0.01) -> Tuple[float, float]:
    """
    Snap coordinates to a grid (for persistence grouping).
    Matches PostGIS ST_SnapToGrid behavior.
    
    Args:
        lat, lon: Coordinates
        grid_size: Grid cell size in degrees (default 0.01 ≈ ~1km)
    
    Returns:
        Snapped (lat, lon) tuple
    """
    snapped_lat = round(lat / grid_size) * grid_size
    snapped_lon = round(lon / grid_size) * grid_size
    return (round(snapped_lat, 6), round(snapped_lon, 6))


# Convenience aliases
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Alias for haversine_distance_km."""
    return haversine_distance_km(lat1, lon1, lat2, lon2)


def point_in_bbox(
    lat: float, lon: float,
    min_lon: float, min_lat: float, max_lon: float, max_lat: float
) -> bool:
    """Check if a point falls within a bounding box."""
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
