from sqlalchemy import String, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class Agent(Base, TimestampMixin):
    """A referral agent who introduces clients and earns a commission on their invoicing.

    One agent can bring in many clients (Client.agent_id) and is credited on the
    invoices raised for those clients (ClientInvoice.agent_id).
    """

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_name: Mapped[str] = mapped_column(String(200), index=True)
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    gst_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    pan: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Bank details — used to pay out the agent's commission.
    bank_account_holder: Mapped[str | None] = mapped_column(String(160), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    account_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ifsc_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    commission_rate: Mapped[float] = mapped_column(Float, default=0.0)  # percent of invoiced value
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Deleting an agent clears the link on clients/invoices (FK is nullable, ON DELETE SET NULL)
    # rather than cascading the delete — the business records must survive.
    clients: Mapped[list["Client"]] = relationship(  # noqa: F821
        back_populates="agent", passive_deletes=True
    )
    invoices: Mapped[list["ClientInvoice"]] = relationship(  # noqa: F821
        back_populates="agent", passive_deletes=True
    )
