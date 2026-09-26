import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from app.models.spatial import MLClassificationEnum

class FacilityBase(BaseModel):
    osm_id: str
    name: Optional[str] = None
    facility_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    state: Optional[str] = None
    district: Optional[str] = None

class FacilityResponse(FacilityBase):
    id: int
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)

class ClassificationLogBase(BaseModel):
    model_version: str
    predicted_label: MLClassificationEnum
    probability_scores: Optional[str] = None
    execution_time_ms: Optional[float] = None

class HotspotIngest(BaseModel):
    latitude: float
    longitude: float
    brightness: float
    bright_t31: float
    frp: float
    confidence: float
    satellite: str
    instrument: str
    daynight: str
    scan: Optional[float] = None
    track: Optional[float] = None
    pixel_area: Optional[float] = None
    acq_date: datetime.datetime

class HotspotResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    brightness: float
    bright_t31: float
    frp: float
    confidence: float
    satellite: str
    instrument: Optional[str] = None
    daynight: Optional[str] = None
    scan: Optional[float] = None
    track: Optional[float] = None
    acq_date: datetime.datetime
    
    # Enriched fields
    land_cover_class: Optional[str] = None
    dist_to_industry_m: Optional[float] = None
    persistence_hours: float = 0.0
    recurrence_count: int = 0
    spatial_cluster_size: int = 1
    spread_rate: Optional[float] = None
    
    # ML fields
    ml_label: MLClassificationEnum
    classification_confidence: Optional[float] = None
    is_user_verified: bool
    
    # Relationships
    nearest_facility_id: Optional[int] = None
    nearest_facility: Optional[FacilityResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    weight: float = 1.0

class HotspotVerifyRequest(BaseModel):
    verified_label: MLClassificationEnum
    user_id: Optional[str] = None
    notes: Optional[str] = None

class VerificationLogResponse(BaseModel):
    id: int
    hotspot_id: int
    original_label: MLClassificationEnum
    verified_label: MLClassificationEnum
    user_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)

class AlertBase(BaseModel):
    hotspot_id: int
    alert_type: str
    severity: str
    status: str
    is_read: bool

class AlertResponse(AlertBase):
    id: int
    created_at: datetime.datetime
    resolution_note: Optional[str] = None
    hotspot: Optional[HotspotResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class AlertUpdate(BaseModel):
    resolution_note: Optional[str] = None

class AnalyticsSummaryResponse(BaseModel):
    total_hotspots: int
    active_industrial_fires: int
    high_severity_alerts: int
    unverified_classifications: int

class ClassificationCount(BaseModel):
    label: MLClassificationEnum
    count: int

class TimelineDataPoint(BaseModel):
    date: str
    count: int

