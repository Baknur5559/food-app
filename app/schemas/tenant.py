from typing import Optional
from pydantic import BaseModel
from datetime import date

class TenantBase(BaseModel):
    name: str
    slug: str
    custom_domain: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    bot_username: Optional[str] = None # <--- НОВОЕ
    active_until: Optional[date] = None
    branch_limit: int = 1
    owner_phone_contact: Optional[str] = None

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    custom_domain: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    bot_username: Optional[str] = None # <--- НОВОЕ
    active_until: Optional[date] = None
    branch_limit: Optional[int] = None
    is_active: Optional[bool] = None

class Tenant(TenantBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True