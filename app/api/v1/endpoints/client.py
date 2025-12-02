from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.tenant import Tenant
from app.db.models.menu import Category, MenuItem
from app.db.models.order import Order, OrderItem
from app.db.models.client import Client # <-- Импорт
from app.schemas import client as client_schemas
from app.schemas import order as order_schemas

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- МЕНЮ ---
@router.get("/{slug}", response_model=client_schemas.RestaurantPublic)
async def get_restaurant_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tenant).filter(Tenant.slug == slug))
    tenant = result.scalars().first()
    
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=404, detail="Ресторан не найден")

    cat_result = await db.execute(
        select(Category).filter(Category.tenant_id == tenant.id).order_by(Category.sort_order)
    )
    categories = cat_result.scalars().all()

    categories_with_items = []
    for cat in categories:
        items_result = await db.execute(
            select(MenuItem).filter(MenuItem.category_id == cat.id, MenuItem.is_active == True)
        )
        items = items_result.scalars().all()
        if items:
            cat_data = client_schemas.CategoryWithItems(
                id=cat.id, name=cat.name, sort_order=cat.sort_order, tenant_id=cat.tenant_id, items=items
            )
            categories_with_items.append(cat_data)

    return {
        "id": tenant.id,
        "name": tenant.name,
        "slug": tenant.slug,
        "custom_domain": tenant.custom_domain,
        # Токен НЕ отдаем!
        "bot_username": tenant.bot_username, # <--- Отдаем имя бота
        "categories": categories_with_items
    }

# --- СОЗДАНИЕ ЗАКАЗА (Умная версия) ---
@router.post("/orders", response_model=order_schemas.OrderCreated)
async def create_order(
    order_in: order_schemas.OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Поиск или создание КЛИЕНТА
    # Нормализуем телефон (убираем пробелы, скобки)
    clean_phone = ''.join(filter(str.isdigit, order_in.client_phone))
    
    client_result = await db.execute(select(Client).filter(Client.phone == clean_phone))
    client = client_result.scalars().first()
    
    if not client:
        # Создаем нового
        client = Client(phone=clean_phone, name=order_in.client_name)
        db.add(client)
        await db.commit()
        await db.refresh(client)
    else:
        # Обновляем имя, если изменилось (опционально)
        if order_in.client_name and client.name != order_in.client_name:
            client.name = order_in.client_name
            db.add(client)
            await db.commit()

    # 2. Собираем товары
    total_amount = 0.0
    db_items = []
    
    for item_in in order_in.items:
        menu_item = await db.get(MenuItem, item_in.menu_item_id)
        if not menu_item: continue
            
        line_total = menu_item.price * item_in.quantity
        total_amount += line_total
        
        db_item = OrderItem(
            menu_item_id=menu_item.id,
            name=menu_item.name,
            price=menu_item.price,
            quantity=item_in.quantity
        )
        db_items.append(db_item)

    # 3. Создаем Заказ
    db_order = Order(
        tenant_id=order_in.tenant_id,
        client_id=client.id, # <-- ПРИВЯЗКА К КЛИЕНТУ
        client_name=order_in.client_name,
        client_phone=clean_phone,
        delivery_address=order_in.delivery_address,
        order_type=order_in.order_type,
        payment_method=order_in.payment_method,
        comment=order_in.comment,
        total_amount=total_amount,
        status="new",
        source="web", # Источник - сайт
        is_paid=False
    )
    
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    for item in db_items:
        item.order_id = db_order.id
        db.add(item)
    
    await db.commit()
    await db.refresh(db_order)
    
    return db_order