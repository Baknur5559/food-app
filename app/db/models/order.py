from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Order(Base):
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)
    
    # Связь с клиентом (НОВОЕ)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    client = relationship("Client", back_populates="orders")

    # Данные для доставки (копируются из клиента или вводятся вручную)
    client_name = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    delivery_address = Column(String, nullable=True)
    order_type = Column(String, default="delivery")
    payment_method = Column(String, default="cash")
    
    # Оплата (НОВОЕ)
    is_paid = Column(Boolean, default=False)
    payment_proof = Column(String, nullable=True) # Ссылка на скриншот
    
    # Источник заказа (web, bot, ai)
    source = Column(String, default="web") 

    # Деньги
    total_amount = Column(Float, default=0.0)
    delivery_price = Column(Float, default=0.0)
    
    # Статус
    status = Column(String, default="new")
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Товары
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menuitem.id"), nullable=False)
    
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")