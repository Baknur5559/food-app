from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sort_order = Column(Integer, default=0) # Для сортировки (Drag & Drop)
    
    # Привязка к ресторану
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)
    tenant = relationship("Tenant")
    
    # Связь с товарами (одна категория -> много товаров)
    items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True) # Если False - блюдо в стоп-листе
    
    # Привязки
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("Category", back_populates="items")
    
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)