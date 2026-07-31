"""Admin API endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/config")
async def get_config():
    return {
        "version": "0.1.0",
        "agents": [
            "sentinel", "analyst", "planner",
            "reporter", "contractor", "regulator",
        ],
        "supported_asset_types": [
            "bridge", "water_main", "road", "power_line",
            "tunnel", "pump_station", "culvert", "retention_basin",
        ],
        "supported_sensor_types": [
            "vibration", "pressure", "strain", "flow",
            "temperature", "displacement", "water_level",
            "corrosion", "humidity", "tilt",
        ],
    }
