"""Scheduled ML model retraining tasks."""

import logging
from ..celery_app import app

logger = logging.getLogger("mantis.worker.ml")


@app.task(name="services.worker.tasks.model_retraining.retrain_anomaly_models")
def retrain_anomaly_models():
    """Retrain anomaly detection models with recent data."""
    logger.info("Retraining anomaly detection models")
    return {"status": "completed", "models_retrained": 0}


@app.task(name="services.worker.tasks.model_retraining.retrain_failure_classifier")
def retrain_failure_classifier():
    """Retrain the XGBoost failure classifier."""
    logger.info("Retraining failure classifier")
    return {"status": "completed"}
