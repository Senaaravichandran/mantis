"""Work order management API endpoints."""

from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db
from ..models.work_order import WorkOrder
from ..schemas.workorder_schema import (
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkOrderApprove,
    WorkOrderResponse,
    WorkOrderListResponse,
)

router = APIRouter(prefix="/api/v1/workorders", tags=["Work Orders"])


@router.get("", response_model=WorkOrderListResponse)
async def list_work_orders(
    municipality_id: UUID | None = None,
    asset_id: UUID | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(WorkOrder)
    count_query = select(func.count(WorkOrder.id))

    if municipality_id:
        query = query.where(WorkOrder.municipality_id == municipality_id)
        count_query = count_query.where(WorkOrder.municipality_id == municipality_id)
    if asset_id:
        query = query.where(WorkOrder.asset_id == asset_id)
        count_query = count_query.where(WorkOrder.asset_id == asset_id)
    if status:
        query = query.where(WorkOrder.status == status)
        count_query = count_query.where(WorkOrder.status == status)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(WorkOrder.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().all()

    return WorkOrderListResponse(
        items=[WorkOrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}", response_model=WorkOrderResponse)
async def get_work_order(order_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkOrder).where(WorkOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return WorkOrderResponse.model_validate(order)


@router.post("", response_model=WorkOrderResponse, status_code=201)
async def create_work_order(data: WorkOrderCreate, db: AsyncSession = Depends(get_db)):
    order = WorkOrder(**data.model_dump())
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return WorkOrderResponse.model_validate(order)


@router.patch("/{order_id}", response_model=WorkOrderResponse)
async def update_work_order(
    order_id: UUID, data: WorkOrderUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(WorkOrder).where(WorkOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(order, key, value)

    await db.flush()
    await db.refresh(order)
    return WorkOrderResponse.model_validate(order)


@router.post("/{order_id}/approve", response_model=WorkOrderResponse)
async def approve_work_order(
    order_id: UUID, data: WorkOrderApprove, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(WorkOrder).where(WorkOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")
    order.status = "approved"
    order.approved_by = data.approved_by
    order.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(order)
    return WorkOrderResponse.model_validate(order)
