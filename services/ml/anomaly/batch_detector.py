"""PyOD ensemble anomaly detection for batch sensor data analysis."""

from dataclasses import dataclass
import numpy as np


@dataclass
class BatchAnomalyResult:
    anomaly_indices: list[int]
    scores: list[float]
    labels: list[int]  # 0=normal, 1=anomaly
    threshold: float


class BatchAnomalyDetector:
    """Ensemble anomaly detection using multiple statistical methods.

    Combines Isolation Forest, Local Outlier Factor (LOF),
    Histogram-based Outlier Score (HBOS), and COPOD approaches
    for robust anomaly detection on batch sensor data.

    Falls back to statistical methods if PyOD is not available.
    """

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self._pyod_available = False

        try:
            from pyod.models.iforest import IForest
            from pyod.models.lof import LOF
            from pyod.models.hbos import HBOS
            from pyod.models.copod import COPOD
            self._pyod_available = True
        except ImportError:
            pass

    def detect(self, data: np.ndarray) -> BatchAnomalyResult:
        """Run ensemble anomaly detection on sensor data.

        Args:
            data: 2D numpy array of shape (n_samples, n_features)
        """
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        if len(data) < 20:
            return BatchAnomalyResult(
                anomaly_indices=[], scores=[0.0] * len(data),
                labels=[0] * len(data), threshold=0.5,
            )

        if self._pyod_available:
            return self._pyod_ensemble(data)
        return self._statistical_fallback(data)

    def _pyod_ensemble(self, data: np.ndarray) -> BatchAnomalyResult:
        from pyod.models.iforest import IForest
        from pyod.models.lof import LOF
        from pyod.models.hbos import HBOS
        from pyod.models.copod import COPOD

        models = [
            IForest(contamination=self.contamination, random_state=42),
            LOF(contamination=self.contamination),
            HBOS(contamination=self.contamination),
            COPOD(contamination=self.contamination),
        ]

        all_scores = []
        for model in models:
            model.fit(data)
            scores = model.decision_scores_
            # Normalize to [0, 1]
            s_min, s_max = scores.min(), scores.max()
            if s_max > s_min:
                scores = (scores - s_min) / (s_max - s_min)
            all_scores.append(scores)

        # Average ensemble
        ensemble_scores = np.mean(all_scores, axis=0)
        threshold = np.percentile(ensemble_scores, (1 - self.contamination) * 100)
        labels = (ensemble_scores > threshold).astype(int)
        anomaly_indices = np.where(labels == 1)[0].tolist()

        return BatchAnomalyResult(
            anomaly_indices=anomaly_indices,
            scores=ensemble_scores.tolist(),
            labels=labels.tolist(),
            threshold=float(threshold),
        )

    def _statistical_fallback(self, data: np.ndarray) -> BatchAnomalyResult:
        """Z-score + IQR based detection when PyOD is not available."""
        means = np.mean(data, axis=0)
        stds = np.std(data, axis=0)
        stds[stds == 0] = 1e-6

        z_scores = np.abs((data - means) / stds)
        max_z = np.max(z_scores, axis=1)

        # IQR method
        q1 = np.percentile(max_z, 25)
        q3 = np.percentile(max_z, 75)
        iqr = q3 - q1
        threshold = q3 + 1.5 * iqr

        # Normalize scores
        s_max = max_z.max()
        scores = max_z / s_max if s_max > 0 else max_z

        labels = (max_z > threshold).astype(int)
        anomaly_indices = np.where(labels == 1)[0].tolist()

        return BatchAnomalyResult(
            anomaly_indices=anomaly_indices,
            scores=scores.tolist(),
            labels=labels.tolist(),
            threshold=float(threshold / s_max) if s_max > 0 else 0.5,
        )

# Threshold tuning
