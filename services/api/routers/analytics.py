"""Analytics and dashboard data API endpoints."""

from uuid import UUID
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db
from ..models.asset import Asset
from ..models.alert import Alert
from ..models.work_order import WorkOrder
from ..models.agent_run import AgentRun
from ..schemas.analytics_schema import (
    DashboardStats,
    RiskDistribution,
    AssetTypeCount,
    AnalyticsDashboard,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_dashboard(
    municipality_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    # Base filters
    asset_filter = Asset.municipality_id == municipality_id if municipality_id else True
    alert_filter = Alert.municipality_id == municipality_id if municipality_id else True
    wo_filter = WorkOrder.municipality_id == municipality_id if municipality_id else True
    ar_filter = AgentRun.municipality_id == municipality_id if municipality_id else True

    # Total assets
    total_assets = (
        await db.execute(select(func.count(Asset.id)).where(asset_filter))
    ).scalar() or 0

    # Active alerts (not resolved)
    active_alerts = (
        await db.execute(
            select(func.count(Alert.id))
            .where(alert_filter)
            .where(Alert.resolved_at.is_(None))
        )
    ).scalar() or 0

    # Pending work orders
    pending_wos = (
        await db.execute(
            select(func.count(WorkOrder.id))
            .where(wo_filter)
            .where(WorkOrder.status.in_(["draft", "pending_approval"]))
        )
    ).scalar() or 0

    # Agent runs today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    runs_today = (
        await db.execute(
            select(func.count(AgentRun.id))
            .where(ar_filter)
            .where(AgentRun.started_at >= today_start)
        )
    ).scalar() or 0

    # Assets at risk (high or critical)
    at_risk = (
        await db.execute(
            select(func.count(Asset.id))
            .where(asset_filter)
            .where(Asset.risk_level.in_(["high", "critical"]))
        )
    ).scalar() or 0

    # Average health score
    avg_health = (
        await db.execute(
            select(func.avg(Asset.current_health_score)).where(asset_filter)
        )
    ).scalar() or 0.0

    stats = DashboardStats(
        total_assets=total_assets,
        active_alerts=active_alerts,
        pending_work_orders=pending_wos,
        agent_runs_today=runs_today,
        assets_at_risk=at_risk,
        avg_health_score=round(float(avg_health), 1),
    )

    # Risk distribution
    risk_result = await db.execute(
        select(Asset.risk_level, func.count(Asset.id))
        .where(asset_filter)
        .group_by(Asset.risk_level)
    )
    risk_map = {row[0]: row[1] for row in risk_result.fetchall()}
    risk_dist = RiskDistribution(
        low=risk_map.get("low", 0),
        medium=risk_map.get("medium", 0),
        high=risk_map.get("high", 0),
        critical=risk_map.get("critical", 0),
    )

    # Asset type counts
    type_result = await db.execute(
        select(Asset.asset_type, func.count(Asset.id))
        .where(asset_filter)
        .group_by(Asset.asset_type)
    )
    type_counts = [
        AssetTypeCount(asset_type=row[0], count=row[1])
        for row in type_result.fetchall()
    ]

    return AnalyticsDashboard(
        stats=stats,
        risk_distribution=risk_dist,
        asset_type_counts=type_counts,
        recent_alert_trend=[],
    )
