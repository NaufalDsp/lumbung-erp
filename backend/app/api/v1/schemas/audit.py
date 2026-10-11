from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    actor_id: int | None
    entity: str
    entity_id: int
    action: str
    from_status: str | None
    to_status: str | None
    diff: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
