"""Dynamic threshold calibration per sensor type."""

import numpy as np
from dataclasses import dataclass


@dataclass
class ThresholdConfig:
    warning_sigma: float
    critical_sigma: float
    min_samples: int
    decay_rate: float


# Default thresholds by sensor type
SENSOR_THRESHOLDS: dict[str, ThresholdConfig] = {
    "vibration": ThresholdConfig(warning_sigma=2.0, critical_sigma=3.5, min_samples=100, decay_rate=0.001),
    "pressure": ThresholdConfig(warning_sigma=2.5, critical_sigma=4.0, min_samples=50, decay_rate=0.005),
    "strain": ThresholdConfig(warning_sigma=2.0, critical_sigma=3.0, min_samples=100, decay_rate=0.001),
    "flow": ThresholdConfig(warning_sigma=3.0, critical_sigma=5.0, min_samples=50, decay_rate=0.01),
    "temperature": ThresholdConfig(warning_sigma=3.0, critical_sigma=5.0, min_samples=24, decay_rate=0.02),
    "displacement": ThresholdConfig(warning_sigma=2.0, critical_sigma=3.0, min_samples=100, decay_rate=0.001),
    "water_level": ThresholdConfig(warning_sigma=2.5, critical_sigma=4.0, min_samples=50, decay_rate=0.005),
    "corrosion": ThresholdConfig(warning_sigma=2.0, critical_sigma=3.0, min_samples=30, decay_rate=0.001),
    "humidity": ThresholdConfig(warning_sigma=3.0, critical_sigma=5.0, min_samples=24, decay_rate=0.02),
    "tilt": ThresholdConfig(warning_sigma=1.5, critical_sigma=2.5, min_samples=100, decay_rate=0.001),
}


class ThresholdCalibrator:
    """Calibrates anomaly detection thresholds based on historical data patterns."""

    def __init__(self, sensor_type: str):
        self.config = SENSOR_THRESHOLDS.get(
            sensor_type,
            ThresholdConfig(warning_sigma=2.5, critical_sigma=4.0, min_samples=50, decay_rate=0.005),
        )

    def calibrate(self, historical_values: np.ndarray) -> dict:
        """Calculate calibrated thresholds from historical data.

        Returns warning and critical threshold values.
        """
        if len(historical_values) < self.config.min_samples:
            return {
                "calibrated": False,
                "reason": f"Insufficient data ({len(historical_values)}/{self.config.min_samples})",
            }

        mean = np.mean(historical_values)
        std = np.std(historical_values)

        return {
            "calibrated": True,
            "mean": float(mean),
            "std": float(std),
            "warning_lower": float(mean - self.config.warning_sigma * std),
            "warning_upper": float(mean + self.config.warning_sigma * std),
            "critical_lower": float(mean - self.config.critical_sigma * std),
            "critical_upper": float(mean + self.config.critical_sigma * std),
            "samples_used": len(historical_values),
        }
