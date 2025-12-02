from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.tenant import Tenant
from app.db.models.order import Order
from app.db.models.client import Client
from aiogram import Bot
from app.schemas.order import Order as OrderSchema

# Эта функция обрабатывает входящее сообщение от Telegram
async def process_telegram_update(token: str, update: dict, db: AsyncSession):
    # 1. Проверяем, существует ли ресторан с таким токеном
    # (В реальной нагрузке это стоит кэшировать в Redis)
    result = await db.execute(select(Tenant).filter(Tenant.telegram_bot_token == token))
    tenant = result.scalars().first()
    
    if not tenant:
        return {"status": "error", "msg": "Tenant not found"}

    # Инициализируем бота "на лету"
    bot = Bot(token=token)

    try:
        # Разбираем JSON от Телеграма
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        contact = message.get("contact")
        
        if not chat_id:
            return {"status": "ignored", "msg": "No chat_id"}

        # --- СЦЕНАРИЙ 1: Нажали СТАРТ с параметром (DeepLink) ---
        if text.startswith("/start order_"):
            # Вытаскиваем ID заказа: "/start order_15" -> "15"
            order_id_str = text.split("_")[1]
            if order_id_str.isdigit():
                order_id = int(order_id_str)
                
                # Ищем заказ
                order = await db.get(Order, order_id)
                if order and order.tenant_id == tenant.id:
                    # Приветствуем клиента
                    await bot.send_message(
                        chat_id,
                        f"👋 Здравствуйте, {order.client_name}!\n"
                        f"Вижу ваш заказ №{order.id} на сумму {order.total_amount} с.\n\n"
                        f"Чтобы получать уведомления о статусе, пожалуйста, нажмите кнопку ниже 👇",
                        reply_markup={
                            "keyboard": [[{
                                "text": "📱 Подтвердить номер телефона",
                                "request_contact": True # Магия Телеграма
                            }]],
                            "resize_keyboard": True,
                            "one_time_keyboard": True
                        }
                    )
                    return {"status": "ok", "msg": "Welcome sent"}

        # --- СЦЕНАРИЙ 2: Клиент отправил КОНТАКТ ---
        if contact:
            phone_number = contact.get("phone_number")
            # Чистим номер (убираем +, если есть)
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            
            # Ищем клиента в базе
            client_res = await db.execute(select(Client).filter(Client.phone == clean_phone))
            client = client_res.scalars().first()
            
            if client:
                # ПРИВЯЗЫВАЕМ TELEGRAM ID!
                client.telegram_chat_id = chat_id
                client.telegram_username = message.get("from", {}).get("username")
                await db.commit()
                
                await bot.send_message(
                    chat_id,
                    "✅ Отлично! Ваш профиль привязан.\nТеперь вы будете получать статусы заказов здесь.",
                    reply_markup={"remove_keyboard": True}
                )
                return {"status": "ok", "msg": "Linked"}
            else:
                await bot.send_message(chat_id, "Хм, я не нашел заказов с таким номером. Попробуйте сделать заказ на сайте.")

        return {"status": "ok", "msg": "Unhandled message"}

    except Exception as e:
        print(f"BOT ERROR: {e}")
        return {"status": "error", "msg": str(e)}
    finally:
        await bot.session.close()