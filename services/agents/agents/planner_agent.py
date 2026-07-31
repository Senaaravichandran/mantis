"""Planner Agent — maintenance schedule optimizer and work order drafter."""

from ..graph.state import MANTISState
from ..tools.database_tools import get_asset_details
from .base_agent import BaseMantisAgent


class PlannerAgent(BaseMantisAgent):
    """Generates prioritized maintenance schedules and work order drafts.

    Balances urgency vs cost vs resource availability.
    """

    name = "planner"
    description = "Maintenance schedule optimizer and work order drafter"

    async def run(self, state: MANTISState) -> MANTISState:
        asset_id = state.trigger_asset_id
        risk_score = state.risk_score or 50
        rca = state.root_cause_analysis or "No root cause analysis available"

        self._add_thought(state, f"Planning maintenance response for asset {asset_id} (risk: {risk_score})")

        asset = await get_asset_details(asset_id, db_session=self.db_session)

        # Determine priority from risk score
        if risk_score >= 80:
            priority = 1  # Critical
            timeline = "Within 7 days"
        elif risk_score >= 60:
            priority = 2  # High
            timeline = "Within 30 days"
        elif risk_score >= 40:
            priority = 3  # Medium
            timeline = "Within 60 days"
        else:
            priority = 4  # Low
            timeline = "Within 90 days"

        # LLM generates work order details
        prompt = (
            f"Generate a detailed maintenance work order for this infrastructure issue:\n\n"
            f"Asset: {asset.get('name', 'Unknown')} ({asset.get('asset_type', 'unknown')})\n"
            f"Material: {asset.get('material', 'unknown')}\n"
            f"Risk Score: {risk_score}/100\n"
            f"Root Cause Analysis: {rca[:500]}\n"
            f"Priority: {priority} ({timeline})\n\n"
            f"Provide:\n"
            f"1. Work order title\n"
            f"2. Detailed scope of work\n"
            f"3. Estimated cost range\n"
            f"4. Required contractor specialty\n"
            f"5. Safety considerations\n"
        )

        wo_details = await self._invoke_llm(prompt)
        self._add_thought(state, f"Work order drafted: {wo_details[:200]}...")

        # Estimate cost based on asset type and risk
        base_costs = {
            "bridge": 75000, "water_main": 35000, "road": 25000,
            "tunnel": 100000, "pump_station": 45000, "culvert": 20000,
            "retention_basin": 15000, "power_line": 40000,
        }
        base = base_costs.get(asset.get("asset_type", ""), 30000)
        estimated_cost = base * (0.5 + risk_score / 100)

        state.work_order_draft = {
            "asset_id": asset_id,
            "municipality_id": state.municipality_id,
            "title": f"Maintenance: {asset.get('name', 'Infrastructure Asset')}",
            "scope_of_work": wo_details,
            "priority": priority,
            "timeline": timeline,
            "estimated_cost": round(estimated_cost, 2),
            "risk_score": risk_score,
            "generated_by": "planner_agent",
            "recommended_specialty": asset.get("asset_type", "general"),
        }

        self._add_thought(state, f"Work order: Priority {priority}, Est. cost ${estimated_cost:,.0f}, Timeline: {timeline}")

        state.next_agent = "reporter"
        state.completed_agents.append(self.name)
        return state
