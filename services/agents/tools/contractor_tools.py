"""Contractor management tools for MANTIS agents."""

from typing import Any
from datetime import datetime, timezone


async def search_contractors(
    specialty: str | None = None,
    location: str | None = None,
    min_rating: float = 3.0,
    db_session=None,
) -> list[dict[str, Any]]:
    """Search the contractor registry by specialty and location."""
    if db_session is None:
        return [
            {"id": "c1", "name": "Allegheny Bridge Solutions", "specialty": "Bridge repair", "rating": 4.5, "location": "Pittsburgh, PA"},
            {"id": "c2", "name": "PennWater Services Inc.", "specialty": "Water main repair", "rating": 4.2, "location": "Pittsburgh, PA"},
            {"id": "c3", "name": "Three Rivers Paving Co.", "specialty": "Road resurfacing", "rating": 4.0, "location": "Pittsburgh, PA"},
        ]

    from sqlalchemy import text
    query = "SELECT * FROM contractors WHERE is_active = true AND rating >= :min_rating"
    params = {"min_rating": min_rating}

    if specialty:
        query += " AND specialty ILIKE :specialty"
        params["specialty"] = f"%{specialty}%"
    if location:
        query += " AND location ILIKE :location"
        params["location"] = f"%{location}%"

    query += " ORDER BY rating DESC LIMIT 10"
    result = await db_session.execute(text(query), params)
    return [dict(row._mapping) for row in result.fetchall()]


async def draft_rfq(
    work_order: dict[str, Any],
    contractors: list[dict[str, Any]],
) -> dict[str, Any]:
    """Draft a Request for Quotation document."""
    return {
        "rfq_id": f"RFQ-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}",
        "title": f"RFQ: {work_order.get('title', 'Infrastructure Maintenance')}",
        "scope_of_work": work_order.get("scope_of_work", ""),
        "estimated_budget": work_order.get("estimated_cost", 0),
        "response_deadline": "14 days from issue",
        "invited_contractors": [c.get("name", "") for c in contractors],
        "evaluation_criteria": {
            "cost": 40,
            "experience": 30,
            "timeline": 20,
            "safety_record": 10,
        },
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def compare_bids(bids: list[dict[str, Any]]) -> dict[str, Any]:
    """Score and rank contractor bids."""
    scored = []
    for bid in bids:
        cost_score = max(0, 100 - (bid.get("cost", 0) / 1000))
        exp_score = bid.get("experience_years", 0) * 5
        timeline_score = max(0, 100 - bid.get("timeline_days", 30) * 2)
        safety_score = bid.get("safety_rating", 3) * 20

        total = (
            cost_score * 0.4 +
            exp_score * 0.3 +
            timeline_score * 0.2 +
            safety_score * 0.1
        )
        scored.append({**bid, "score": round(total, 1)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "ranked_bids": scored,
        "recommended": scored[0] if scored else None,
    }
