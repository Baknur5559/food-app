from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    phone = Column(String, unique=True, index=True, nullable=False) # Логин по телефону
    hashed_password = Column(String, nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False) # Супер-админ (Владелец платформы)

    # Мультитеннантность: привязка к ресторану
    # Если tenant_id пустой, значит это Супер-админ системы
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=True)
    tenant = relationship("Tenant")