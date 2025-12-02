import asyncio
from sqlalchemy import text
from app.db.session import engine

async def test_connection():
    try:
        async with engine.connect() as conn:
            # Просто просим базу ответить "1"
            result = await conn.execute(text("SELECT 1"))
            print(f"✅ УСПЕХ! База ответила: {result.scalar()}")
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())