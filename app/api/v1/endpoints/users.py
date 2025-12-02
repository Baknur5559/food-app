from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas import user as schemas
from app.services import user as service
from app.core.config import settings
# Импортируем модель БД напрямую для get_current_user
from app.db.models.user import User as UserModel 

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- ЗАВИСИМОСТЬ (DEPENDENCY) ---
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.get(UserModel, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- ЭНДПОИНТЫ ---

@router.post("/", response_model=schemas.User)
async def create_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await service.get_user_by_phone(db, phone=user_in.phone)
    if existing_user:
        raise HTTPException(status_code=400, detail="Телефон занят")
    return await service.create_user(db=db, user_in=user_in)

@router.get("/", response_model=List[schemas.User])
async def read_users(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_users_by_tenant(db, tenant_id)

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    user = await service.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await service.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"status": "success", "message": "User deleted"}

# --- НОВЫЙ ЭНДПОИНТ ---
@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user