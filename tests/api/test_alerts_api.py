"""
API tests for alert schemas and response models.
"""
import pytest
from app.schemas.spatial import AlertBase, AlertResponse, AlertUpdate
from datetime import datetime


def test_alert_response_schema():
    """AlertResponse should correctly parse from dict."""
    data = AlertResponse(
        id=1,
        hotspot_id=42,
        alert_type="HIGH_FRP_INDUSTRIAL",
        severity="CRITICAL",
        status="NEW",
        is_read=False,
        created_at=datetime(2024, 6, 15, 10, 0, 0),
        resolution_note=None,
    )
    assert data.severity == "CRITICAL"
    assert data.is_read is False


def test_alert_update_schema():
    """AlertUpdate should accept optional resolution_note."""
    update = AlertUpdate(resolution_note="False alarm — confirmed gas flare")
    assert "flare" in update.resolution_note

    empty = AlertUpdate()
    assert empty.resolution_note is None
