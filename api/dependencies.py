from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from database.repository import AsyncSessionLocal
from config import settings

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

async def get_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key