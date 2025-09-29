from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    qr_count: int

    class Config:
        from_attributes = True


class QRCodeBase(BaseModel):
    text_content: str
    format: str
    size: int
    fg_color: str
    bg_color: str


class QRCodeCreate(QRCodeBase):
    user_id: int


class QRCode(QRCodeBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_qr_codes: int
    member_since: str
