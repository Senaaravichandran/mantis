"""Database query tools for MANTIS agents."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID


async def query_sensor_history(
    asset_id: str, days: int = 30, db_session=None
) -> list[dict[str, Any]]:
    """Query sensor reading history for an asset."""
    if db_session is None:
        return _mock_sensor_history(asset_id, days)

    from sqlalchemy import text
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db_session.execute(
        text("""
            SELECT time, sensor_id, sensor_type, value, unit, quality_flag
            FROM sensor_readings
            WHERE asset_id = :asset_id AND time >= :cutoff
            ORDER BY time DESC
            LIMIT 5000
        """),
        {"asset_id": asset_id, "cutoff": cutoff},
    )
    return [dict(row._mapping) for row in result.fetchall()]


async def get_asset_details(asset_id: str, db_session=None) -> dict[str, Any]:
    """Get full asset details including metadata."""
    if db_session is None:
        return {
            "id": asset_id,
            "name": "Sample Asset",
            "asset_type": "bridge",
            "health_score": 65.0,
            "risk_level": "medium",
            "material": "Steel",
            "age_years": 40,
        }

    from sqlalchemy import text
    result = await db_session.execute(
        text("SELECT * FROM assets WHERE id = :id"),
        {"id": asset_id},
    )
    row = result.fetchone()
    return dict(row._mapping) if row else {}


async def get_asset_alerts(
    asset_id: str, days: int = 90, db_session=None
) -> list[dict[str, Any]]:
    """Get recent alerts for an asset."""
    if db_session is None:
        return []

    from sqlalchemy import text
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db_session.execute(
        text("""
            SELECT id, severity, title, description, risk_score, detected_at
            FROM alerts
            WHERE asset_id = :asset_id AND detected_at >= :cutoff
            ORDER BY detected_at DESC
        """),
        {"asset_id": asset_id, "cutoff": cutoff},
    )
    return [dict(row._mapping) for row in result.fetchall()]


async def create_alert_record(alert_data: dict, db_session=None) -> str:
    """Create a new alert record in the database."""
    if db_session is None:
        return "mock-alert-id"

    from sqlalchemy import text
    from uuid import uuid4
    alert_id = str(uuid4())
    await db_session.execute(
        text("""
            INSERT INTO alerts (id, asset_id, municipality_id, severity, anomaly_type,
                title, description, agent_reasoning, confidence_score, risk_score,
                affected_sensors, weather_context)
            VALUES (:id, :asset_id, :municipality_id, :severity, :anomaly_type,
                :title, :description, :reasoning, :confidence, :risk_score,
                :sensors, :weather)
        """),
        {
            "id": alert_id,
            **alert_data,
        },
    )
    return alert_id


async def create_work_order_record(wo_data: dict, db_session=None) -> str:
    """Create a new work order record."""
    if db_session is None:
        return "mock-wo-id"

    from sqlalchemy import text
    from uuid import uuid4
    wo_id = str(uuid4())
    await db_session.execute(
        text("""
            INSERT INTO work_orders (id, asset_id, municipality_id, status, priority,
                title, scope_of_work, estimated_cost, generated_by)
            VALUES (:id, :asset_id, :municipality_id, 'draft', :priority,
                :title, :scope, :cost, 'agent')
        """),
        {"id": wo_id, **wo_data},
    )
    return wo_id


def _mock_sensor_history(asset_id: str, days: int) -> list[dict]:
    """Generate mock sensor data for testing without a database."""
    import random
    history = []
    now = datetime.now(timezone.utc)
    for day in range(days):
        for hour in [0, 6, 12, 18]:
            history.append({
                "time": (now - timedelta(days=day, hours=hour)).isoformat(),
                "sensor_id": f"{asset_id[:8]}_vibration",
                "sensor_type": "vibration",
                "value": round(random.gauss(2.5, 0.5), 3),
                "unit": "mm/s",
                "quality_flag": "good",
            })
    return history
