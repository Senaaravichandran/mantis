"""MANTIS API Service — FastAPI application factory."""

import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add shared library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from vigil_shared.config import get_settings
from vigil_shared.logging import setup_logging

from .middleware.request_id import RequestIDMiddleware
from .middleware.audit_log import AuditLogMiddleware
from .routers import assets, sensors, alerts, workorders, analytics, agents, reports, admin

logger = setup_logging("mantis-api")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MANTIS API starting up", extra={"service": "api", "version": "0.1.0"})
    logger.info("Initializing database connections...")
    yield
    logger.info("MANTIS API shutting down gracefully", extra={"service": "api"})


app = FastAPI(
    title="MANTIS API",
    description="Intelligent Infrastructure Monitoring with AI-Powered Lifecycle Management",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(AuditLogMiddleware)
app.add_middleware(RequestIDMiddleware)

# Register routers
app.include_router(assets.router)
app.include_router(sensors.router)
app.include_router(alerts.router)
app.include_router(workorders.router)
app.include_router(analytics.router)
app.include_router(agents.router)
app.include_router(reports.router)
app.include_router(admin.router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mantis-api",
        "version": "0.1.0",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    return {
        "name": "MANTIS",
        "tagline": "From Sensor to Work Order, Autonomously",
        "version": "0.1.0",
        "docs": "/docs",
    }

# API initialization configuration

# Finalizing end-to-end backend integration
