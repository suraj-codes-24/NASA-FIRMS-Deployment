import os
from celery import Celery
from app.config import settings

celery_app = Celery(
    "ignis_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.ml_tasks", "app.tasks.nasa_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_concurrency=4
)

celery_app.conf.beat_schedule = {
    "fetch-nasa-firms-every-10-mins": {
        "task": "app.tasks.nasa_tasks.fetch_nasa_firms_data",
        "schedule": 600.0, # 10 minutes in seconds
    },
}
