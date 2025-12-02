from typing import List, Optional
from pydantic import BaseModel
from app.schemas.menu import MenuItem, Category

class CategoryWithItems(Category):
    items: List[MenuItem] = []

class RestaurantPublic(BaseModel):
    id: int
    name: str
    slug: str
    custom_domain: Optional[str] = None
    # telegram_bot_token УБРАЛИ (Секретно)
    bot_username: Optional[str] = None # ДОБАВИЛИ (Публично)
    categories: List[CategoryWithItems]