"""Alert management API endpoints."""

from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from models.alert import Alert
from schemas.alert_schema import (
    AlertCreate,
    AlertAcknowledge,
    AlertResolve,
    AlertResponse,
    AlertListResponse,
)

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    municipality_id: UUID | None = None,
    asset_id: UUID | None = None,
    severity: str | None = None,
    acknowledged: bool | None = None,
    resolved: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Alert)
    count_query = select(func.count(Alert.id))

    if municipality_id:
        query = query.where(Alert.municipality_id == municipality_id)
        count_query = count_query.where(Alert.municipality_id == municipality_id)
    if asset_id:
        query = query.where(Alert.asset_id == asset_id)
        count_query = count_query.where(Alert.asset_id == asset_id)
    if severity:
        query = query.where(Alert.severity == severity)
        count_query = count_query.where(Alert.severity == severity)
    if acknowledged is not None:
        if acknowledged:
            query = query.where(Alert.acknowledged_at.isnot(None))
            count_query = count_query.where(Alert.acknowledged_at.isnot(None))
        else:
            query = query.where(Alert.acknowledged_at.is_(None))
            count_query = count_query.where(Alert.acknowledged_at.is_(None))
    if resolved is not None:
        if resolved:
            query = query.where(Alert.resolved_at.isnot(None))
            count_query = count_query.where(Alert.resolved_at.isnot(None))
        else:
            query = query.where(Alert.resolved_at.is_(None))
            count_query = count_query.where(Alert.resolved_at.is_(None))

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Alert.detected_at.desc())

    result = await db.execute(query)
    alerts = result.scalars().all()

    return AlertListResponse(
        items=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.post("", response_model=AlertResponse, status_code=201)
async def create_alert(data: AlertCreate, db: AsyncSession = Depends(get_db)):
    alert = Alert(**data.model_dump())
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: UUID, data: AlertAcknowledge, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = data.acknowledged_by
    await db.flush()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: UUID, data: AlertResolve, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.resolved_at = datetime.now(timezone.utc)
    alert.is_false_positive = data.is_false_positive
    await db.flush()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)
