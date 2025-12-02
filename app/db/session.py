from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Создаем "движок" (Engine) - это сердце подключения
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,  # Если True, будет выводить все SQL запросы в консоль (удобно для отладки)
)

# Создаем фабрику сессий (SessionLocal)
# Каждый раз, когда нам нужно что-то сделать с БД, мы будем брать новую сессию отсюда
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)