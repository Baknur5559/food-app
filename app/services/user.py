from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

async def create_user(db: AsyncSession, user_in: UserCreate):
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        phone=user_in.phone,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
        tenant_id=user_in.tenant_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_phone(db: AsyncSession, phone: str):
    result = await db.execute(select(User).filter(User.phone == phone))
    return result.scalars().first()

async def get_users_by_tenant(db: AsyncSession, tenant_id: int):
    result = await db.execute(select(User).filter(User.tenant_id == tenant_id))
    return result.scalars().all()

# --- НОВЫЕ ФУНКЦИИ ---

async def delete_user(db: AsyncSession, user_id: int):
    user = await db.get(User, user_id)
    if user:
        await db.delete(user)
        await db.commit()
    return user

async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate):
    user = await db.get(User, user_id)
    if not user:
        return None
    
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Если пришел новый пароль - хешируем его
    if 'password' in update_data and update_data['password']:
        update_data['hashed_password'] = get_password_hash(update_data['password'])
        del update_data['password'] # Удаляем чистый пароль
    
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user