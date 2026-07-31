"""Celery application configuration for MANTIS async task processing."""

import os
from celery import Celery
from celery.schedules import crontab

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

app = Celery(
    "mantis",
    broker=broker_url,
    backend=result_backend,
    include=[
        "services.worker.tasks.scheduled_scans",
        "services.worker.tasks.report_generation",
        "services.worker.tasks.data_sync",
        "services.worker.tasks.model_retraining",
    ],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minute hard limit
    task_soft_time_limit=540,  # 9 minute soft limit
)

# Celery Beat schedule
app.conf.beat_schedule = {
    "nightly-full-scan": {
        "task": "services.worker.tasks.scheduled_scans.full_asset_scan",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2:00 AM
    },
    "weekly-report": {
        "task": "services.worker.tasks.report_generation.generate_weekly_report",
        "schedule": crontab(day_of_week=1, hour=6, minute=0),  # Monday 6 AM
    },
    "nbi-data-sync": {
        "task": "services.worker.tasks.data_sync.sync_nbi_data",
        "schedule": crontab(day_of_week=0, hour=3, minute=0),  # Sunday 3 AM
    },
    "model-retraining": {
        "task": "services.worker.tasks.model_retraining.retrain_anomaly_models",
        "schedule": crontab(day_of_week=6, hour=4, minute=0),  # Saturday 4 AM
    },
}
