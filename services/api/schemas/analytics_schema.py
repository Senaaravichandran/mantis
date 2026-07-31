"""Pydantic schemas for Analytics/Dashboard API endpoints."""

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_assets: int = 0
    active_alerts: int = 0
    pending_work_orders: int = 0
    agent_runs_today: int = 0
    assets_at_risk: int = 0
    avg_health_score: float = 0.0


class RiskDistribution(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class AssetTypeCount(BaseModel):
    asset_type: str
    count: int


class AlertTrend(BaseModel):
    date: str
    count: int
    severity: str


class AnalyticsDashboard(BaseModel):
    stats: DashboardStats
    risk_distribution: RiskDistribution
    asset_type_counts: list[AssetTypeCount]
    recent_alert_trend: list[AlertTrend]
