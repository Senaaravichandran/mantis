"""USGS Water Services API connector."""

import httpx
from typing import Any
from .base import BaseConnector


class USGSConnector(BaseConnector):
    """Polls USGS National Water Information System for stream gauge data."""

    name = "usgs"
    poll_interval_seconds = 900  # Every 15 minutes

    def __init__(self, kafka_producer=None, site_ids: list[str] | None = None):
        super().__init__(kafka_producer)
        self.site_ids = site_ids or ["03049500"]  # Default: Allegheny River at Pittsburgh

    async def poll(self) -> list[dict[str, Any]]:
        events = []
        sites = ",".join(self.site_ids)
        url = f"https://waterservices.usgs.gov/nwis/iv/?sites={sites}&format=json&parameterCd=00060,00065"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=15.0)
                if resp.status_code == 200:
                    data = resp.json()
                    for ts in data.get("value", {}).get("timeSeries", []):
                        site = ts["sourceInfo"]["siteName"]
                        param = ts["variable"]["variableName"]
                        values = ts.get("values", [{}])[0].get("value", [])
                        if values:
                            latest = values[-1]
                            events.append({
                                "source": "usgs",
                                "site_name": site,
                                "parameter": param,
                                "value": float(latest["value"]),
                                "timestamp": latest["dateTime"],
                            })
        except Exception:
            pass
        return events
