from typing import List, Optional
from pydantic import BaseModel

# --- КАТЕГОРИИ ---
class CategoryBase(BaseModel):
    name: str
    sort_order: int = 0

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    tenant_id: int
    
    class Config:
        from_attributes = True

# --- ТОВАРЫ ---
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_active: bool = True
    category_id: int

class MenuItemCreate(MenuItemBase):
    pass

# НОВАЯ СХЕМА ДЛЯ ОБНОВЛЕНИЯ
class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None

class MenuItem(MenuItemBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True