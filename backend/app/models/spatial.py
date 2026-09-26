import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base
import enum

class MLClassificationEnum(str, enum.Enum):
    INDUSTRIAL_FIRE = "Industrial Fire"
    FOREST_FIRE = "Forest Fire"
    GAS_FLARE = "Gas Flare"
    AGRICULTURAL_BURN = "Agricultural Burn"
    MINING_THERMAL = "Mining/Thermal"
    UNCLASSIFIED = "Unclassified"

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    osm_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    facility_type = Column(String, index=True)  # e.g., 'refinery', 'power_plant'
    geom = Column(Geometry('POINT', srid=4326), nullable=False)
    state = Column(String, nullable=True, index=True)
    district = Column(String, nullable=True)
    operator = Column(String, nullable=True)
    source_fuel = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # Raw OSM tags as JSON
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc),
                          onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

class Hotspot(Base):
    __tablename__ = "hotspots"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=False, index=True)
    
    # Satellite Data
    brightness = Column(Float)
    bright_t31 = Column(Float)
    frp = Column(Float)
    confidence = Column(Float)
    satellite = Column(String, index=True)  # 'MODIS', 'VIIRS-SNPP', 'VIIRS-NOAA20'
    instrument = Column(String)
    daynight = Column(String(1)) # 'D' or 'N'
    scan = Column(Float, nullable=True)
    track = Column(Float, nullable=True)
    pixel_area = Column(Float, nullable=True)
    
    # Time Data
    acq_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Enrichment Data
    land_cover_class = Column(String, nullable=True)
    nearest_facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=True)
    dist_to_industry_m = Column(Float, nullable=True)
    persistence_hours = Column(Float, default=0.0)
    recurrence_count = Column(Integer, default=0)
    spatial_cluster_size = Column(Integer, default=1)
    spread_rate = Column(Float, nullable=True)  # km/hr
    
    # ML Classification
    ml_label = Column(SQLEnum(MLClassificationEnum), default=MLClassificationEnum.UNCLASSIFIED, index=True)
    classification_confidence = Column(Float, nullable=True)
    is_user_verified = Column(Boolean, default=False)
    
    # Relationships
    nearest_facility = relationship("Facility")
    classification_logs = relationship("ClassificationLog", back_populates="hotspot", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="hotspot", cascade="all, delete-orphan")
    verification_logs = relationship("VerificationLog", back_populates="hotspot", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc),
                        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

class ClassificationLog(Base):
    __tablename__ = "classification_logs"

    id = Column(Integer, primary_key=True, index=True)
    hotspot_id = Column(Integer, ForeignKey("hotspots.id"), nullable=False)
    model_version = Column(String, nullable=False)
    predicted_label = Column(SQLEnum(MLClassificationEnum), nullable=False)
    probability_scores = Column(String, nullable=True) # JSON string of probs
    execution_time_ms = Column(Float, nullable=True)
    
    hotspot = relationship("Hotspot", back_populates="classification_logs")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    hotspot_id = Column(Integer, ForeignKey("hotspots.id"), nullable=False)
    alert_type = Column(String, nullable=False) # e.g. "HIGH_FRP_INDUSTRIAL", "NEW_GAS_FLARE"
    severity = Column(String, default="MEDIUM") # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    status = Column(String, default="NEW") # "NEW", "ACKNOWLEDGED", "RESOLVED"
    resolution_note = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    
    hotspot = relationship("Hotspot", back_populates="alerts")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))

class VerificationLog(Base):
    __tablename__ = "verification_logs"

    id = Column(Integer, primary_key=True, index=True)
    hotspot_id = Column(Integer, ForeignKey("hotspots.id"), nullable=False)
    original_label = Column(SQLEnum(MLClassificationEnum), nullable=False)
    verified_label = Column(SQLEnum(MLClassificationEnum), nullable=False)
    user_id = Column(String, nullable=True) # E.g., agent ID or email
    notes = Column(String, nullable=True)
    
    hotspot = relationship("Hotspot", back_populates="verification_logs")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))

class UserAccount(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="viewer")  # "admin" or "viewer"
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))

class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
