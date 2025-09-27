from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from config import settings

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    qr_count = Column(Integer, default=0)

class QRCode(Base):
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    format = Column(String(10), nullable=False)
    size = Column(Integer, nullable=False)
    fg_color = Column(String(20), nullable=False)
    bg_color = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)