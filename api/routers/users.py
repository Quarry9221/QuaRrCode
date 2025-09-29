from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.repository import UserRepository
from api.schemas import User, UserCreate, UserStats
from api.dependencies import get_db, get_api_key
from aiocache import cached, Cache
from config import settings

router = APIRouter()


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    db_user = await UserRepository.get_or_create_user(
        telegram_id=user.telegram_id, username=user.username, first_name=user.first_name
    )
    return db_user


@cached(ttl=300, cache=Cache.REDIS, endpoint=settings.redis_url)
@router.get("/{telegram_id}/stats", response_model=UserStats)
async def get_user_stats(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    stats = await UserRepository.get_user_stats(telegram_id)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return stats
