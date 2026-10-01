"""
IGNIS — FastAPI Application Configuration (Production/Deployment)

Loads all environment variables via Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ----- Application -----
    app_env: str = "production"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ----- Database (Neon PostgreSQL + PostGIS) -----
    postgres_user: str = "ignis"
    postgres_password: str = ""
    postgres_db: str = "ignis_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str = ""
    database_url_sync: str = ""

    # ----- Security -----
    secret_key: str = "replace-this-with-a-strong-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    # ----- NASA FIRMS -----
    firms_map_key: str = ""
    ingestion_interval_hours: int = 3
    india_bbox: str = "68.0,6.0,97.5,37.5"

    # ----- ML Model (HuggingFace Space) -----
    huggingface_inference_url: str = ""  # e.g., https://<user>-ignis-ml-inference.hf.space/api/predict

    # ----- Alerts -----
    alert_frp_threshold: float = 200.0
    alert_industrial_fire_confidence: float = 0.85

    # ----- CORS -----
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost"

    # ----- Upstash Redis (optional, for caching) -----
    redis_url: str = ""
    upstash_redis_url: str = ""
    upstash_redis_token: str = ""

    # ----- QStash (cron trigger security) -----
    qstash_current_signing_key: str = ""
    qstash_next_signing_key: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def india_bbox_tuple(self) -> tuple:
        """Parse India bounding box as (min_lon, min_lat, max_lon, max_lat)."""
        parts = [float(x.strip()) for x in self.india_bbox.split(",")]
        return tuple(parts)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Singleton settings instance
settings = Settings()
