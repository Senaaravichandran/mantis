"""Async report generation tasks."""

import logging
from ..celery_app import app

logger = logging.getLogger("mantis.worker.reports")


@app.task(name="services.worker.tasks.report_generation.generate_weekly_report")
def generate_weekly_report():
    """Generate weekly infrastructure status report."""
    logger.info("Generating weekly infrastructure report")
    return {"status": "completed", "report_type": "weekly_summary"}


@app.task(name="services.worker.tasks.report_generation.generate_asset_report")
def generate_asset_report(asset_id: str):
    """Generate a detailed report for a specific asset."""
    logger.info(f"Generating report for asset {asset_id}")
    return {"status": "completed", "asset_id": asset_id}
