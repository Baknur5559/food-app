from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.schemas import tenant as schemas
from app.services import tenant as service

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.Tenant)
async def create_tenant(
    tenant_in: schemas.TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    return await service.create_tenant(db=db, tenant_in=tenant_in)

@router.get("/", response_model=List[schemas.Tenant])
async def read_tenants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_tenants(db=db, skip=skip, limit=limit)

# Новый эндпоинт для редактирования
@router.put("/{tenant_id}", response_model=schemas.Tenant)
async def update_tenant(
    tenant_id: int,
    tenant_in: schemas.TenantUpdate,
    db: AsyncSession = Depends(get_db)
):
    tenant = await service.update_tenant(db, tenant_id, tenant_in)
    if not tenant:
        raise HTTPException(status_code=404, detail="Ресторан не найден")
    return tenant