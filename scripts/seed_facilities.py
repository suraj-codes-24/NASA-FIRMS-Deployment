"""
IGNIS — Seed OSM Facilities into Database

Loads industrial facilities from data/osm/osm_all_industrial_india.csv
into the facilities table.

Usage (run inside Docker):
    docker exec ignis-backend python /app/scripts/seed_facilities.py
"""

import sys
import os
import csv
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
# Also support running from /app inside Docker
sys.path.insert(0, "/app")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger("seed_facilities")

from geoalchemy2.elements import WKTElement
from app.database import SyncSessionLocal
from app.models.spatial import Facility

# Try multiple possible paths for the CSV
CSV_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "data", "osm", "osm_all_industrial_india.csv"),
    "/data/osm/osm_all_industrial_india.csv",
]


def find_csv():
    for p in CSV_PATHS:
        if os.path.exists(p):
            return p
    return None


def main():
    csv_path = find_csv()
    if not csv_path:
        logger.error(f"OSM CSV not found in any of: {CSV_PATHS}")
        return

    logger.info(f"Loading facilities from {csv_path}...")

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info(f"Found {len(rows)} facility records in CSV.")

    with SyncSessionLocal() as db:
        # Check how many already exist
        existing_count = db.query(Facility).count()
        logger.info(f"Existing facilities in DB: {existing_count}")
        
        if existing_count > 1000:
            logger.info("Database already has >1000 facilities. Skipping seed.")
            return
        
        inserted = 0
        skipped = 0
        
        for row in rows:
            osm_id = row.get("osm_id", "")
            lat_str = row.get("lat", "0")
            lon_str = row.get("lon", "0")
            
            try:
                lat = float(lat_str)
                lon = float(lon_str)
            except ValueError:
                skipped += 1
                continue
                
            if not osm_id or lat == 0 or lon == 0:
                skipped += 1
                continue

            # Filter to India bounding box (approx)
            if not (6.0 <= lat <= 37.5 and 68.0 <= lon <= 97.5):
                skipped += 1
                continue

            facility = Facility(
                osm_id=f"{row.get('osm_type', 'node')}/{osm_id}",
                name=row.get("name", None) or None,
                facility_type=row.get("facility_type", "industrial"),
                geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
                operator=row.get("operator", None) or None,
                source_fuel=row.get("source_fuel", None) or None,
            )
            db.add(facility)
            inserted += 1

            if inserted % 5000 == 0:
                db.flush()
                logger.info(f"  ... inserted {inserted} facilities so far")

        db.commit()

    logger.info(f"DONE! Inserted {inserted} new facilities ({skipped} skipped).")
    
    with SyncSessionLocal() as db:
        total = db.query(Facility).count()
        logger.info(f"Total facilities in database: {total}")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("IGNIS — Industrial Facility Seeder")
    logger.info("=" * 60)
    main()
