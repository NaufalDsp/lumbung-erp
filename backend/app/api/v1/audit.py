from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthenticatedUser, require_permission
from app.api.v1.schemas.audit import AuditLogResponse
from app.api.v1.schemas.master import PaginatedResponse
from app.core.permissions import Permission
from app.models.audit import AuditLog
from app.models.database import get_db

router = APIRouter(prefix="/audit", tags=["Audit Log"])


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[AuthenticatedUser, Depends(require_permission(Permission.VIEW_AUDIT_LOG))],
    entity: str | None = Query(
        None, description="Filter entitas (product, customer, sales_order, dll)"),
    entity_id: int | None = Query(
        None, description="Filter ID spesifik entitas"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
) -> PaginatedResponse[AuditLogResponse]:
    """Retrieves immutable audit logs ordered by newest first. Restricted to Admin."""
    stmt = select(AuditLog)
    count_stmt = select(func.count(AuditLog.id))

    if entity:
        stmt = stmt.where(AuditLog.entity == entity.strip().lower())
        count_stmt = count_stmt.where(
            AuditLog.entity == entity.strip().lower())

    if entity_id is not None:
        stmt = stmt.where(AuditLog.entity_id == entity_id)
        count_stmt = count_stmt.where(AuditLog.entity_id == entity_id)

    total = (await db.execute(count_stmt)).scalar_one() or 0
    offset = (page - 1) * limit
    stmt = stmt.order_by(AuditLog.created_at.desc(),
                         AuditLog.id.desc()).offset(offset).limit(limit)

    result = await db.execute(stmt)
    items = [AuditLogResponse.model_validate(
        log) for log in result.scalars().all()]

    return PaginatedResponse(items=items, total=total, page=page, limit=limit)
