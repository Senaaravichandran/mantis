"""NOAA National Weather Service API connector."""

import httpx
from typing import Any
from .base import BaseConnector


class WeatherConnector(BaseConnector):
    """Polls NOAA NWS API for weather data relevant to infrastructure assets."""

    name = "weather"
    poll_interval_seconds = 3600  # Hourly

    def __init__(self, kafka_producer=None, coordinates: list[tuple[float, float]] | None = None):
        super().__init__(kafka_producer)
        self.coordinates = coordinates or [(40.4406, -79.9959)]  # Default: Pittsburgh

    async def poll(self) -> list[dict[str, Any]]:
        events = []
        async with httpx.AsyncClient() as client:
            for lat, lon in self.coordinates:
                try:
                    resp = await client.get(
                        f"https://api.weather.gov/points/{lat},{lon}",
                        headers={"User-Agent": "MANTIS/0.1.0"},
                        timeout=10.0,
                    )
                    if resp.status_code == 200:
                        props = resp.json()["properties"]
                        forecast_url = props.get("forecastHourly")
                        if forecast_url:
                            f_resp = await client.get(
                                forecast_url,
                                headers={"User-Agent": "MANTIS/0.1.0"},
                                timeout=10.0,
                            )
                            if f_resp.status_code == 200:
                                current = f_resp.json()["properties"]["periods"][0]
                                temp_f = current["temperature"]
                                temp_c = round((temp_f - 32) * 5 / 9, 1)
                                events.append({
                                    "latitude": lat,
                                    "longitude": lon,
                                    "temperature_c": temp_c,
                                    "conditions": current["shortForecast"],
                                    "wind_speed": current.get("windSpeed", ""),
                                    "freeze_thaw_risk": -2 <= temp_c <= 4,
                                    "extreme_heat": temp_c > 38,
                                })
                except Exception:
                    pass
        return events
