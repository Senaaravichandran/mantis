"""Weather data tools for MANTIS agents."""

import httpx
from typing import Any


async def get_current_conditions(
    asset_id: str | None = None,
    latitude: float = 40.4406,
    longitude: float = -79.9959,
) -> dict[str, Any]:
    """Get current weather conditions from NOAA API.

    Falls back to mock data if the API is unavailable.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Get forecast office from coordinates
            point_resp = await client.get(
                f"https://api.weather.gov/points/{latitude},{longitude}",
                headers={"User-Agent": "MANTIS/0.1.0"},
                timeout=10.0,
            )
            if point_resp.status_code == 200:
                props = point_resp.json()["properties"]
                forecast_url = props["forecastHourly"]

                # Step 2: Get hourly forecast
                forecast_resp = await client.get(
                    forecast_url,
                    headers={"User-Agent": "MANTIS/0.1.0"},
                    timeout=10.0,
                )
                if forecast_resp.status_code == 200:
                    periods = forecast_resp.json()["properties"]["periods"]
                    current = periods[0]
                    temp_f = current["temperature"]
                    temp_c = round((temp_f - 32) * 5 / 9, 1)

                    return {
                        "temperature_c": temp_c,
                        "humidity_pct": current.get("relativeHumidity", {}).get("value", 50),
                        "wind_speed_kmh": round(int(current.get("windSpeed", "0").split()[0]) * 1.6, 1),
                        "conditions": current["shortForecast"],
                        "freeze_thaw_risk": -2 <= temp_c <= 4,
                        "extreme_heat": temp_c > 38,
                        "precipitation_mm": 0.0,
                    }
    except Exception:
        pass

    # Fallback mock data
    return {
        "temperature_c": 15.0,
        "humidity_pct": 65.0,
        "wind_speed_kmh": 12.0,
        "conditions": "Partly Cloudy",
        "freeze_thaw_risk": False,
        "extreme_heat": False,
        "precipitation_mm": 0.0,
    }


async def get_weather_forecast(
    latitude: float = 40.4406,
    longitude: float = -79.9959,
    days: int = 7,
) -> list[dict[str, Any]]:
    """Get weather forecast for the next N days."""
    try:
        async with httpx.AsyncClient() as client:
            point_resp = await client.get(
                f"https://api.weather.gov/points/{latitude},{longitude}",
                headers={"User-Agent": "MANTIS/0.1.0"},
                timeout=10.0,
            )
            if point_resp.status_code == 200:
                forecast_url = point_resp.json()["properties"]["forecast"]
                forecast_resp = await client.get(
                    forecast_url,
                    headers={"User-Agent": "MANTIS/0.1.0"},
                    timeout=10.0,
                )
                if forecast_resp.status_code == 200:
                    periods = forecast_resp.json()["properties"]["periods"]
                    return [
                        {
                            "name": p["name"],
                            "temperature_f": p["temperature"],
                            "conditions": p["shortForecast"],
                            "wind": p["windSpeed"],
                        }
                        for p in periods[:days * 2]
                    ]
    except Exception:
        pass

    return [{"name": "Today", "temperature_f": 59, "conditions": "Partly Cloudy", "wind": "5 mph"}]
