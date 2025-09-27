from sqlalchemy.orm import Session
from database.models import User, QRCode, SessionLocal
from typing import Optional, List

class UserRepository:
    @staticmethod
    def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None) -> User:
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            return user
    
    @staticmethod
    def increment_qr_count(telegram_id: int):
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.qr_count += 1
                db.commit()
    
    @staticmethod
    def get_user_stats(telegram_id: int) -> Optional[dict]:
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                qr_count = db.query(QRCode).filter(QRCode.user_id == user.id).count()
                return {
                    "total_qr_codes": qr_count,
                    "member_since": user.created_at.strftime("%d.%m.%Y")
                }
            return None

class QRRepository:
    @staticmethod
    def save_qr_code(user_id: int, text_content: str, settings: dict):
        with SessionLocal() as db:
            qr_code = QRCode(
                user_id=user_id,
                text_content=text_content,
                format=settings["fmt"],
                size=settings["size"],
                fg_color=settings["fg"],
                bg_color=settings["bg"]
            )
            db.add(qr_code)
            db.commit()
    
    @staticmethod
    def get_user_history(user_id: int, limit: int = 10) -> List[QRCode]:
        with SessionLocal() as db:
            return db.query(QRCode).filter(
                QRCode.user_id == user_id
            ).order_by(QRCode.created_at.desc()).limit(limit).all()