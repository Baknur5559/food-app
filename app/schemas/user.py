from typing import Optional
from pydantic import BaseModel

# Базовая схема
class UserBase(BaseModel):
    phone: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

# Создание
class UserCreate(UserBase):
    password: str
    tenant_id: Optional[int] = None

# Обновление (НОВОЕ)
class UserUpdate(BaseModel):
    phone: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None # Если пустой - не меняем
    is_active: Optional[bool] = None

# Чтение
class User(UserBase):
    id: int
    tenant_id: Optional[int]

    class Config:
        from_attributes = True