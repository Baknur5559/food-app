from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal
from app.db.models.order import Order, OrderItem
from app.db.models.menu import MenuItem
from app.schemas import order as schemas
from app.api.v1.endpoints.users import get_current_user
from app.db.models.user import User

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 1. Получить список заказов
@router.get("/", response_model=List[schemas.Order])
async def read_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.tenant_id:
        return []

    result = await db.execute(
        select(Order)
        .filter(Order.tenant_id == current_user.tenant_id)
        .order_by(desc(Order.created_at))
        .options(selectinload(Order.items))
    )
    return result.scalars().all()

# 2. Обновить статус или данные клиента
@router.patch("/{order_id}", response_model=schemas.Order)
async def update_order(
    order_id: int,
    status: Optional[str] = Body(None),
    client_name: Optional[str] = Body(None),
    client_phone: Optional[str] = Body(None),
    delivery_address: Optional[str] = Body(None),
    comment: Optional[str] = Body(None),
    order_type: Optional[str] = Body(None), # <--- ДОБАВИЛИ ЭТО ПОЛЕ
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Order).filter(Order.id == order_id).options(selectinload(Order.items))
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    
    if order.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Это чужой заказ")

    # Обновляем поля, если они пришли
    if status: order.status = status
    if client_name: order.client_name = client_name
    if client_phone: order.client_phone = client_phone
    if delivery_address: order.delivery_address = delivery_address
    if comment: order.comment = comment
    if order_type: order.order_type = order_type # <--- ОБНОВЛЯЕМ В БАЗЕ
        
    await db.commit()
    await db.refresh(order)
    return order

# 3. Удалить позицию из заказа
@router.delete("/{order_id}/items/{item_id}")
async def delete_order_item(
    order_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Order).filter(Order.id == order_id))
    order = result.scalars().first()
    
    if not order or order.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    item_result = await db.execute(select(OrderItem).filter(OrderItem.id == item_id, OrderItem.order_id == order_id))
    item = item_result.scalars().first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Позиция не найдена")

    order.total_amount -= (item.price * item.quantity)
    
    await db.delete(item)
    await db.commit()
    return {"status": "deleted", "new_total": order.total_amount}

# 4. Добавить позицию в заказ
@router.post("/{order_id}/items")
async def add_order_item(
    order_id: int,
    menu_item_id: int = Body(...),
    quantity: int = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Order).filter(Order.id == order_id))
    order = result.scalars().first()
    
    if not order or order.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    menu_item = await db.get(MenuItem, menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    new_item = OrderItem(
        order_id=order_id,
        menu_item_id=menu_item_id,
        name=menu_item.name,
        price=menu_item.price,
        quantity=quantity
    )
    
    order.total_amount += (menu_item.price * quantity)
    
    db.add(new_item)
    await db.commit()
    
    return {"status": "added", "new_total": order.total_amount}