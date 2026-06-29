from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import require_roles
from app.models import AuditLog, User, UserRole
from app.schemas.misc import AuditLogOut

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogOut])
def list_audit(
    limit: int = Query(100, le=500),
    entity_type: str | None = None,
    db: Session = Depends(get_db),
    # Audit trail is CEO-only.
    user: User = Depends(require_roles(UserRole.ADMIN_CEO)),
):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    return q.order_by(AuditLog.created_at.desc()).limit(limit).all()
