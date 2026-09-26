import pandas as pd
import requests
import time

def ingest_test_data():
    csv_path = "data/processed/ignis_training_data.csv"
    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Take a small sample to test
    sample = df.sample(10)
    
    hotspots_payload = []
    for _, row in sample.iterrows():
        hotspots_payload.append({
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "brightness": float(row["brightness"]),
            "bright_t31": float(row["bright_t31"]),
            "frp": float(row["frp"]),
            "confidence": float(row["confidence"]),
            "satellite": "VIIRS-SNPP",
            "instrument": "VIIRS",
            "daynight": str(row["daynight"]),
            "pixel_area": float(row["pixel_area"]) if "pixel_area" in row and not pd.isna(row["pixel_area"]) else 1.0,
            "acq_date": "2023-01-01T12:00:00Z" # Dummy date for test
        })
        
    print(f"Sending {len(hotspots_payload)} hotspots to API...")
    resp = requests.post("http://localhost:8000/api/v1/hotspots/ingest", json=hotspots_payload)
    print("Response:", resp.status_code, resp.json())
    
    print("Waiting for Celery worker to process...")
    time.sleep(3)
    
    print("Fetching ingested hotspots...")
    resp = requests.get("http://localhost:8000/api/v1/hotspots?limit=10")
    data = resp.json()
    for h in data:
        print(f"Hotspot ID {h['id']}: Classified as {h['ml_label']} (Conf: {h['classification_confidence']}%)")

if __name__ == "__main__":
    ingest_test_data()
