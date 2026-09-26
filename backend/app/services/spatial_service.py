"""
IGNIS — Spatial Query Service

Provides PostGIS-powered spatial operations:
- Find nearest industrial facility to a hotspot
- Spatial join (hotspots within buffer of facilities)
- Clustering analysis
"""

import logging
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from app.models.spatial import Hotspot, Facility

logger = logging.getLogger("ignis.services.spatial")


def find_nearest_facility(db: Session, lat: float, lon: float, limit: int = 1):
    """Find the nearest facility to a given coordinate using PostGIS distance."""
    point = WKTElement(f"POINT({lon} {lat})", srid=4326)
    query = (
        select(Facility)
        .order_by(Facility.geom.distance_centroid(point))
        .limit(limit)
    )
    return db.execute(query).scalars().first()


def enrich_hotspot_with_facility(db: Session, hotspot: Hotspot):
    """Set nearest_facility_id and dist_to_industry_m on a hotspot."""
    nearest = find_nearest_facility(db, hotspot.latitude, hotspot.longitude)
    if nearest:
        hotspot.nearest_facility_id = nearest.id
        from app.utils.geo_utils import haversine_distance_km
        from sqlalchemy import func
        # Extract facility coordinates and compute distance
        fac_point = db.execute(
            func.ST_Y(nearest.geom), func.ST_X(nearest.geom)
        ).first()
        if fac_point:
            hotspot.dist_to_industry_m = haversine_distance_km(
                hotspot.latitude, hotspot.longitude,
                fac_point[0], fac_point[1]
            ) * 1000.0  # Convert km → meters
        else:
            hotspot.dist_to_industry_m = 0.0
    else:
        hotspot.dist_to_industry_m = 99999.0
    return hotspot


def get_hotspots_near_facility(db: Session, facility_id: int, radius_m: float = 2000):
    """Return hotspots within `radius_m` meters of a facility using ST_DWithin."""
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        return []
    query = (
        select(Hotspot)
        .where(func.ST_DWithin(Hotspot.geom, facility.geom, radius_m))
    )
    return db.execute(query).scalars().all()


def get_facilities_in_bbox(db: Session, min_lon: float, min_lat: float,
                           max_lon: float, max_lat: float):
    """Return all facilities within a bounding box."""
    bbox_wkt = (
        f"POLYGON(({min_lon} {min_lat}, {max_lon} {min_lat}, "
        f"{max_lon} {max_lat}, {min_lon} {max_lat}, {min_lon} {min_lat}))"
    )
    bbox = WKTElement(bbox_wkt, srid=4326)
    query = select(Facility).where(func.ST_Within(Facility.geom, bbox))
    return db.execute(query).scalars().all()
