from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from database.models import Base, User, QRCode
from config import settings
from typing import Optional, List

# Database setup
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class UserRepository:
    @staticmethod
    async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, db: AsyncSession = None) -> User:
        if db is None:
            async with AsyncSessionLocal() as session:
                return await UserRepository.get_or_create_user(telegram_id, username, first_name, session)
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user
    
    @staticmethod
    async def increment_qr_count(telegram_id: int, db: AsyncSession = None):
        if db is None:
            async with AsyncSessionLocal() as session:
                return await UserRepository.increment_qr_count(telegram_id, session)
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.qr_count += 1
            await db.commit()
    
    @staticmethod
    async def get_user_stats(telegram_id: int, db: AsyncSession = None) -> Optional[dict]:
        if db is None:
            async with AsyncSessionLocal() as session:
                return await UserRepository.get_user_stats(telegram_id, session)
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return {
                "total_qr_codes": user.qr_count,  # Використовуємо user.qr_count
                "member_since": user.created_at.strftime("%d.%m.%Y")
            }
        return None

class QRRepository:
    @staticmethod
    async def save_qr_code(user_id: int, text_content: str, settings: dict, db: AsyncSession = None):
        if db is None:
            async with AsyncSessionLocal() as session:
                return await QRRepository.save_qr_code(user_id, text_content, settings, session)
        qr_code = QRCode(
            user_id=user_id,
            text_content=text_content,
            format=settings["fmt"],
            size=settings["size"],
            fg_color=settings["fg"],
            bg_color=settings["bg"]
        )
        db.add(qr_code)
        await db.commit()
        await db.refresh(qr_code)
        # Оновлюємо лічильник QR-кодів для користувача
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.qr_count += 1
            await db.commit()
        return qr_code
    
    @staticmethod
    async def get_user_history(user_id: int, limit: int = 10, db: AsyncSession = None) -> List[QRCode]:
        if db is None:
            async with AsyncSessionLocal() as session:
                return await QRRepository.get_user_history(user_id, limit, session)
        stmt = select(QRCode).where(QRCode.user_id == user_id).order_by(QRCode.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()