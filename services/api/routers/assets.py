"""Asset management API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

from ..database.connection import get_db
from ..models.asset import Asset
from ..schemas.asset_schema import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
)

router = APIRouter(prefix="/api/v1/assets", tags=["Assets"])


def _asset_to_response(asset: Asset) -> AssetResponse:
    return AssetResponse(
        id=asset.id,
        municipality_id=asset.municipality_id,
        name=asset.name,
        asset_type=asset.asset_type,
        latitude=None,
        longitude=None,
        installation_date=asset.installation_date,
        design_life_years=asset.design_life_years,
        material=asset.material,
        manufacturer=asset.manufacturer,
        diameter_mm=asset.diameter_mm,
        span_m=asset.span_m,
        last_inspection_date=asset.last_inspection_date,
        next_inspection_date=asset.next_inspection_date,
        current_health_score=asset.current_health_score,
        risk_level=asset.risk_level,
        fhwa_id=asset.fhwa_id,
        epa_id=asset.epa_id,
        metadata=asset.metadata_json or {},
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


@router.get("", response_model=AssetListResponse)
async def list_assets(
    municipality_id: UUID | None = None,
    asset_type: str | None = None,
    risk_level: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Asset)
    count_query = select(func.count(Asset.id))

    if municipality_id:
        query = query.where(Asset.municipality_id == municipality_id)
        count_query = count_query.where(Asset.municipality_id == municipality_id)
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
        count_query = count_query.where(Asset.asset_type == asset_type)
    if risk_level:
        query = query.where(Asset.risk_level == risk_level)
        count_query = count_query.where(Asset.risk_level == risk_level)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Asset.created_at.desc())

    result = await db.execute(query)
    assets = result.scalars().all()

    return AssetListResponse(
        items=[_asset_to_response(a) for a in assets],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return _asset_to_response(asset)


@router.post("", response_model=AssetResponse, status_code=201)
async def create_asset(data: AssetCreate, db: AsyncSession = Depends(get_db)):
    asset = Asset(
        municipality_id=data.municipality_id,
        name=data.name,
        asset_type=data.asset_type,
        geom=ST_SetSRID(ST_MakePoint(data.longitude, data.latitude), 4326),
        installation_date=data.installation_date,
        design_life_years=data.design_life_years,
        material=data.material,
        manufacturer=data.manufacturer,
        diameter_mm=data.diameter_mm,
        span_m=data.span_m,
        fhwa_id=data.fhwa_id,
        epa_id=data.epa_id,
        metadata_json=data.metadata,
    )
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    return _asset_to_response(asset)


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: UUID, data: AssetUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    update_data = data.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["metadata_json"] = update_data.pop("metadata")
    for key, value in update_data.items():
        setattr(asset, key, value)

    await db.flush()
    await db.refresh(asset)
    return _asset_to_response(asset)


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    await db.delete(asset)

# Asset retrieval logic
