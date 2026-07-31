"""Analyst Agent — deep investigation and risk scoring."""

from ..graph.state import MANTISState
from ..tools.database_tools import get_asset_details, get_asset_alerts
from .base_agent import BaseMantisAgent


class AnalystAgent(BaseMantisAgent):
    """Performs deep-dive analysis of flagged anomalies.

    Cross-references against maintenance history, material specs,
    age curves, and weather. Generates risk score (0-100).
    """

    name = "analyst"
    description = "Deep investigation and risk scoring agent"

    async def run(self, state: MANTISState) -> MANTISState:
        asset_id = state.trigger_asset_id
        anomaly = state.anomaly_details

        self._add_thought(state, f"Beginning deep analysis of anomaly on asset {asset_id}")

        # Get asset details and alert history
        asset = await get_asset_details(asset_id, db_session=self.db_session)
        past_alerts = await get_asset_alerts(asset_id, days=90, db_session=self.db_session)

        self._add_thought(state, f"Asset: {asset.get('name', 'Unknown')} ({asset.get('asset_type', 'unknown')}), "
                         f"Health: {asset.get('health_score', 'N/A')}, Past alerts: {len(past_alerts)}")

        # Build comprehensive analysis prompt
        prompt = (
            f"Perform a comprehensive risk analysis for this infrastructure anomaly:\n\n"
            f"Asset: {asset.get('name', 'Unknown')}\n"
            f"Type: {asset.get('asset_type', 'unknown')}\n"
            f"Material: {asset.get('material', 'unknown')}\n"
            f"Age: {asset.get('age_years', 'unknown')} years\n"
            f"Current Health Score: {asset.get('health_score', 'N/A')}/100\n"
            f"Risk Level: {asset.get('risk_level', 'unknown')}\n\n"
            f"Anomaly Details:\n"
            f"- Score: {anomaly.get('score', 'N/A')}\n"
            f"- Confidence: {anomaly.get('confidence', 'N/A')}\n"
            f"- Affected Sensors: {anomaly.get('affected_sensors', [])}\n"
            f"- Deviation: {anomaly.get('deviation_pct', 'N/A')}%\n"
            f"- Weather Correlation: {anomaly.get('weather_correlation', 'none')}\n\n"
            f"Past 90-day alerts: {len(past_alerts)}\n\n"
            f"Provide:\n"
            f"1. Root cause analysis\n"
            f"2. Risk score (0-100) with justification\n"
            f"3. Recommended immediate actions\n"
        )

        analysis = await self._invoke_llm(prompt)
        self._add_thought(state, f"Analysis complete: {analysis[:200]}...")

        # Calculate risk score based on available data
        health = asset.get("health_score", 50)
        anomaly_score = anomaly.get("score", 0)
        alert_factor = min(20, len(past_alerts) * 5)

        risk_score = min(100, max(0,
            (100 - health) * 0.4 +
            anomaly_score * 15 +
            alert_factor
        ))

        state.risk_score = round(risk_score, 1)
        state.risk_confidence = anomaly.get("confidence", 0.5)
        state.root_cause_analysis = analysis
        state.recommended_actions = [
            f"Schedule inspection of {asset.get('name', 'asset')}",
            "Review sensor calibration on affected sensors",
            "Cross-reference with nearby asset readings",
        ]

        self._add_thought(state, f"Risk Score: {state.risk_score}/100 (Confidence: {state.risk_confidence})")

        if state.risk_score >= 60:
            state.next_agent = "planner"
            self._add_thought(state, "High risk — routing to Planner for work order generation")
        elif state.risk_score >= 30:
            state.next_agent = "reporter"
            self._add_thought(state, "Medium risk — routing to Reporter for notification")
        else:
            state.next_agent = None
            self._add_thought(state, "Low risk — ending pipeline")

        state.completed_agents.append(self.name)
        return state
