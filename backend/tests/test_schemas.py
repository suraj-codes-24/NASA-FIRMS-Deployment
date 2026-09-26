import pytest
from app.schemas.spatial import HotspotIngest, MLClassificationEnum

def test_hotspot_schema_valid():
    data = {
        "latitude": 28.7041,
        "longitude": 77.1025,
        "brightness": 320.5,
        "satellite": "Terra",
        "acq_date": "2026-09-08",
        "acq_time": "14:30",
        "confidence": 85,
        "bright_t31": 310.2,
        "frp": 12.5,
        "daynight": "D",
        "instrument": "MODIS"
    }
    hotspot = HotspotIngest(**data)
    assert hotspot.latitude == 28.7041
    assert hotspot.instrument == "MODIS"

def test_hotspot_schema_invalid():
    data = {
        "latitude": "invalid_string",
        "longitude": 77.1025
    }
    with pytest.raises(ValueError):
        HotspotIngest(**data)
