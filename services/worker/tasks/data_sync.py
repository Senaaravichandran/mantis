"""Data synchronization tasks."""

import logging
from ..celery_app import app

logger = logging.getLogger("mantis.worker.sync")


@app.task(name="services.worker.tasks.data_sync.sync_nbi_data")
def sync_nbi_data():
    """Sync National Bridge Inventory data from FHWA."""
    logger.info("Syncing NBI data from FHWA")
    return {"status": "completed", "bridges_synced": 0}


@app.task(name="services.worker.tasks.data_sync.sync_regulatory_calendar")
def sync_regulatory_calendar():
    """Update regulatory compliance calendar."""
    logger.info("Syncing regulatory calendar")
    return {"status": "completed"}
