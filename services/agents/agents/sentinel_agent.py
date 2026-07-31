"""Sentinel Agent — continuous infrastructure sensor anomaly detection."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from ..graph.state import MANTISState
from ..tools.database_tools import query_sensor_history
from ..tools.weather_tools import get_current_conditions
from .base_agent import BaseMantisAgent
from services.ml.anomaly.streaming_detector import StreamingAnomalyDetector


class SentinelAgent(BaseMantisAgent):
    """Monitors all active sensor streams for anomalies.

    Applies statistical and ML-based detection.
    Issues structured alerts with confidence scores.
    """

    name = "sentinel"
    description = "Continuous infrastructure sensor anomaly detector"

    async def run(self, state: MANTISState) -> MANTISState:
        asset_id = state.trigger_asset_id
        sensor_data = state.trigger_sensor_data or {}

        self._add_thought(state, f"Analyzing sensor data for asset {asset_id}")

        # Fetch 30-day historical baseline
        history = await query_sensor_history(asset_id, days=30, db_session=self.db_session)
        weather = await get_current_conditions(asset_id)

        self._add_thought(state, f"Retrieved {len(history)} historical readings and current weather")

        # Run streaming anomaly detection
        detector = StreamingAnomalyDetector(asset_id)
        anomaly_result = detector.score(sensor_data, history, weather)

        # LLM reasoning step: interpret anomaly in context
        prompt = (
            f"Sensor data for asset {asset_id}:\n"
            f"Current readings: {sensor_data}\n"
            f"Anomaly score: {anomaly_result.score}\n"
            f"Affected sensors: {anomaly_result.affected_sensors}\n"
            f"Deviation: {anomaly_result.deviation_pct}%\n"
            f"Weather conditions: {weather}\n"
            f"Historical readings count: {len(history)}\n\n"
            f"Analyze these readings and determine if this is a genuine anomaly "
            f"or an expected variation. Consider weather effects."
        )

        reasoning = await self._invoke_llm(prompt)
        self._add_thought(state, reasoning)

        if anomaly_result.is_anomaly:
            state.anomaly_detected = True
            state.anomaly_details = {
                "score": anomaly_result.score,
                "confidence": anomaly_result.confidence,
                "affected_sensors": anomaly_result.affected_sensors,
                "deviation_pct": anomaly_result.deviation_pct,
                "weather_correlation": anomaly_result.weather_factor,
                "llm_interpretation": reasoning,
            }
            self._add_thought(state, f"ANOMALY DETECTED - Score: {anomaly_result.score}, Confidence: {anomaly_result.confidence}")
            state.next_agent = "analyst"
        else:
            self._add_thought(state, "No significant anomaly detected. Ending pipeline.")
            state.next_agent = None

        state.completed_agents.append(self.name)
        return state
