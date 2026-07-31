"""Modbus TCP / OPC-UA SCADA connector (stub for MVP)."""

from typing import Any
from .base import BaseConnector


class SCADAConnector(BaseConnector):
    """Connects to SCADA systems via Modbus TCP or OPC-UA.

    Stub implementation for MVP. Full implementation will use
    pymodbus for Modbus TCP and asyncua for OPC-UA connections.
    """

    name = "scada"
    poll_interval_seconds = 60

    async def poll(self) -> list[dict[str, Any]]:
        # Stub: In production, this connects to actual SCADA systems
        return []
