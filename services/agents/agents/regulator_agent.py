"""Regulator Agent — compliance monitoring and filing."""

from datetime import datetime, timedelta, timezone

from ..graph.state import MANTISState
from ..tools.document_tools import fill_compliance_form
from ..tools.database_tools import get_asset_details
from .base_agent import BaseMantisAgent


class RegulatorAgent(BaseMantisAgent):
    """Monitors regulatory calendars and auto-populates compliance filings."""

    name = "regulator"
    description = "Compliance monitoring and filing agent"

    INSPECTION_CYCLES = {
        "bridge": {"agency": "FHWA", "cycle_months": 24, "form": "fhwa_nbi"},
        "water_main": {"agency": "EPA", "cycle_months": 12, "form": "epa_water_quality"},
        "tunnel": {"agency": "FHWA", "cycle_months": 24, "form": "fhwa_nbi"},
        "pump_station": {"agency": "EPA", "cycle_months": 12, "form": "epa_water_quality"},
    }

    async def run(self, state: MANTISState) -> MANTISState:
        asset_id = state.trigger_asset_id
        self._add_thought(state, f"Checking regulatory compliance for asset {asset_id}")

        asset = await get_asset_details(asset_id, db_session=self.db_session)
        asset_type = asset.get("asset_type", "unknown")

        # Check applicable regulations
        regulation = self.INSPECTION_CYCLES.get(asset_type)
        compliance_status = {"asset_id": asset_id, "checks": [], "deadlines": []}

        if regulation:
            agency = regulation["agency"]
            cycle_months = regulation["cycle_months"]

            # Check if inspection is due
            last_inspection = asset.get("last_inspection_date")
            now = datetime.now(timezone.utc)

            if last_inspection:
                next_due = last_inspection + timedelta(days=cycle_months * 30)
                days_until_due = (next_due - now.date()).days if hasattr(next_due, 'days') else 0

                status = "compliant" if days_until_due > 0 else "overdue"
                compliance_status["checks"].append({
                    "agency": agency,
                    "requirement": f"{cycle_months}-month inspection cycle",
                    "status": status,
                    "last_inspection": str(last_inspection),
                    "days_until_due": days_until_due,
                })

                # Generate deadline warnings
                if 0 < days_until_due <= 30:
                    compliance_status["deadlines"].append({
                        "agency": agency,
                        "deadline": str(next_due),
                        "days_remaining": days_until_due,
                        "warning_level": "urgent" if days_until_due <= 7 else "warning",
                    })
                    self._add_thought(state, f"WARNING: {agency} inspection due in {days_until_due} days")
            else:
                compliance_status["checks"].append({
                    "agency": agency,
                    "requirement": f"{cycle_months}-month inspection cycle",
                    "status": "no_record",
                    "notes": "No previous inspection on record",
                })

            # Auto-populate compliance form
            form = await fill_compliance_form(
                form_type=regulation["form"],
                asset_data=asset,
            )
            compliance_status["draft_filing"] = form
            self._add_thought(state, f"Draft {regulation['form']} form prepared")
        else:
            self._add_thought(state, f"No specific regulatory cycle defined for asset type: {asset_type}")

        # LLM compliance assessment
        prompt = (
            f"Review the compliance status for this infrastructure asset:\n\n"
            f"Asset: {asset.get('name', 'Unknown')} ({asset_type})\n"
            f"Risk Score: {state.risk_score}/100\n"
            f"Compliance Checks: {compliance_status['checks']}\n"
            f"Upcoming Deadlines: {compliance_status['deadlines']}\n\n"
            f"Identify any compliance risks and recommend actions."
        )

        assessment = await self._invoke_llm(prompt, use_fast=True)
        self._add_thought(state, f"Compliance assessment: {assessment[:200]}...")

        state.compliance_status = compliance_status
        state.upcoming_deadlines = compliance_status.get("deadlines", [])
        state.next_agent = None
        state.completed_agents.append(self.name)
        return state
