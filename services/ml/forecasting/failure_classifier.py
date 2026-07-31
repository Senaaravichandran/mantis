"""XGBoost binary failure classifier for infrastructure assets."""

from dataclasses import dataclass
import numpy as np


@dataclass
class FailurePrediction:
    failure_probability: float
    risk_factors: list[dict]
    recommendation: str


class FailureClassifier:
    """Predicts probability of infrastructure failure based on asset features.

    Uses a rule-based scoring model (XGBoost can be plugged in when training data
    is available).
    """

    # Feature importance weights for failure prediction
    WEIGHTS = {
        "age_factor": 0.25,
        "health_factor": 0.30,
        "material_factor": 0.15,
        "inspection_overdue": 0.15,
        "alert_frequency": 0.15,
    }

    # Material vulnerability scores (0=robust, 1=vulnerable)
    MATERIAL_SCORES = {
        "Cast iron": 0.8,
        "Corrugated steel": 0.7,
        "Steel": 0.5,
        "Steel truss": 0.55,
        "Steel arch": 0.45,
        "Asphalt": 0.6,
        "Ductile iron": 0.35,
        "Concrete": 0.3,
        "Concrete lined": 0.25,
        "Concrete box": 0.3,
        "PVC": 0.2,
        "Earth/concrete": 0.35,
    }

    def predict(
        self,
        health_score: float,
        age_years: int,
        material: str | None = None,
        days_since_inspection: int | None = None,
        recent_alert_count: int = 0,
        design_life_years: int | None = None,
    ) -> FailurePrediction:
        """Predict failure probability for an asset."""
        risk_factors = []

        # Age factor: higher risk as asset exceeds design life
        design_life = design_life_years or 50
        age_ratio = age_years / design_life
        age_score = min(1.0, age_ratio ** 1.5)
        if age_ratio > 0.8:
            risk_factors.append({
                "factor": "Age",
                "severity": "high" if age_ratio > 1.0 else "medium",
                "detail": f"Asset is {age_years} years old ({int(age_ratio*100)}% of {design_life}-year design life)",
            })

        # Health factor: inverse of health score
        health_factor = max(0, 1.0 - health_score / 100.0)
        if health_score < 50:
            risk_factors.append({
                "factor": "Health Score",
                "severity": "critical" if health_score < 30 else "high",
                "detail": f"Current health score is {health_score}/100",
            })

        # Material factor
        material_score = self.MATERIAL_SCORES.get(material, 0.5) if material else 0.5
        if material_score > 0.6:
            risk_factors.append({
                "factor": "Material",
                "severity": "medium",
                "detail": f"{material} has higher vulnerability to degradation",
            })

        # Inspection overdue factor
        inspection_score = 0.0
        if days_since_inspection is not None:
            if days_since_inspection > 730:  # 2 years
                inspection_score = 0.8
                risk_factors.append({
                    "factor": "Inspection Overdue",
                    "severity": "high",
                    "detail": f"Last inspection was {days_since_inspection} days ago",
                })
            elif days_since_inspection > 365:
                inspection_score = 0.4

        # Alert frequency factor
        alert_score = min(1.0, recent_alert_count / 5.0)
        if recent_alert_count >= 3:
            risk_factors.append({
                "factor": "Alert Frequency",
                "severity": "high",
                "detail": f"{recent_alert_count} alerts in recent period",
            })

        # Weighted probability
        probability = (
            self.WEIGHTS["age_factor"] * age_score +
            self.WEIGHTS["health_factor"] * health_factor +
            self.WEIGHTS["material_factor"] * material_score +
            self.WEIGHTS["inspection_overdue"] * inspection_score +
            self.WEIGHTS["alert_frequency"] * alert_score
        )
        probability = round(min(0.99, max(0.01, probability)), 3)

        # Recommendation
        if probability > 0.7:
            rec = "URGENT: Schedule immediate inspection and emergency maintenance"
        elif probability > 0.5:
            rec = "HIGH PRIORITY: Schedule inspection within 30 days"
        elif probability > 0.3:
            rec = "MONITOR: Increase monitoring frequency and plan preventive maintenance"
        else:
            rec = "NORMAL: Continue standard monitoring schedule"

        return FailurePrediction(
            failure_probability=probability,
            risk_factors=risk_factors,
            recommendation=rec,
        )
