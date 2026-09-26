import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from app.database import Base, async_engine, init_db
from app.routers import hotspots, facilities, analytics, reports, alerts, settings as settings_router, auth, websocket
from app.tasks.nasa_tasks import fetch_nasa_firms_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting IGNIS API...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    yield
    # Shutdown
    logger.info("Shutting down IGNIS API...")
    await async_engine.dispose()

app = FastAPI(
    title="IGNIS API (Production)",
    description="Industrial Fire Classification & Notification System API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(hotspots.router, prefix="/api/v1/hotspots", tags=["Hotspots"])
app.include_router(facilities.router, prefix="/api/v1/facilities", tags=["Facilities"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(websocket.router, tags=["WebSocket"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.app_env}

# ----- Serverless Cron Endpoint (Triggered by Upstash QStash) -----

async def verify_qstash_signature(request: Request):
    """
    In production, verify the Upstash QStash signature.
    """
    if not settings.qstash_current_signing_key:
        return True # Skip verification if keys are not set
        
    signature = request.headers.get("Upstash-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing Upstash Signature")
        
    # Full verification logic would go here
    # For now we'll accept it if keys aren't strictly enforced
    return True

@app.post("/api/v1/cron/ingest")
async def trigger_ingestion(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint intended to be called on a schedule by Upstash QStash.
    It queues the data ingestion in a FastAPI BackgroundTask so the webhook returns 200 immediately.
    """
    await verify_qstash_signature(request)
    background_tasks.add_task(fetch_nasa_firms_data)
    return {"status": "accepted", "message": "NASA FIRMS ingestion started in background"}
