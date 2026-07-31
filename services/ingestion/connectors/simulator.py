"""Synthetic sensor data simulator for MVP development and testing."""

import random
import math
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from .base import BaseConnector


class SensorSimulator(BaseConnector):
    """Generates realistic synthetic sensor data for infrastructure assets.

    Simulates sensor readings with:
    - Diurnal (day/night) patterns
    - Seasonal trends
    - Random noise
    - Occasional anomalies (configurable probability)
    """

    name = "simulator"
    poll_interval_seconds = 10  # Generate data every 10 seconds

    def __init__(self, kafka_producer=None, anomaly_probability: float = 0.03):
        super().__init__(kafka_producer)
        self.anomaly_probability = anomaly_probability
        self._assets = self._init_simulated_assets()

    def _init_simulated_assets(self) -> list[dict[str, Any]]:
        """Initialize simulated asset configurations."""
        return [
            {"id": "sim-bridge-001", "type": "bridge", "sensors": [
                {"id": "vib-001", "type": "vibration", "base": 2.5, "unit": "mm/s", "noise": 0.3},
                {"id": "str-001", "type": "strain", "base": 250, "unit": "microstrain", "noise": 30},
                {"id": "tmp-001", "type": "temperature", "base": 20, "unit": "celsius", "noise": 3},
            ]},
            {"id": "sim-water-001", "type": "water_main", "sensors": [
                {"id": "prs-001", "type": "pressure", "base": 55, "unit": "psi", "noise": 5},
                {"id": "flw-001", "type": "flow", "base": 800, "unit": "gpm", "noise": 100},
            ]},
            {"id": "sim-road-001", "type": "road", "sensors": [
                {"id": "tmp-002", "type": "temperature", "base": 22, "unit": "celsius", "noise": 5},
                {"id": "dsp-001", "type": "displacement", "base": 2, "unit": "mm", "noise": 0.5},
            ]},
            {"id": "sim-pump-001", "type": "pump_station", "sensors": [
                {"id": "prs-002", "type": "pressure", "base": 60, "unit": "psi", "noise": 8},
                {"id": "vib-002", "type": "vibration", "base": 1.5, "unit": "mm/s", "noise": 0.2},
            ]},
        ]

    async def poll(self) -> list[dict[str, Any]]:
        """Generate synthetic sensor readings."""
        now = datetime.now(timezone.utc)
        hour = now.hour
        events = []

        for asset in self._assets:
            for sensor in asset["sensors"]:
                # Base value with diurnal pattern
                diurnal = math.sin(2 * math.pi * hour / 24) * sensor["noise"] * 0.5
                noise = random.gauss(0, sensor["noise"])
                value = sensor["base"] + diurnal + noise

                # Inject anomaly with configured probability
                is_anomaly = random.random() < self.anomaly_probability
                if is_anomaly:
                    anomaly_factor = random.choice([2.5, 3.0, 3.5, -2.5])
                    value += anomaly_factor * sensor["noise"]

                events.append({
                    "asset_id": asset["id"],
                    "sensor_id": sensor["id"],
                    "sensor_type": sensor["type"],
                    "value": round(value, 3),
                    "unit": sensor["unit"],
                    "quality_flag": "good",
                    "timestamp": now.isoformat(),
                    "is_simulated": True,
                })

        return events
