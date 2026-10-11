from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def record_audit_log(
    db: AsyncSession,
    entity: str,
    entity_id: int,
    action: str,
    actor_id: int | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    diff: dict[str, Any] | None = None,
) -> AuditLog:
    """Records an immutable audit log entry within the current transaction."""
    entry = AuditLog(
        entity=entity,
        entity_id=entity_id,
        action=action,
        actor_id=actor_id,
        from_status=from_status,
        to_status=to_status,
        diff=diff,
    )
    db.add(entry)
    return entry
