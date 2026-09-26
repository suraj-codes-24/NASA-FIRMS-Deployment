"""
IGNIS — FIRMS Data Ingestion Service

Handles fetching NASA FIRMS CSV data (MODIS / VIIRS) from the public
API or MAP_KEY-authenticated endpoints, parsing, harmonizing, and
returning clean DataFrames ready for database insertion.
"""

import logging
import io
import requests
import pandas as pd

from app.config import settings
from app.ml.features import harmonize_modis_viirs

logger = logging.getLogger("ignis.services.firms")

PUBLIC_MODIS_URL = (
    "https://firms.modaps.eosdis.nasa.gov/data/active_fire/"
    "modis-c6.1/csv/MODIS_C6_1_South_Asia_24h.csv"
)
PUBLIC_VIIRS_URL = (
    "https://firms.modaps.eosdis.nasa.gov/data/active_fire/"
    "suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_Asia_24h.csv"
)


def _build_urls() -> list[str]:
    """Return the list of NASA FIRMS CSV endpoints to fetch."""
    if settings.firms_map_key:
        bbox = settings.india_bbox
        return [
            f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
            f"{settings.firms_map_key}/VIIRS_SNPP_NRT/{bbox}/1",
            f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
            f"{settings.firms_map_key}/MODIS_NRT/{bbox}/1",
        ]
    logger.warning("No FIRMS_MAP_KEY — using public 24-hr South Asia CSVs.")
    return [PUBLIC_MODIS_URL, PUBLIC_VIIRS_URL]


def fetch_firms_data(timeout: int = 30) -> pd.DataFrame | None:
    """
    Download the latest NASA FIRMS data, harmonize MODIS/VIIRS columns,
    and return a combined DataFrame.
    """
    urls = _build_urls()
    frames: list[pd.DataFrame] = []

    for url in urls:
        try:
            safe_url = url.split(settings.firms_map_key)[0] if settings.firms_map_key else url
            logger.info(f"Fetching: {safe_url}...")
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            if "No fires" in resp.text:
                continue
            df = pd.read_csv(io.StringIO(resp.text))
            df = harmonize_modis_viirs(df)
            frames.append(df)
        except Exception as exc:
            logger.error(f"Error fetching FIRMS data: {exc}")

    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)
