"""FHWA National Bridge Inventory data sync connector."""

from typing import Any
from .base import BaseConnector


class NBIConnector(BaseConnector):
    """Syncs National Bridge Inventory data from FHWA."""

    name = "nbi"
    poll_interval_seconds = 86400 * 7  # Weekly

    async def poll(self) -> list[dict[str, Any]]:
        # NBI data is typically synced as a batch CSV download
        # Stub: Full implementation downloads and parses NBI ASCII files
        return []
