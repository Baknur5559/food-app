from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
# Добавили orders в импорты
from app.api.v1.endpoints import tenants, users, login, menu, client, orders
from app.api.v1.endpoints import tenants, users, login, menu, client, orders, telegram 

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="FoodTech SaaS Platform API with Multi-tenancy and AI",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("app/static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем роутеры
app.include_router(login.router, prefix=f"{settings.API_V1_STR}/login", tags=["Auth"])
app.include_router(tenants.router, prefix=f"{settings.API_V1_STR}/tenants", tags=["Tenants"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(menu.router, prefix=f"{settings.API_V1_STR}/menu", tags=["Menu"])
app.include_router(client.router, prefix=f"{settings.API_V1_STR}/client", tags=["Client Showcase"])
# НОВЫЙ РОУТЕР ЗАКАЗОВ (Админка)
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["Orders"])
app.include_router(telegram.router, prefix=f"{settings.API_V1_STR}/telegram", tags=["Telegram Webhook"])

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "active",
        "system": "FoodTech AI SaaS",
        "version": "1.0.0"
    }