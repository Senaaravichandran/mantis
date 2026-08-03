"""Sensor data API endpoints."""

from uuid import UUID
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from models.sensor_reading import SensorReading
from schemas.sensor_schema import (
    SensorReadingCreate,
    SensorReadingResponse,
    SensorHourlyResponse,
)

router = APIRouter(prefix="/api/v1/sensors", tags=["Sensors"])


@router.post("", response_model=SensorReadingResponse, status_code=201)
async def ingest_sensor_reading(
    data: SensorReadingCreate, db: AsyncSession = Depends(get_db)
):
    reading = SensorReading(
        time=data.time or datetime.now(timezone.utc),
        asset_id=data.asset_id,
        sensor_id=data.sensor_id,
        sensor_type=data.sensor_type,
        value=data.value,
        unit=data.unit,
        quality_flag=data.quality_flag,
        raw_payload=data.raw_payload,
    )
    db.add(reading)
    await db.flush()
    return SensorReadingResponse.model_validate(reading)


@router.post("/batch", status_code=201)
async def ingest_batch(
    readings: list[SensorReadingCreate], db: AsyncSession = Depends(get_db)
):
    objects = [
        SensorReading(
            time=r.time or datetime.now(timezone.utc),
            asset_id=r.asset_id,
            sensor_id=r.sensor_id,
            sensor_type=r.sensor_type,
            value=r.value,
            unit=r.unit,
            quality_flag=r.quality_flag,
            raw_payload=r.raw_payload,
        )
        for r in readings
    ]
    db.add_all(objects)
    return {"ingested": len(objects)}


@router.get("/history", response_model=list[SensorReadingResponse])
async def get_sensor_history(
    asset_id: UUID,
    sensor_type: str | None = None,
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    query = (
        select(SensorReading)
        .where(SensorReading.asset_id == asset_id)
        .where(SensorReading.time >= cutoff)
    )
    if sensor_type:
        query = query.where(SensorReading.sensor_type == sensor_type)
    query = query.order_by(SensorReading.time.desc()).limit(limit)

    result = await db.execute(query)
    readings = result.scalars().all()
    return [SensorReadingResponse.model_validate(r) for r in readings]


@router.get("/hourly", response_model=list[SensorHourlyResponse])
async def get_hourly_aggregates(
    asset_id: UUID,
    sensor_type: str | None = None,
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sql = text("""
        SELECT bucket, asset_id, sensor_type, avg_val, max_val, min_val, reading_count
        FROM sensor_hourly
        WHERE asset_id = :asset_id AND bucket >= :cutoff
        ORDER BY bucket DESC
    """)
    params = {"asset_id": str(asset_id), "cutoff": cutoff}
    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [
        SensorHourlyResponse(
            bucket=row.bucket,
            asset_id=row.asset_id,
            sensor_type=row.sensor_type,
            avg_val=row.avg_val,
            max_val=row.max_val,
            min_val=row.min_val,
            reading_count=row.reading_count,
        )
        for row in rows
    ]
