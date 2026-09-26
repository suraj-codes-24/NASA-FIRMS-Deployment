"""
IGNIS — Seed Historical Hotspots into Database

Loads a sample of historical FIRMS data from data/firms/ CSVs
into the hotspots table for demonstration and testing.

Usage:
    python scripts/seed_hotspots.py [--limit 5000]
"""

import sys
import os
import argparse
import datetime

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from geoalchemy2.elements import WKTElement
from app.database import SyncSessionLocal
from app.models.spatial import Hotspot, MLClassificationEnum
from app.ml.features import harmonize_modis_viirs

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "firms")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000, help="Max records to seed")
    args = parser.parse_args()

    csvs = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if not csvs:
        print(f"❌ No CSV files found in {DATA_DIR}")
        return

    print(f"📂 Loading from {len(csvs)} CSV file(s) in {DATA_DIR}...")
    frames = []
    for csv_file in csvs[:2]:  # Load max 2 files for speed
        path = os.path.join(DATA_DIR, csv_file)
        df = pd.read_csv(path, nrows=args.limit)
        df = harmonize_modis_viirs(df)
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True).head(args.limit)
    print(f"   Loaded {len(combined)} records.")

    with SyncSessionLocal() as db:
        inserted = 0
        for _, row in combined.iterrows():
            lat = float(row.get("latitude", 0))
            lon = float(row.get("longitude", 0))
            if lat == 0 or lon == 0:
                continue

            acq_date_str = str(row.get("acq_date", "2026-01-01"))
            acq_time_str = str(row.get("acq_time", "0000")).zfill(4)
            try:
                acq_dt = datetime.datetime.strptime(f"{acq_date_str} {acq_time_str}", "%Y-%m-%d %H%M")
            except Exception:
                acq_dt = datetime.datetime.utcnow()

            hotspot = Hotspot(
                latitude=lat,
                longitude=lon,
                geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
                brightness=float(row.get("brightness", 0)),
                bright_t31=float(row.get("bright_t31", 0)),
                frp=float(row.get("frp", 0)),
                confidence=float(row.get("confidence", 50)),
                satellite=str(row.get("satellite", "Unknown")),
                instrument=str(row.get("instrument", "Unknown")),
                daynight=str(row.get("daynight", "D")),
                pixel_area=1.0,
                acq_date=acq_dt,
                ml_label=MLClassificationEnum.UNCLASSIFIED,
            )
            db.add(hotspot)
            inserted += 1

        db.commit()

    print(f"✅ Inserted {inserted} hotspots.")


if __name__ == "__main__":
    main()
