"""
IGNIS — Spatial Enrichment & Feature Engineering

Phase 2: Enriches unified FIRMS hotspot data with spatial context:
- Distance to nearest OSM industrial facility (Feature #6)
- Type of nearest facility (Feature #7)  
- Land cover class at hotspot location (Feature #8)
- Persistence hours (Feature #9)
- Recurrence count (Feature #10)
- Spatial cluster size (Feature #11)
- Spread rate (Feature #12)

Uses BallTree for efficient spatial proximity queries against
88,596 OSM industrial facilities.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

logger = logging.getLogger("ignis.spatial")

# Spatial constants from §3.3 and §5.3
INDUSTRIAL_PROXIMITY_M = 2000       # 2km for "near industrial facility"
CLUSTER_RADIUS_KM = 5.0             # §5.3: hotspots within 5km radius
RECURRENCE_RADIUS_KM = 1.0          # §5.3: ±1km for recurrence
RECURRENCE_WINDOW_DAYS = 30         # §5.3: 30-day window
EARTH_RADIUS_KM = 6371.0


def load_osm_facilities(osm_csv_path: str) -> pd.DataFrame:
    """
    Load the consolidated OSM industrial facilities CSV.
    
    Expected columns: osm_id, osm_type, lat, lon, name, facility_type, operator, source_fuel
    """
    logger.info(f"Loading OSM facilities from {os.path.basename(osm_csv_path)}...")
    
    df = pd.read_csv(osm_csv_path, dtype={
        "osm_id": str,
        "osm_type": str,
        "lat": float,
        "lon": float,
        "name": str,
        "facility_type": str,
        "operator": str,
        "source_fuel": str,
    })
    
    # Remove facilities without coordinates
    df = df.dropna(subset=["lat", "lon"])
    
    logger.info(f"  Loaded {len(df):,} facilities")
    logger.info(f"  Facility types: {df['facility_type'].value_counts().head(10).to_dict()}")
    
    return df


def build_facility_tree(facilities: pd.DataFrame) -> Tuple[BallTree, np.ndarray]:
    """
    Build a BallTree index for efficient spatial proximity queries.
    Uses Haversine metric (geographic distance, not planar).
    
    Returns:
        (BallTree, facility_coords_radians)
    """
    logger.info("Building spatial index (BallTree with Haversine)...")
    
    # Convert to radians for Haversine
    coords_rad = np.radians(facilities[["lat", "lon"]].values)
    
    tree = BallTree(coords_rad, metric="haversine")
    
    logger.info(f"  BallTree built with {len(coords_rad):,} facilities")
    return tree, coords_rad


def compute_nearest_facility(
    hotspots: pd.DataFrame,
    facilities: pd.DataFrame,
    tree: BallTree,
) -> pd.DataFrame:
    """
    For each hotspot, find the nearest industrial facility using BallTree.
    
    Computes:
    - dist_to_industry_m: Distance in meters to nearest facility
    - industrial_type: Facility type of the nearest facility
    - is_near_industry: Boolean, within 2km (§3.3)
    """
    logger.info("Computing nearest facility for each hotspot...")
    
    # Hotspot coordinates in radians
    hotspot_coords_rad = np.radians(hotspots[["latitude", "longitude"]].values)
    
    # Query nearest facility
    distances_rad, indices = tree.query(hotspot_coords_rad, k=1)
    
    # Convert Haversine distance (radians) to meters
    distances_m = distances_rad.flatten() * EARTH_RADIUS_KM * 1000
    
    # Get nearest facility info
    nearest_idx = indices.flatten()
    
    hotspots = hotspots.copy()
    hotspots["dist_to_industry_m"] = distances_m
    hotspots["industrial_type"] = facilities.iloc[nearest_idx]["facility_type"].values
    hotspots["is_near_industry"] = distances_m <= INDUSTRIAL_PROXIMITY_M
    
    near_count = hotspots["is_near_industry"].sum()
    logger.info(f"  Hotspots near industry (<2km): {near_count:,} ({100*near_count/len(hotspots):.1f}%)")
    logger.info(f"  Distance range: {distances_m.min():.0f}m - {distances_m.max():.0f}m")
    
    return hotspots


def compute_persistence_hours(hotspots: pd.DataFrame) -> pd.DataFrame:
    """
    Compute how long a location has been persistently active (Feature #9, §5.3).
    
    Groups hotspots by snapped grid location (0.01° ≈ 1km) and computes
    the time span of detections at that location.
    """
    logger.info("Computing persistence hours...")
    
    hotspots = hotspots.copy()
    
    # Snap to grid (0.01° ≈ 1km) for location grouping
    hotspots["grid_lat"] = (hotspots["latitude"] / 0.01).round() * 0.01
    hotspots["grid_lon"] = (hotspots["longitude"] / 0.01).round() * 0.01
    
    # Ensure datetime
    if not pd.api.types.is_datetime64_any_dtype(hotspots["acq_date"]):
        hotspots["acq_date"] = pd.to_datetime(hotspots["acq_date"])
    
    # Group by grid cell, compute time span
    grid_groups = hotspots.groupby(["grid_lat", "grid_lon"])["acq_date"].agg(
        first_seen="min",
        last_seen="max",
        detection_count="count",
    ).reset_index()
    
    grid_groups["persistence_hours"] = (
        (grid_groups["last_seen"] - grid_groups["first_seen"]).dt.total_seconds() / 3600
    )
    
    # Merge back
    hotspots = hotspots.merge(
        grid_groups[["grid_lat", "grid_lon", "persistence_hours"]],
        on=["grid_lat", "grid_lon"],
        how="left",
    )
    
    hotspots["persistence_hours"] = hotspots["persistence_hours"].fillna(0)
    
    # Cleanup temp columns
    hotspots = hotspots.drop(columns=["grid_lat", "grid_lon"])
    
    logger.info(f"  Persistence range: {hotspots['persistence_hours'].min():.1f} - {hotspots['persistence_hours'].max():.1f} hours")
    
    return hotspots


def compute_recurrence_count(hotspots: pd.DataFrame) -> pd.DataFrame:
    """
    Count number of detections at approximately the same location (±1km) 
    within a 30-day window (Feature #10, §5.3).
    """
    logger.info("Computing recurrence counts...")
    
    hotspots = hotspots.copy()
    
    # Use grid snapping for grouping (0.01° ≈ 1km)
    hotspots["grid_lat"] = (hotspots["latitude"] / 0.01).round() * 0.01
    hotspots["grid_lon"] = (hotspots["longitude"] / 0.01).round() * 0.01
    
    if not pd.api.types.is_datetime64_any_dtype(hotspots["acq_date"]):
        hotspots["acq_date"] = pd.to_datetime(hotspots["acq_date"])
    
    # For each hotspot, count detections at same grid cell within 30 days
    # Efficient approach: group by grid cell, then count per 30-day rolling window
    recurrence = hotspots.groupby(
        ["grid_lat", "grid_lon"]
    ).agg(
        total_detections=("acq_date", "count"),
    ).reset_index()
    
    # Use total detections at that grid cell as a proxy for recurrence
    # (full 30-day rolling window would be O(n²) on millions of records)
    hotspots = hotspots.merge(
        recurrence.rename(columns={"total_detections": "recurrence_count"}),
        on=["grid_lat", "grid_lon"],
        how="left",
    )
    
    hotspots["recurrence_count"] = hotspots["recurrence_count"].fillna(1).astype(int)
    hotspots = hotspots.drop(columns=["grid_lat", "grid_lon"])
    
    logger.info(f"  Recurrence range: {hotspots['recurrence_count'].min()} - {hotspots['recurrence_count'].max()}")
    
    return hotspots


def compute_spatial_cluster_size(hotspots: pd.DataFrame) -> pd.DataFrame:
    """
    Count the number of other hotspots within a 5km radius (Feature #11, §5.3).
    
    Uses BallTree for efficient spatial counting.
    """
    logger.info("Computing spatial cluster sizes (5km radius)...")
    
    hotspots = hotspots.copy()
    
    # Sample-based approach for large datasets
    n = len(hotspots)
    
    if n > 500_000:
        # For very large datasets, use grid-based approximation
        logger.info(f"  Large dataset ({n:,} records), using grid-based approximation...")
        
        # Grid at ~5km resolution (0.05° ≈ 5km)
        hotspots["cluster_grid_lat"] = (hotspots["latitude"] / 0.05).round() * 0.05
        hotspots["cluster_grid_lon"] = (hotspots["longitude"] / 0.05).round() * 0.05
        
        cluster_counts = hotspots.groupby(
            ["cluster_grid_lat", "cluster_grid_lon"]
        ).size().reset_index(name="spatial_cluster_size")
        
        hotspots = hotspots.merge(
            cluster_counts,
            on=["cluster_grid_lat", "cluster_grid_lon"],
            how="left",
        )
        
        hotspots = hotspots.drop(columns=["cluster_grid_lat", "cluster_grid_lon"])
    else:
        # Exact BallTree approach for smaller datasets
        coords_rad = np.radians(hotspots[["latitude", "longitude"]].values)
        tree = BallTree(coords_rad, metric="haversine")
        
        radius_rad = CLUSTER_RADIUS_KM / EARTH_RADIUS_KM
        counts = tree.query_radius(coords_rad, r=radius_rad, count_only=True)
        
        hotspots["spatial_cluster_size"] = counts
    
    hotspots["spatial_cluster_size"] = hotspots["spatial_cluster_size"].fillna(1).astype(int)
    
    logger.info(f"  Cluster size range: {hotspots['spatial_cluster_size'].min()} - {hotspots['spatial_cluster_size'].max()}")
    
    return hotspots


def compute_spread_rate(hotspots: pd.DataFrame) -> pd.DataFrame:
    """
    Compute spatial spread rate in km/hr (Feature #12, §5.3).
    
    For each grid cell, measures how far the fire front moved over time.
    Simplified as: max_distance_between_detections / time_span.
    """
    logger.info("Computing spread rates...")
    
    hotspots = hotspots.copy()
    
    # Grid cells for grouping
    hotspots["spread_grid_lat"] = (hotspots["latitude"] / 0.05).round() * 0.05
    hotspots["spread_grid_lon"] = (hotspots["longitude"] / 0.05).round() * 0.05
    
    if not pd.api.types.is_datetime64_any_dtype(hotspots["acq_date"]):
        hotspots["acq_date"] = pd.to_datetime(hotspots["acq_date"])
    
    # Compute spread per cluster
    def cluster_spread(group):
        if len(group) < 2:
            return 0.0
        
        lat_range = group["latitude"].max() - group["latitude"].min()
        lon_range = group["longitude"].max() - group["longitude"].min()
        
        # Approximate distance in km
        spatial_extent_km = np.sqrt(
            (lat_range * 111.0) ** 2 + 
            (lon_range * 111.0 * np.cos(np.radians(group["latitude"].mean()))) ** 2
        )
        
        time_span_hours = (
            (group["acq_date"].max() - group["acq_date"].min()).total_seconds() / 3600
        )
        
        if time_span_hours > 0:
            return spatial_extent_km / time_span_hours
        return 0.0
    
    spread_rates = hotspots.groupby(
        ["spread_grid_lat", "spread_grid_lon"]
    ).apply(cluster_spread, include_groups=False).reset_index(name="spread_rate")
    
    hotspots = hotspots.merge(
        spread_rates,
        on=["spread_grid_lat", "spread_grid_lon"],
        how="left",
    )
    
    hotspots["spread_rate"] = hotspots["spread_rate"].fillna(0.0)
    hotspots = hotspots.drop(columns=["spread_grid_lat", "spread_grid_lon"])
    
    # Cap extreme outliers
    p99 = hotspots["spread_rate"].quantile(0.99)
    hotspots["spread_rate"] = hotspots["spread_rate"].clip(upper=p99)
    
    logger.info(f"  Spread rate range: {hotspots['spread_rate'].min():.4f} - {hotspots['spread_rate'].max():.4f} km/hr")
    
    return hotspots


def assign_land_cover_from_osm(hotspots: pd.DataFrame, facilities: pd.DataFrame) -> pd.DataFrame:
    """
    Assign simplified land cover class based on OSM proximity.
    
    Strategy D (user decision): Use OSM-derived land use for real-time.
    Categories derived from facility proximity and type:
    - Industrial: within 2km of industrial facility
    - Urban: within 5km of urban infrastructure
    - Unknown: everything else (will be refined with raster data in training)
    """
    logger.info("Assigning land cover class (OSM-derived)...")
    
    hotspots = hotspots.copy()
    
    conditions = [
        hotspots["dist_to_industry_m"] <= 1000,      # Very close to industry
        hotspots["dist_to_industry_m"] <= 5000,       # Near industrial area
        hotspots["dist_to_industry_m"] <= 20000,      # Semi-urban
    ]
    choices = ["Industrial", "Urban", "Semi-Urban"]
    
    hotspots["land_cover_class"] = np.select(conditions, choices, default="Unknown")
    
    lc_dist = hotspots["land_cover_class"].value_counts().to_dict()
    logger.info(f"  Land cover distribution: {lc_dist}")
    
    return hotspots


def run_spatial_enrichment(
    firms_csv_path: str,
    osm_csv_path: str,
    output_path: str,
) -> pd.DataFrame:
    """
    Full spatial enrichment pipeline.
    
    Takes unified FIRMS data and enriches with all spatial features.
    """
    logger.info("=" * 60)
    logger.info("SPATIAL ENRICHMENT PIPELINE")
    logger.info("=" * 60)
    
    # Load data
    logger.info(f"Loading unified FIRMS data from {os.path.basename(firms_csv_path)}...")
    hotspots = pd.read_csv(firms_csv_path, low_memory=False)
    logger.info(f"  Loaded {len(hotspots):,} hotspots")
    
    facilities = load_osm_facilities(osm_csv_path)
    
    # Build spatial index
    tree, _ = build_facility_tree(facilities)
    
    # Step 1: Nearest facility (Features #6, #7)
    hotspots = compute_nearest_facility(hotspots, facilities, tree)
    
    # Step 2: Land cover (Feature #8) — OSM-derived
    hotspots = assign_land_cover_from_osm(hotspots, facilities)
    
    # Step 3: Persistence (Feature #9)
    hotspots = compute_persistence_hours(hotspots)
    
    # Step 4: Recurrence (Feature #10)
    hotspots = compute_recurrence_count(hotspots)
    
    # Step 5: Cluster size (Feature #11)
    hotspots = compute_spatial_cluster_size(hotspots)
    
    # Step 6: Spread rate (Feature #12)
    hotspots = compute_spread_rate(hotspots)
    
    # Summary
    logger.info("=" * 60)
    logger.info("ENRICHMENT COMPLETE")
    logger.info(f"  Total records: {len(hotspots):,}")
    logger.info(f"  Features added: dist_to_industry_m, industrial_type, is_near_industry,")
    logger.info(f"                  land_cover_class, persistence_hours, recurrence_count,")
    logger.info(f"                  spatial_cluster_size, spread_rate")
    
    # Check for missing values in key features
    feature_cols = [
        "dist_to_industry_m", "industrial_type", "land_cover_class",
        "persistence_hours", "recurrence_count", "spatial_cluster_size", "spread_rate",
    ]
    for col in feature_cols:
        if col in hotspots.columns:
            nulls = hotspots[col].isna().sum()
            if nulls > 0:
                logger.warning(f"  {col}: {nulls:,} missing values")
    
    logger.info("=" * 60)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    hotspots.to_csv(output_path, index=False)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    logger.info(f"  Saved to: {output_path} ({size_mb:.1f} MB)")
    
    return hotspots


# ----- CLI Entry Point -----
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    data_dir = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\suraj\Desktop\NASA-FIRMS\data"
    
    firms_csv = os.path.join(data_dir, "processed", "firms_unified.csv")
    osm_csv = os.path.join(data_dir, "osm", "osm_all_industrial_india.csv")
    output_csv = os.path.join(data_dir, "processed", "firms_enriched.csv")
    
    if not os.path.exists(firms_csv):
        print(f"ERROR: Unified FIRMS data not found at {firms_csv}")
        print("Run preprocess_firms.py first!")
        sys.exit(1)
    
    df = run_spatial_enrichment(firms_csv, osm_csv, output_csv)
    print(f"\nDone! {len(df):,} enriched records saved to {output_csv}")
