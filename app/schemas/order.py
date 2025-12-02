from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# --- Товар в корзине ---
class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderItem(OrderItemCreate):
    id: int
    name: str
    price: float
    
    class Config:
        from_attributes = True

# --- Создание заказа (от клиента) ---
class OrderCreate(BaseModel):
    tenant_id: int
    client_name: str
    client_phone: str
    delivery_address: Optional[str] = None
    order_type: str = "delivery" # delivery или pickup
    payment_method: str = "cash"
    comment: Optional[str] = None
    items: List[OrderItemCreate]

# --- Просмотр заказа (для админа) ---
class Order(OrderCreate):
    id: int
    status: str
    total_amount: float
    delivery_price: float
    created_at: datetime
    items: List[OrderItem]

    class Config:
        from_attributes = True

# Упрощенная схема для ответа при создании (чтобы не грузить items)
class OrderCreated(BaseModel):
    id: int
    status: str
    total_amount: float
    
    class Config:
        from_attributes = True