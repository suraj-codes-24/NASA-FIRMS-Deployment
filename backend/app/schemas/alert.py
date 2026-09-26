"""
Alert-specific Pydantic schemas.
"""
from app.schemas.spatial import (
    AlertBase,
    AlertResponse,
    AlertUpdate,
)

__all__ = ["AlertBase", "AlertResponse", "AlertUpdate"]
