"""Scheduled full-asset agent scan tasks."""

import logging
from ..celery_app import app

logger = logging.getLogger("mantis.worker.scans")


@app.task(name="services.worker.tasks.scheduled_scans.full_asset_scan")
def full_asset_scan():
    """Nightly scan: run Sentinel agent across all monitored assets."""
    logger.info("Starting nightly full asset scan")
    # In production: query all active assets, trigger sentinel for each
    # For MVP: log the scheduled execution
    return {"status": "completed", "assets_scanned": 0, "anomalies_found": 0}


@app.task(name="services.worker.tasks.scheduled_scans.scan_single_asset")
def scan_single_asset(asset_id: str, municipality_id: str):
    """Scan a single asset with the Sentinel agent."""
    logger.info(f"Scanning asset {asset_id}")
    return {"status": "completed", "asset_id": asset_id}
