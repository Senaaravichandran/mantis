"""River online ML — per-sensor adaptive baseline anomaly detection."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class AnomalyResult:
    is_anomaly: bool
    score: float
    confidence: float
    affected_sensors: list[str]
    deviation_pct: float
    weather_factor: float | None = None


class StreamingAnomalyDetector:
    """Online anomaly detection using streaming statistics.

    Maintains a running mean and standard deviation per sensor,
    and flags readings that deviate beyond a configurable threshold.
    Uses an exponentially weighted moving average for adaptability.
    """

    def __init__(self, asset_id: str, sigma_threshold: float = 2.0, alpha: float = 0.01):
        self.asset_id = asset_id
        self.sigma_threshold = sigma_threshold
        self.alpha = alpha
        self._sensors: dict[str, dict[str, float]] = {}

    def _get_stats(self, sensor_id: str) -> dict[str, float]:
        if sensor_id not in self._sensors:
            self._sensors[sensor_id] = {
                "mean": 0.0,
                "var": 1.0,
                "count": 0,
            }
        return self._sensors[sensor_id]

    def _update_stats(self, sensor_id: str, value: float):
        stats = self._get_stats(sensor_id)
        stats["count"] += 1
        if stats["count"] == 1:
            stats["mean"] = value
            stats["var"] = 0.0
        else:
            old_mean = stats["mean"]
            stats["mean"] = (1 - self.alpha) * old_mean + self.alpha * value
            stats["var"] = (1 - self.alpha) * stats["var"] + self.alpha * (value - old_mean) ** 2

    def score(
        self,
        sensor_data: dict[str, Any],
        history: list[dict] | None = None,
        weather: dict | None = None,
    ) -> AnomalyResult:
        """Score incoming sensor data for anomalies.

        Args:
            sensor_data: Current sensor readings {sensor_id: value}
            history: Historical readings for baseline (optional, for cold start)
            weather: Current weather conditions (optional)
        """
        # Bootstrap from history if available and we have no stats
        if history and not self._sensors:
            for record in history:
                sid = record.get("sensor_id", "unknown")
                val = record.get("value", 0.0)
                self._update_stats(sid, val)

        anomaly_scores = []
        affected = []

        readings = sensor_data if isinstance(sensor_data, dict) else {"default": sensor_data}
        for sensor_id, value in readings.items():
            if not isinstance(value, (int, float)):
                continue
            stats = self._get_stats(sensor_id)

            if stats["count"] < 10:
                # Not enough data — update and skip
                self._update_stats(sensor_id, value)
                continue

            std = max(np.sqrt(stats["var"]), 1e-6)
            z_score = abs(value - stats["mean"]) / std
            anomaly_scores.append(z_score)

            if z_score > self.sigma_threshold:
                affected.append(sensor_id)

            self._update_stats(sensor_id, value)

        if not anomaly_scores:
            return AnomalyResult(
                is_anomaly=False, score=0.0, confidence=0.0,
                affected_sensors=[], deviation_pct=0.0,
            )

        max_score = max(anomaly_scores)
        avg_score = np.mean(anomaly_scores)
        is_anomaly = len(affected) > 0

        # Weather correlation factor
        weather_factor = None
        if weather:
            if weather.get("freeze_thaw_risk") or weather.get("extreme_heat"):
                weather_factor = 1.3  # Amplify anomaly likelihood

        confidence = min(0.99, 1.0 - np.exp(-max_score / 3.0))
        deviation_pct = (max_score / self.sigma_threshold) * 100

        return AnomalyResult(
            is_anomaly=is_anomaly,
            score=round(float(max_score), 4),
            confidence=round(float(confidence), 4),
            affected_sensors=affected,
            deviation_pct=round(float(deviation_pct), 2),
            weather_factor=weather_factor,
        )
