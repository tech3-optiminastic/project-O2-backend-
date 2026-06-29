from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class AgentBase(BaseModel):
    business_name: str
    legal_name: str | None = None
    contact_person: str | None = None
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    gst_number: str | None = None
    pan: str | None = None
    bank_account_holder: str | None = None
    bank_name: str | None = None
    account_number: str | None = None
    ifsc_code: str | None = None
    commission_rate: float = 0.0
    notes: str | None = None


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    business_name: str | None = None
    legal_name: str | None = None
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    gst_number: str | None = None
    pan: str | None = None
    bank_account_holder: str | None = None
    bank_name: str | None = None
    account_number: str | None = None
    ifsc_code: str | None = None
    commission_rate: float | None = None
    is_active: bool | None = None
    notes: str | None = None


class AgentOut(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
