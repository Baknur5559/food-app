from sqlalchemy.ext.asyncio import AsyncSession
from app.services import user as user_service
from app.core.security import verify_password

async def authenticate_user(db: AsyncSession, phone: str, password: str):
    """Проверяет логин и пароль. Возвращает юзера или None."""
    # 1. Ищем пользователя по телефону
    user = await user_service.get_user_by_phone(db, phone=phone)
    if not user:
        return None
    
    # 2. Проверяем пароль
    if not verify_password(password, user.hashed_password):
        return None
        
    return user