from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services import telegram as telegram_service

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Этот адрес мы потом скажем Телеграму
# {token} в URL позволяет нам понять, КАКОМУ из 100 ресторанов пишут
@router.post("/webhook/{token}")
async def telegram_webhook(
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Получаем JSON от Телеграма
    update_data = await request.json()
    
    # Отправляем в сервис на обработку
    result = await telegram_service.process_telegram_update(token, update_data, db)
    
    return result