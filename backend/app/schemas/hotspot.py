"""
Hotspot-specific Pydantic schemas.
Re-exports from the main spatial module for spec directory structure compliance.
"""
from app.schemas.spatial import (
    HotspotIngest,
    HotspotResponse,
    HotspotVerifyRequest,
    HeatmapPoint,
    VerificationLogResponse,
)

__all__ = [
    "HotspotIngest",
    "HotspotResponse",
    "HotspotVerifyRequest",
    "HeatmapPoint",
    "VerificationLogResponse",
]
