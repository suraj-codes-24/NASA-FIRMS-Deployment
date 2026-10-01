import sys
import os
import datetime

# Add backend dir to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SyncSessionLocal
from app.models.spatial import Hotspot, Alert, Facility, MLClassificationEnum
from geoalchemy2.elements import WKTElement

def seed_demo_alerts():
    print("Seeding demo alerts...")
    with SyncSessionLocal() as db:
        # Create a dummy facility
        facility = Facility(
            name="Demo Steel Plant",
            facility_type="metal_smelting",
            geom=WKTElement("POINT(86.2 22.8)", srid=4326),
            state="Jharkhand",
            district="Singhbhum"
        )
        db.add(facility)
        db.flush()

        # Create a hotspot classified as Industrial Fire
        hotspot = Hotspot(
            latitude=22.805,
            longitude=86.205,
            geom=WKTElement("POINT(86.205 22.805)", srid=4326),
            brightness=350.5,
            bright_t31=310.0,
            frp=250.0,  # High FRP
            confidence=100.0,
            satellite="Terra",
            instrument="MODIS",
            daynight="D",
            acq_date=datetime.datetime.utcnow(),
            ml_label=MLClassificationEnum.INDUSTRIAL_FIRE,
            classification_confidence=98.5,
            nearest_facility_id=facility.id,
            dist_to_industry_m=500.0
        )
        db.add(hotspot)
        db.flush()

        # Create an alert for it
        alert = Alert(
            hotspot_id=hotspot.id,
            severity="CRITICAL",
            status="NEW",
            description="High-intensity thermal anomaly detected near Demo Steel Plant. Probable unrecorded flare or accident.",
            created_at=datetime.datetime.utcnow()
        )
        db.add(alert)
        
        # Another one
        hotspot2 = Hotspot(
            latitude=23.7,
            longitude=86.4,
            geom=WKTElement("POINT(86.4 23.7)", srid=4326),
            brightness=340.0,
            bright_t31=300.0,
            frp=150.0,
            confidence=90.0,
            satellite="N",
            instrument="VIIRS",
            daynight="N",
            acq_date=datetime.datetime.utcnow(),
            ml_label=MLClassificationEnum.INDUSTRIAL_FIRE,
            classification_confidence=92.0,
            nearest_facility_id=facility.id,
            dist_to_industry_m=2000.0
        )
        db.add(hotspot2)
        db.flush()

        alert2 = Alert(
            hotspot_id=hotspot2.id,
            severity="HIGH",
            status="INVESTIGATING",
            description="Anomalous night-time thermal signature near industrial zone.",
            created_at=datetime.datetime.utcnow()
        )
        db.add(alert2)

        db.commit()
        print("Done seeding demo alerts!")

if __name__ == "__main__":
    seed_demo_alerts()
