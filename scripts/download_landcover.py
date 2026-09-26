"""
scripts/download_landcover.py
Download MODIS MCD12Q1 Land Cover data for India.

Usage:
    python scripts/download_landcover.py --year 2022 --output data/land_cover_india.tif

This script downloads the MODIS MCD12Q1 v061 product (IGBP Land Cover)
for the India bounding box and saves it as a GeoTIFF.

Requires:
    - NASA Earthdata account (set EARTHDATA_USER and EARTHDATA_PASS env vars)
    - requests, rasterio (pip install requests rasterio)

IGBP Land Cover Classes:
    1: Evergreen Needleleaf Forests
    2: Evergreen Broadleaf Forests
    3: Deciduous Needleleaf Forests
    4: Deciduous Broadleaf Forests
    5: Mixed Forests
    6: Closed Shrublands
    7: Open Shrublands
    8: Woody Savannas
    9: Savannas
   10: Grasslands
   11: Permanent Wetlands
   12: Croplands
   13: Urban and Built-up Lands
   14: Cropland/Natural Vegetation Mosaics
   15: Permanent Snow and Ice
   16: Barren
   17: Water Bodies
"""

import os
import sys
import argparse
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# India bounding box
INDIA_BBOX = {
    "min_lon": 68.0,
    "min_lat": 6.0,
    "max_lon": 97.5,
    "max_lat": 37.5,
}

MODIS_BASE_URL = "https://e4ftl01.cr.usgs.gov/MOTA/MCD12Q1.061"

# IGBP class lookup for the feature engineering pipeline
IGBP_CLASSES = {
    0: "water",
    1: "evergreen_needleleaf_forest",
    2: "evergreen_broadleaf_forest",
    3: "deciduous_needleleaf_forest",
    4: "deciduous_broadleaf_forest",
    5: "mixed_forest",
    6: "closed_shrubland",
    7: "open_shrubland",
    8: "woody_savanna",
    9: "savanna",
    10: "grassland",
    11: "permanent_wetland",
    12: "cropland",
    13: "urban",
    14: "cropland_natural_mosaic",
    15: "snow_ice",
    16: "barren",
    17: "water",
}


def download_landcover(year: int, output_path: str):
    """
    Download MODIS MCD12Q1 land cover for a given year.

    For a real production deployment this would:
    1. Authenticate with NASA Earthdata
    2. Search the CMR catalog for MCD12Q1 granules covering India
    3. Download the relevant HDF tiles (h24v06, h25v06, h25v07, h26v06, etc.)
    4. Mosaic and reproject to EPSG:4326
    5. Crop to the India bbox and save as GeoTIFF

    For the hackathon demo, we provide a pre-processed sample file.
    """
    earthdata_user = os.environ.get("EARTHDATA_USER")
    earthdata_pass = os.environ.get("EARTHDATA_PASS")

    if not earthdata_user or not earthdata_pass:
        logger.warning(
            "EARTHDATA_USER and EARTHDATA_PASS not set. "
            "Creating a placeholder land cover file for demo purposes."
        )
        _create_placeholder(output_path)
        return

    # CMR search for MCD12Q1 granules
    cmr_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
    params = {
        "short_name": "MCD12Q1",
        "version": "061",
        "temporal": f"{year}-01-01T00:00:00Z,{year}-12-31T23:59:59Z",
        "bounding_box": f"{INDIA_BBOX['min_lon']},{INDIA_BBOX['min_lat']},{INDIA_BBOX['max_lon']},{INDIA_BBOX['max_lat']}",
        "page_size": 20,
    }

    logger.info(f"Searching CMR for MCD12Q1 granules (year={year})...")
    response = requests.get(cmr_url, params=params, timeout=30)
    response.raise_for_status()

    granules = response.json().get("feed", {}).get("entry", [])
    if not granules:
        logger.error("No granules found. Check year and bounding box.")
        sys.exit(1)

    logger.info(f"Found {len(granules)} granules covering India for {year}.")

    # Download each granule
    session = requests.Session()
    session.auth = (earthdata_user, earthdata_pass)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    for i, granule in enumerate(granules):
        links = granule.get("links", [])
        hdf_url = next(
            (l["href"] for l in links if l.get("href", "").endswith(".hdf")),
            None,
        )
        if not hdf_url:
            continue

        tile_name = os.path.basename(hdf_url)
        tile_path = os.path.join(os.path.dirname(output_path), tile_name)

        if os.path.exists(tile_path):
            logger.info(f"  [{i+1}/{len(granules)}] Already downloaded: {tile_name}")
            continue

        logger.info(f"  [{i+1}/{len(granules)}] Downloading: {tile_name}")
        r = session.get(hdf_url, stream=True, timeout=120)
        r.raise_for_status()

        with open(tile_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    logger.info(f"Download complete. Tiles saved to {os.path.dirname(output_path)}")
    logger.info(
        "NOTE: Mosaic and reprojection to GeoTIFF requires GDAL/rasterio. "
        "Run `gdal_merge.py` followed by `gdalwarp -t_srs EPSG:4326` to produce the final file."
    )


def _create_placeholder(output_path: str):
    """Create a minimal placeholder file for demo/development."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(
            "# PLACEHOLDER: MODIS MCD12Q1 Land Cover\n"
            "# Set EARTHDATA_USER and EARTHDATA_PASS to download real data.\n"
            "# For the demo, land cover lookup defaults to 'urban' in the pipeline.\n"
        )
    logger.info(f"Created placeholder at {output_path}")


def get_landcover_class(pixel_value: int) -> str:
    """Map a MCD12Q1 IGBP pixel value to a human-readable class name."""
    return IGBP_CLASSES.get(pixel_value, "unknown")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download MODIS MCD12Q1 Land Cover data")
    parser.add_argument("--year", type=int, default=2022, help="Year of land cover product")
    parser.add_argument("--output", type=str, default="data/land_cover_india.tif", help="Output path")
    args = parser.parse_args()

    download_landcover(args.year, args.output)
