"""CEO payment approval state machine (single-level: CEO sign-off)."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import PaymentApproval, ApprovalAction, ApprovalStatus, User, UserRole


# Allowed transitions: status -> {action: next_status}
def _record(db: Session, approval: PaymentApproval, user: User, decision: str, comments: str | None):
    db.add(
        ApprovalAction(
            approval_id=approval.id,
            approver_name=user.name,
            approver_role=user.role.value,
            decision=decision,
            comments=comments,
        )
    )


def submit_for_approval(db: Session, approval: PaymentApproval, user: User) -> None:
    """Submit a request straight to the CEO (CFO approval is not required)."""
    if approval.status not in {ApprovalStatus.DRAFT, ApprovalStatus.CEO_REJECTED}:
        raise HTTPException(400, f"Cannot submit from status '{approval.status.value}'")
    approval.status = ApprovalStatus.SUBMITTED_CEO
    _record(db, approval, user, "Submitted for CEO Approval", None)


def ceo_decision(db: Session, approval: PaymentApproval, user: User, approve: bool, comment: str | None) -> None:
    if user.role != UserRole.ADMIN_CEO:
        raise HTTPException(403, "Only the CEO can take this action")
    if approval.status != ApprovalStatus.SUBMITTED_CEO:
        raise HTTPException(400, "Approval is not awaiting CEO decision")
    approval.ceo_comment = comment
    if approve:
        approval.status = ApprovalStatus.CEO_APPROVED
        _record(db, approval, user, "CEO Approved", comment)
        # Both approvals complete -> payment is ready for release.
        approval.status = ApprovalStatus.PAYMENT_READY
        _record(db, approval, user, "Payment Ready", None)
    else:
        approval.status = ApprovalStatus.CEO_REJECTED
        _record(db, approval, user, "CEO Rejected", comment)


def release_payment(db: Session, approval: PaymentApproval, user: User, payment_reference: str) -> None:
    if approval.status != ApprovalStatus.PAYMENT_READY:
        raise HTTPException(400, "Payment is not ready for release (requires CFO + CEO approval)")
    reference = (payment_reference or "").strip()
    if not reference:
        raise HTTPException(400, "A payment reference ID is required to complete the payment")
    approval.payment_reference = reference
    approval.status = ApprovalStatus.PAYMENT_RELEASED
    approval.released_at = datetime.now(timezone.utc)
    _record(db, approval, user, "Payment Released", f"Reference: {reference}")


def mark_verified(db: Session, approval: PaymentApproval, user: User) -> None:
    if approval.status != ApprovalStatus.PAYMENT_RELEASED:
        raise HTTPException(400, "Only a released payment can be verified")
    approval.status = ApprovalStatus.PAYMENT_VERIFIED
    _record(db, approval, user, "Payment Verified", None)
