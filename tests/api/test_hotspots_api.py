"""
API tests for hotspots endpoints.
Tests the schema validation layer (does not require a running DB).
"""
import pytest
from app.schemas.spatial import HotspotIngest, HotspotResponse, HeatmapPoint, HotspotVerifyRequest
from app.models.spatial import MLClassificationEnum
from datetime import datetime


def test_hotspot_ingest_schema_valid():
    """A valid HotspotIngest should parse without errors."""
    data = HotspotIngest(
        latitude=19.07,
        longitude=72.87,
        brightness=400.0,
        bright_t31=300.0,
        frp=250.0,
        confidence=95.0,
        satellite="VIIRS",
        instrument="VIIRS",
        daynight="D",
        scan=1.0,
        track=1.0,
        acq_date=datetime(2024, 6, 15, 10, 0, 0),
    )
    assert data.latitude == 19.07
    assert data.scan == 1.0
    assert data.track == 1.0


def test_hotspot_ingest_schema_missing_optional():
    """Optional fields scan, track, pixel_area should default to None."""
    data = HotspotIngest(
        latitude=28.0,
        longitude=77.0,
        brightness=350.0,
        bright_t31=290.0,
        frp=80.0,
        confidence=70.0,
        satellite="MODIS",
        instrument="MODIS",
        daynight="N",
        acq_date=datetime(2024, 1, 10, 22, 0, 0),
    )
    assert data.scan is None
    assert data.track is None
    assert data.pixel_area is None


def test_heatmap_point_schema():
    """HeatmapPoint should have lat, lon, weight."""
    pt = HeatmapPoint(latitude=19.0, longitude=72.8, weight=150.0)
    assert pt.weight == 150.0


def test_verify_request_schema():
    """HotspotVerifyRequest should accept a valid label."""
    req = HotspotVerifyRequest(
        verified_label=MLClassificationEnum.GAS_FLARE,
        user_id="analyst@ntro.gov.in",
        notes="Confirmed persistent gas flare at IOCL refinery",
    )
    assert req.verified_label == MLClassificationEnum.GAS_FLARE
