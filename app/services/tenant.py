from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate

async def create_tenant(db: AsyncSession, tenant_in: TenantCreate):
    db_tenant = Tenant(**tenant_in.model_dump())
    db.add(db_tenant)
    await db.commit()
    await db.refresh(db_tenant)
    return db_tenant

async def get_tenants(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Tenant).offset(skip).limit(limit))
    return result.scalars().all()

# Новая функция обновления
async def update_tenant(db: AsyncSession, tenant_id: int, tenant_in: TenantUpdate):
    db_tenant = await db.get(Tenant, tenant_id)
    if not db_tenant:
        return None
    
    # Обновляем только те поля, которые пришли
    update_data = tenant_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tenant, key, value)
        
    await db.commit()
    await db.refresh(db_tenant)
    return db_tenant