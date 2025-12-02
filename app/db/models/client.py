from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Client(Base):
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False) # Главный ключ
    name = Column(String, nullable=True)
    
    # Telegram (BigInteger, т.к. ID могут быть длинными)
    telegram_chat_id = Column(BigInteger, unique=True, nullable=True, index=True)
    telegram_username = Column(String, nullable=True)
    
    # Мета
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    bonus_balance = Column(Integer, default=0)
    
    # Связь с заказами (один клиент -> много заказов)
    orders = relationship("Order", back_populates="client")