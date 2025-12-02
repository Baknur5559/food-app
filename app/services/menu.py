from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.menu import Category, MenuItem
from app.schemas.menu import CategoryCreate, MenuItemCreate, MenuItemUpdate

# --- КАТЕГОРИИ ---
async def create_category(db: AsyncSession, category: CategoryCreate, tenant_id: int):
    db_category = Category(**category.model_dump(), tenant_id=tenant_id)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def get_categories(db: AsyncSession, tenant_id: int):
    result = await db.execute(
        select(Category)
        .filter(Category.tenant_id == tenant_id)
        .order_by(Category.sort_order)
    )
    return result.scalars().all()

# --- ТОВАРЫ ---
async def create_menu_item(db: AsyncSession, item: MenuItemCreate, tenant_id: int):
    db_item = MenuItem(**item.model_dump(), tenant_id=tenant_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_items_by_category(db: AsyncSession, category_id: int, tenant_id: int):
    result = await db.execute(
        select(MenuItem)
        .filter(MenuItem.category_id == category_id, MenuItem.tenant_id == tenant_id)
    )
    return result.scalars().all()

# НОВЫЕ ФУНКЦИИ
async def update_menu_item(db: AsyncSession, item_id: int, item_in: MenuItemUpdate):
    item = await db.get(MenuItem, item_id)
    if not item:
        return None
    
    # Получаем данные, но фильтруем всё, что None (пустоту)
    # Это ГЛАВНОЕ исправление:
    update_data = item_in.model_dump(exclude_unset=True)
    # Дополнительная чистка: убираем ключи, где значение None
    update_data = {k: v for k, v in update_data.items() if v is not None}

    for key, value in update_data.items():
        setattr(item, key, value)

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

async def delete_menu_item(db: AsyncSession, item_id: int):
    item = await db.get(MenuItem, item_id)
    if item:
        await db.delete(item)
        await db.commit()
    return item