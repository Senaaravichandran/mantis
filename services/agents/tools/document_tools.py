"""Document generation tools for MANTIS agents."""

import json
from datetime import datetime, timezone
from typing import Any


async def generate_report(
    report_type: str,
    title: str,
    content: dict[str, Any],
    municipality_id: str | None = None,
) -> dict[str, Any]:
    """Generate a structured report document.

    Report types: anomaly_summary, inspection_notification,
    executive_briefing, public_status_update
    """
    report = {
        "type": report_type,
        "title": title,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "mantis-reporter-agent",
        "municipality_id": municipality_id,
        "sections": [],
    }

    if report_type == "anomaly_summary":
        report["sections"] = [
            {"heading": "Anomaly Overview", "content": content.get("summary", "")},
            {"heading": "Affected Assets", "content": json.dumps(content.get("assets", []))},
            {"heading": "Risk Assessment", "content": content.get("risk_assessment", "")},
            {"heading": "Recommended Actions", "content": json.dumps(content.get("actions", []))},
        ]
    elif report_type == "executive_briefing":
        report["sections"] = [
            {"heading": "Executive Summary", "content": content.get("summary", "")},
            {"heading": "Key Metrics", "content": json.dumps(content.get("metrics", {}))},
            {"heading": "Critical Issues", "content": json.dumps(content.get("issues", []))},
            {"heading": "Budget Impact", "content": content.get("budget_impact", "")},
        ]
    elif report_type == "work_order_report":
        report["sections"] = [
            {"heading": "Work Order Details", "content": json.dumps(content.get("work_order", {}))},
            {"heading": "Scope of Work", "content": content.get("scope", "")},
            {"heading": "Cost Estimate", "content": content.get("cost_estimate", "")},
            {"heading": "Timeline", "content": content.get("timeline", "")},
        ]
    else:
        report["sections"] = [
            {"heading": "Report Content", "content": json.dumps(content)},
        ]

    return report


async def fill_compliance_form(
    form_type: str,
    asset_data: dict[str, Any],
    inspection_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fill a compliance form template with asset and inspection data.

    Form types: fhwa_nbi, epa_water_quality, osha_safety
    """
    form = {
        "form_type": form_type,
        "filled_at": datetime.now(timezone.utc).isoformat(),
        "status": "draft",
        "fields": {},
    }

    if form_type == "fhwa_nbi":
        form["fields"] = {
            "structure_number": asset_data.get("fhwa_id", ""),
            "structure_name": asset_data.get("name", ""),
            "year_built": asset_data.get("installation_year", ""),
            "material": asset_data.get("material", ""),
            "condition_rating": _health_to_nbi_rating(asset_data.get("health_score", 5)),
            "inspection_date": inspection_data.get("date", "") if inspection_data else "",
        }
    elif form_type == "epa_water_quality":
        form["fields"] = {
            "system_id": asset_data.get("epa_id", ""),
            "facility_name": asset_data.get("name", ""),
            "compliance_status": "compliant",
        }

    return form


def _health_to_nbi_rating(health_score: float) -> int:
    """Convert MANTIS health score (0-100) to NBI condition rating (0-9)."""
    return max(0, min(9, int(health_score / 11.1)))
