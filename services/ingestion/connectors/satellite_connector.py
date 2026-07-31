"""ESA Sentinel Hub satellite imagery connector (stub for MVP)."""

from typing import Any
from .base import BaseConnector


class SatelliteConnector(BaseConnector):
    """Polls ESA Copernicus Sentinel Hub for satellite imagery.

    Stub implementation for MVP. Full implementation will use
    the Sentinel Hub API for SAR data and optical imagery.
    """

    name = "satellite"
    poll_interval_seconds = 86400  # Daily

    async def poll(self) -> list[dict[str, Any]]:
        # Stub: In production, fetches Sentinel-1 SAR and Sentinel-2 optical data
        return []
