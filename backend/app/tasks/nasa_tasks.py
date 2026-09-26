import logging
import datetime
import httpx
import pandas as pd
import io
from geoalchemy2.elements import WKTElement

from app.database import SyncSessionLocal
from app.models.spatial import Hotspot, MLClassificationEnum, SystemSetting
from app.config import settings

logger = logging.getLogger(__name__)

PUBLIC_MODIS_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_South_Asia_24h.csv"
PUBLIC_VIIRS_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_Asia_24h.csv"

async def fetch_nasa_firms_data():
    """
    Pull active fire data from NASA FIRMS,
    insert new hotspots, and trigger the ML pipeline synchronously.
    """
    logger.info("Starting NASA FIRMS ingestion task...")
    
    with SyncSessionLocal() as db:
        settings_rows = db.query(SystemSetting).all()
        prefs = {s.key: s.value for s in settings_rows}
        
        ingestion_interval_hours = float(prefs.get("settings_ingestion", "3"))
        last_ingestion_time_str = prefs.get("last_ingestion_time")
        
        now = datetime.datetime.utcnow()
        if last_ingestion_time_str:
            try:
                last_time = datetime.datetime.fromisoformat(last_ingestion_time_str)
                elapsed = (now - last_time).total_seconds() / 3600.0
                if elapsed < ingestion_interval_hours:
                    logger.info(f"Skipping ingestion. Elapsed {elapsed:.2f}h < {ingestion_interval_hours}h interval.")
                    return False
            except Exception as e:
                logger.error(f"Error parsing last_ingestion_time: {e}")
                
        last_ing_setting = db.query(SystemSetting).filter(SystemSetting.key == "last_ingestion_time").first()
        if last_ing_setting:
            last_ing_setting.value = now.isoformat()
        else:
            db.add(SystemSetting(key="last_ingestion_time", value=now.isoformat()))
        db.commit()
    
    urls_to_fetch = []
    
    active_api_key = prefs.get("firms_api_key") or settings.firms_map_key
    
    if active_api_key and active_api_key != "your_nasa_firms_api_key_here":
        bbox = settings.india_bbox
        urls_to_fetch.append(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{active_api_key}/VIIRS_SNPP_NRT/{bbox}/1")
        urls_to_fetch.append(f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{active_api_key}/MODIS_NRT/{bbox}/1")
    else:
        logger.warning("No FIRMS_MAP_KEY provided. Falling back to public 24-hr South Asia CSVs.")
        urls_to_fetch = [PUBLIC_MODIS_URL, PUBLIC_VIIRS_URL]

    all_hotspots_df = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for url in urls_to_fetch:
            try:
                logger.info(f"Fetching data from: {url.split(settings.firms_map_key)[0] if settings.firms_map_key else url}")
                response = await client.get(url)
                response.raise_for_status()
                
                if 'No fires' in response.text:
                    continue
                    
                df = pd.read_csv(io.StringIO(response.text))
                
                df['satellite'] = df.get('satellite', 'Unknown')
                df['instrument'] = df.get('instrument', 'Unknown')
                df['daynight'] = df.get('daynight', 'D')
                
                all_hotspots_df.append(df)
            except Exception as e:
                logger.error(f"Error fetching from NASA FIRMS: {e}")
            
    if not all_hotspots_df:
        logger.info("No data fetched from NASA FIRMS.")
        return False
        
    combined_df = pd.concat(all_hotspots_df, ignore_index=True)
    logger.info(f"Fetched {len(combined_df)} total records from NASA FIRMS.")
    combined_df = combined_df.fillna(0)
    
    with SyncSessionLocal() as db:
        new_hotspot_ids = []
        
        for _, row in combined_df.iterrows():
            acq_date_str = str(row.get('acq_date', datetime.datetime.utcnow().date()))
            acq_time_str = str(row.get('acq_time', '0000')).zfill(4)
            
            try:
                acq_dt = datetime.datetime.strptime(f"{acq_date_str} {acq_time_str}", "%Y-%m-%d %H%M")
            except:
                acq_dt = datetime.datetime.utcnow()
            
            lat = float(row.get('latitude', 0))
            lon = float(row.get('longitude', 0))
            point = f"POINT({lon} {lat})"
            
            exists = db.query(Hotspot).filter(
                Hotspot.latitude == lat,
                Hotspot.longitude == lon,
                Hotspot.acq_date == acq_dt
            ).first()
            
            if exists:
                continue
                
            hotspot = Hotspot(
                latitude=lat,
                longitude=lon,
                geom=WKTElement(point, srid=4326),
                brightness=float(row.get('brightness', row.get('bright_ti4', 0))),
                bright_t31=float(row.get('bright_t31', row.get('bright_ti5', 0))),
                frp=float(row.get('frp', 0)),
                confidence=float(row.get('confidence', 0)) if str(row.get('confidence')).isnumeric() else 50.0,
                satellite=str(row.get('satellite')),
                instrument=str(row.get('instrument')),
                daynight=str(row.get('daynight')),
                pixel_area=1.0,
                acq_date=acq_dt,
                ml_label=MLClassificationEnum.UNCLASSIFIED
            )
            
            db.add(hotspot)
            db.flush()
            new_hotspot_ids.append(hotspot.id)
            
        db.commit()
        
    logger.info(f"Inserted {len(new_hotspot_ids)} new unique hotspots into database.")
    
    if new_hotspot_ids:
        from app.tasks.ml_tasks import process_hotspots_batch
        await process_hotspots_batch(new_hotspot_ids)
        
    return True
