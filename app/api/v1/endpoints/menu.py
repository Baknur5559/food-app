import shutil
import uuid
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.schemas import menu as schemas
from app.services import menu as service
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- КАТЕГОРИИ ---
@router.post("/categories/", response_model=schemas.Category)
async def create_category(category: schemas.CategoryCreate, db: AsyncSession = Depends(get_db), tenant_id: int = 1):
    return await service.create_category(db, category, tenant_id)

@router.get("/categories/", response_model=List[schemas.Category])
async def read_categories(db: AsyncSession = Depends(get_db), tenant_id: int = 1):
    return await service.get_categories(db, tenant_id)

# --- ТОВАРЫ ---
@router.post("/items/", response_model=schemas.MenuItem)
async def create_item(
    tenant_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    is_active: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    image_url = None
    if file:
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"app/static/images/{unique_filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_url = f"http://213.148.7.107:8002/static/images/{unique_filename}"

    item_in = schemas.MenuItemCreate(
        name=name, price=price, description=description, category_id=category_id, is_active=is_active, image_url=image_url
    )
    return await service.create_menu_item(db, item_in, tenant_id)

@router.get("/items/{category_id}", response_model=List[schemas.MenuItem])
async def read_items(category_id: int, db: AsyncSession = Depends(get_db), tenant_id: int = 1):
    return await service.get_items_by_category(db, category_id, tenant_id)

# --- НОВЫЕ РУЧКИ (UPDATE & DELETE) ---

@router.put("/items/{item_id}", response_model=schemas.MenuItem)
async def update_item(
    item_id: int,
    name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None), # Pydantic сам попробует конвертировать
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    image_url = None
    if file:
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"app/static/images/{unique_filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_url = f"http://213.148.7.107:8002/static/images/{unique_filename}"

    # Создаем объект обновления
    update_data = schemas.MenuItemUpdate(
        name=name,
        price=price,
        description=description,
        category_id=category_id,
        is_active=is_active,
        image_url=image_url
    )
    
    # ВАЖНО: Если is_active пришел как None (не передали), мы его не трогаем.
    # Если пришел как False/True - обновляем.
    
    item = await service.update_menu_item(db, item_id, update_data)
    
    # Если вдруг в базе is_active стало NULL (хотя не должно), вернем False
    if item and item.is_active is None:
        item.is_active = False
        
    return item

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    return await service.delete_menu_item(db, item_id)