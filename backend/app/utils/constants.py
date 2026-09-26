"""
IGNIS — Constants and Enumerations

Fire classification types, color codes, and system-wide constants.
"""

from enum import Enum


class FireType(str, Enum):
    """Classification categories for thermal hotspots."""
    INDUSTRIAL_FIRE = "industrial_fire"
    FOREST_FIRE = "forest_fire"
    GAS_FLARE = "gas_flare"
    AGRICULTURAL_BURN = "agricultural_burn"
    MINING_THERMAL = "mining_thermal"
    UNCLASSIFIED = "unclassified"


# Mapping from numeric label to FireType
LABEL_TO_FIRETYPE = {
    0: FireType.INDUSTRIAL_FIRE,
    1: FireType.FOREST_FIRE,
    2: FireType.GAS_FLARE,
    3: FireType.AGRICULTURAL_BURN,
    4: FireType.MINING_THERMAL,
    5: FireType.UNCLASSIFIED,
}

FIRETYPE_TO_LABEL = {v: k for k, v in LABEL_TO_FIRETYPE.items()}

# Color codes for each classification (matching §3.2 and §9.4)
FIRE_COLORS = {
    FireType.INDUSTRIAL_FIRE: "#e74c3c",     # Red
    FireType.FOREST_FIRE: "#e67e22",         # Orange
    FireType.GAS_FLARE: "#f1c40f",           # Yellow
    FireType.AGRICULTURAL_BURN: "#2ecc71",    # Green
    FireType.MINING_THERMAL: "#3498db",       # Blue
    FireType.UNCLASSIFIED: "#95a5a6",         # Grey
}

# Alert severity levels
class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Alert status lifecycle
class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    AUTO_RESOLVED = "auto_resolved"

# User roles
class UserRole(str, Enum):
    ADMIN = "admin"
    VIEWER = "viewer"

# VIIRS confidence mapping (categorical → numeric)
VIIRS_CONFIDENCE_MAP = {
    "l": 30,    # low
    "n": 50,    # nominal
    "h": 90,    # high
}

# FIRMS column name harmonization
MODIS_TO_UNIFIED = {
    "brightness": "brightness",
    "bright_t31": "bright_t31",
}

VIIRS_TO_UNIFIED = {
    "bright_ti4": "brightness",
    "bright_ti5": "bright_t31",
}

# India bounding box (min_lon, min_lat, max_lon, max_lat)
INDIA_BBOX = (68.0, 6.0, 97.5, 37.5)

# Spatial thresholds
INDUSTRIAL_PROXIMITY_KM = 2.0       # §3.3: "Within 2km of OSM Industrial Facility"
PERSISTENCE_THRESHOLD_HOURS = 48.0  # §3.3: "Persistent > 48hrs"
FRP_INDUSTRIAL_THRESHOLD = 100.0    # §3.3: "FRP > 100 MW"
FRP_URBAN_THRESHOLD = 50.0          # §3.3: "FRP > 50 MW"
CLUSTER_RADIUS_KM = 5.0             # §5.3: "Number of hotspots within 5km radius"
RECURRENCE_WINDOW_DAYS = 30         # §5.3: "detections at same location (±1km) in 30 days"
RECURRENCE_RADIUS_KM = 1.0          # §5.3: "±1km"

# Agricultural burn seasons (Indian context)
AGRI_BURN_MONTHS_RABI = [10, 11, 12]   # Oct-Dec (post-Kharif stubble burning)
AGRI_BURN_MONTHS_ZAID = [4, 5]          # Apr-May (post-Rabi)

# IGBP Land Cover Classes (MCD12Q1)
IGBP_CLASSES = {
    1: "Evergreen Needleleaf Forest",
    2: "Evergreen Broadleaf Forest",
    3: "Deciduous Needleleaf Forest",
    4: "Deciduous Broadleaf Forest",
    5: "Mixed Forest",
    6: "Closed Shrubland",
    7: "Open Shrubland",
    8: "Woody Savanna",
    9: "Savanna",
    10: "Grassland",
    11: "Permanent Wetland",
    12: "Cropland",
    13: "Urban and Built-Up",
    14: "Cropland/Natural Vegetation Mosaic",
    15: "Snow and Ice",
    16: "Barren or Sparsely Vegetated",
    17: "Water",
}

# Simplified land cover groups for classification
FOREST_CLASSES = {1, 2, 3, 4, 5, 8, 9}
CROPLAND_CLASSES = {12, 14}
URBAN_CLASSES = {13}
