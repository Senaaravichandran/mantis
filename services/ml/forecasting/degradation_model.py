"""Infrastructure degradation forecasting using time-series analysis."""

from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta


@dataclass
class DegradationForecast:
    current_health: float
    forecasts: list[dict]  # [{horizon_months, predicted_health, confidence_lower, confidence_upper}]
    estimated_failure_date: str | None
    degradation_rate: float  # health points per year


class DegradationModel:
    """Forecasts infrastructure health degradation over time.

    Uses exponential decay modeling with age-based adjustment factors.
    Falls back to linear regression when NeuralProphet is not available.
    """

    HORIZONS_MONTHS = [6, 12, 24, 60]

    def __init__(self, asset_type: str, material: str | None = None):
        self.asset_type = asset_type
        self.material = material
        # Material-specific decay rates (health points per year)
        self.base_decay_rates = {
            "bridge": {"Steel": 1.2, "Steel truss": 1.4, "Steel arch": 1.1, "Concrete": 0.8},
            "water_main": {"Cast iron": 1.5, "Ductile iron": 0.9, "PVC": 0.4, "Concrete": 0.7},
            "road": {"Asphalt": 2.5, "Concrete": 1.0},
            "tunnel": {"Concrete lined": 0.6, "Concrete": 0.7},
            "pump_station": {"Concrete/Steel": 1.0, "Concrete": 0.8},
            "culvert": {"Corrugated steel": 1.8, "Concrete box": 0.9},
            "retention_basin": {"Earth/concrete": 0.6},
        }

    def _get_decay_rate(self) -> float:
        type_rates = self.base_decay_rates.get(self.asset_type, {})
        return type_rates.get(self.material, 1.0)

    def forecast(
        self,
        current_health: float,
        installation_year: int | None = None,
        health_history: list[dict] | None = None,
    ) -> DegradationForecast:
        """Generate degradation forecast for an infrastructure asset."""
        decay_rate = self._get_decay_rate()

        # Age adjustment: older assets degrade faster
        if installation_year:
            age = datetime.now().year - installation_year
            age_factor = 1.0 + max(0, (age - 30)) * 0.02  # 2% faster per year over 30
            decay_rate *= age_factor

        # If we have historical health data, fit to it
        if health_history and len(health_history) >= 3:
            decay_rate = self._fit_from_history(health_history, decay_rate)

        forecasts = []
        for months in self.HORIZONS_MONTHS:
            years = months / 12.0
            predicted = max(0, current_health - decay_rate * years)
            # Uncertainty grows with horizon
            uncertainty = decay_rate * years * 0.3
            forecasts.append({
                "horizon_months": months,
                "predicted_health": round(predicted, 1),
                "confidence_lower": round(max(0, predicted - uncertainty), 1),
                "confidence_upper": round(min(100, predicted + uncertainty), 1),
            })

        # Estimate failure date (health < 20 = functional failure)
        failure_date = None
        if current_health > 20 and decay_rate > 0:
            years_to_failure = (current_health - 20) / decay_rate
            failure_dt = datetime.now() + timedelta(days=years_to_failure * 365.25)
            failure_date = failure_dt.strftime("%Y-%m")

        return DegradationForecast(
            current_health=current_health,
            forecasts=forecasts,
            estimated_failure_date=failure_date,
            degradation_rate=round(decay_rate, 2),
        )

    def _fit_from_history(self, history: list[dict], default_rate: float) -> float:
        """Estimate decay rate from historical health readings."""
        try:
            times = []
            healths = []
            for entry in history:
                if "date" in entry and "health" in entry:
                    dt = datetime.fromisoformat(entry["date"])
                    times.append(dt.timestamp())
                    healths.append(entry["health"])

            if len(times) < 2:
                return default_rate

            # Linear regression for slope
            t_arr = np.array(times)
            h_arr = np.array(healths)
            t_norm = (t_arr - t_arr[0]) / (365.25 * 24 * 3600)  # to years
            if t_norm[-1] == 0:
                return default_rate

            coeffs = np.polyfit(t_norm, h_arr, 1)
            fitted_rate = -coeffs[0]  # Negative slope = positive decay rate
            return max(0.1, fitted_rate)  # At least 0.1 points/year
        except Exception:
            return default_rate
