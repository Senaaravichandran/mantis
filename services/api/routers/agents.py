"""Agent management API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from models.agent_run import AgentRun
from schemas.agent_schema import (
    AgentTriggerRequest,
    AgentRunResponse,
    AgentRunListResponse,
)

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


@router.get("/runs", response_model=AgentRunListResponse)
async def list_agent_runs(
    municipality_id: UUID | None = None,
    agent_type: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(AgentRun)
    count_query = select(func.count(AgentRun.id))

    if municipality_id:
        query = query.where(AgentRun.municipality_id == municipality_id)
        count_query = count_query.where(AgentRun.municipality_id == municipality_id)
    if agent_type:
        query = query.where(AgentRun.agent_type == agent_type)
        count_query = count_query.where(AgentRun.agent_type == agent_type)
    if status:
        query = query.where(AgentRun.status == status)
        count_query = count_query.where(AgentRun.status == status)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(AgentRun.started_at.desc())

    result = await db.execute(query)
    runs = result.scalars().all()

    return AgentRunListResponse(
        items=[AgentRunResponse.model_validate(r) for r in runs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/runs/{run_id}", response_model=AgentRunResponse)
async def get_agent_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentRun).where(AgentRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return AgentRunResponse.model_validate(run)


@router.post("/trigger", response_model=AgentRunResponse, status_code=201)
async def trigger_agent_run(
    data: AgentTriggerRequest, db: AsyncSession = Depends(get_db)
):
    run = AgentRun(
        municipality_id=data.municipality_id,
        agent_type="sentinel",
        trigger_type=data.trigger_type,
        trigger_ref=data.asset_id,
        status="queued",
        input_context={
            "asset_id": str(data.asset_id) if data.asset_id else None,
            "sensor_data": data.sensor_data,
            "metadata": data.metadata,
        },
    )
    db.add(run)
    await db.flush()
    await db.refresh(run)

    # TODO: publish to Kafka agent task topic for async processing
    return AgentRunResponse.model_validate(run)
