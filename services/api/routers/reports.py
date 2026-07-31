"""Report management API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_db
from ..models.document import Document

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.get("")
async def list_reports(
    municipality_id: UUID | None = None,
    doc_type: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Document).where(
        Document.doc_type.in_(["inspection_report", "agent_report", "compliance_report"])
    )
    count_query = select(func.count(Document.id)).where(
        Document.doc_type.in_(["inspection_report", "agent_report", "compliance_report"])
    )

    if municipality_id:
        query = query.where(Document.municipality_id == municipality_id)
        count_query = count_query.where(Document.municipality_id == municipality_id)
    if doc_type:
        query = query.where(Document.doc_type == doc_type)
        count_query = count_query.where(Document.doc_type == doc_type)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Document.uploaded_at.desc())

    result = await db.execute(query)
    docs = result.scalars().all()

    return {
        "items": [
            {
                "id": str(d.id),
                "title": d.title,
                "doc_type": d.doc_type,
                "asset_id": str(d.asset_id) if d.asset_id else None,
                "inspector_name": d.inspector_name,
                "inspection_date": str(d.inspection_date) if d.inspection_date else None,
                "page_count": d.page_count,
                "uploaded_at": d.uploaded_at.isoformat(),
            }
            for d in docs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
