from sqlalchemy import Column, Integer, String, Boolean, Date
from app.db.base_class import Base
from datetime import date

class Tenant(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    
    # Технические настройки
    custom_domain = Column(String, nullable=True, unique=True)
    telegram_bot_token = Column(String, nullable=True) # Токен (Секретно!)
    bot_username = Column(String, nullable=True) # Имя бота для ссылки (t.me/Name) <--- НОВОЕ
    
    # Биллинг и Лимиты
    is_active = Column(Boolean, default=True)
    active_until = Column(Date, nullable=True)
    branch_limit = Column(Integer, default=1)
    
    # Контакты владельца
    owner_phone_contact = Column(String, nullable=True)