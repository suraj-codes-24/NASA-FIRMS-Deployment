"""
IGNIS — OSM Overpass Service

Fetches industrial facility data from OpenStreetMap (OSM) via the Overpass API.
Used to periodically update the spatial database with new industrial infrastructure.
"""

import logging
import requests
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.models.spatial import Facility

logger = logging.getLogger("ignis.services.osm")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def fetch_industrial_facilities(bbox_str: str) -> list[dict]:
    """
    Fetch industrial facilities in a bounding box using OSM Overpass API.
    bbox_str format: "min_lat,min_lon,max_lat,max_lon"
    """
    # Overpass QL query for industrial landuse, power plants, refineries, etc.
    query = f"""
    [out:json][timeout:50];
    (
      way["landuse"="industrial"]({bbox_str});
      node["industrial"="oil_refinery"]({bbox_str});
      way["industrial"="oil_refinery"]({bbox_str});
      node["power"="plant"]({bbox_str});
      way["power"="plant"]({bbox_str});
      node["man_made"="flare"]({bbox_str});
    );
    out center;
    """

    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        facilities = []
        for el in data.get("elements", []):
            lat = el.get("lat") or (el.get("center", {}).get("lat"))
            lon = el.get("lon") or (el.get("center", {}).get("lon"))
            tags = el.get("tags", {})
            
            if lat and lon:
                f_type = "industrial"
                if tags.get("power") == "plant":
                    f_type = "power_plant"
                elif tags.get("industrial") == "oil_refinery":
                    f_type = "oil_refinery"
                elif tags.get("man_made") == "flare":
                    f_type = "gas_flare"
                    
                facilities.append({
                    "osm_id": str(el["id"]),
                    "name": tags.get("name", "Unknown Facility"),
                    "facility_type": f_type,
                    "lat": float(lat),
                    "lon": float(lon)
                })
        
        logger.info(f"Fetched {len(facilities)} facilities from OSM Overpass.")
        return facilities
    except Exception as e:
        logger.error(f"Error fetching from Overpass API: {e}")
        return []


def update_facilities_db(db: Session, facilities: list[dict]) -> int:
    """Insert or update facilities in the database."""
    inserted = 0
    for f in facilities:
        exists = db.query(Facility).filter(Facility.osm_id == f["osm_id"]).first()
        if not exists:
            geom = WKTElement(f"POINT({f['lon']} {f['lat']})", srid=4326)
            new_fac = Facility(
                osm_id=f["osm_id"],
                name=f["name"],
                facility_type=f["facility_type"],
                geom=geom
            )
            db.add(new_fac)
            inserted += 1
            
    if inserted > 0:
        db.commit()
        
    return inserted
