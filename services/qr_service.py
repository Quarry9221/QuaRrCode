import aiohttp
import qrcode
from qrcode.image.svg import SvgImage
from io import BytesIO
from dataclasses import dataclass
from typing import Literal, Optional
import logging
from core.validators import ContentTypeDetector
from config import settings as config_settings
from database.repository import QRRepository, UserRepository

logger = logging.getLogger(__name__)


@dataclass
class QRResult:
    file: BytesIO
    format: str
    caption: str
    content_type: str


class QRService:
    @staticmethod
    async def generate_qr_code(text: str, settings: dict) -> QRResult:
        try:

            fmt = settings.get("fmt", "PNG")
            size = settings.get("size", 10)
            fg_color = settings.get("fg", "black")
            bg_color = settings.get("bg", "white")
            http_session = settings.get("http_session")
            user_id = settings.get("user_id", 0)

            content_type = ContentTypeDetector.detect_content_type(text)

            if http_session:

                headers = {"X-API-Key": config_settings.api_key}
                data = {
                    "user_id": user_id,
                    "text_content": text,
                    "format": fmt,
                    "size": size,
                    "fg_color": fg_color,
                    "bg_color": bg_color,
                }
                logger.info(
                    f"Sending request to {config_settings.api_url}/qr_codes/ with data: {data}"
                )
                async with http_session.post(
                    f"{config_settings.api_url}/qr_codes/", json=data, headers=headers
                ) as response:
                    if response.status == 200:
                        qr_file = BytesIO(await response.read())
                        qr_file.name = f"qr.{fmt.lower()}"
                        return QRResult(
                            file=qr_file,
                            format=fmt.upper(),
                            caption=f"✅ QR код готовий!\n🔍 Тип: {content_type}",
                            content_type=content_type,
                        )
                    else:
                        logger.warning(
                            f"FastAPI request failed: {response.status}, falling back to local generation"
                        )

            logger.info("Falling back to local QR generation")
            qr_file = QRService._generate_qr_image(text, size, fg_color, bg_color, fmt)
            return QRResult(
                file=qr_file,
                format=fmt.upper(),
                caption=f"✅ QR код готовий!\n🔍 Тип: {content_type} (локальна генерація)",
                content_type=content_type,
            )

        except Exception as e:
            logger.exception(f"Error generating QR code: {e}")
            raise

    @staticmethod
    def _generate_qr_image(
        text: str,
        size: int = 10,
        fg_color: str = "black",
        bg_color: str = "white",
        fmt: Literal["PNG", "SVG"] = "PNG",
    ) -> BytesIO:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        fmt_upper = fmt.upper()
        if fmt_upper == "PNG":
            img = qr.make_image(fill_color=fg_color, back_color=bg_color)
            filename = "qr.png"
        elif fmt_upper == "SVG":
            img = qr.make_image(
                image_factory=SvgImage, fill_color=fg_color, back_color=bg_color
            )
            filename = "qr.svg"
        else:
            raise ValueError(f"Непідтримуваний формат: {fmt}")

        bio = BytesIO()
        bio.name = filename
        img.save(bio)
        bio.seek(0)

        return bio

    @staticmethod
    async def save_to_history(telegram_id: int, text: str, settings: dict):
        try:
            logger.info(f"Saving QR to history for user {telegram_id}: {text[:50]}...")
            http_session = settings.get("http_session")
            db_session = settings.get("db_session")
            if http_session:
                headers = {"X-API-Key": config_settings.api_key}
                data = {
                    "user_id": telegram_id,
                    "text_content": text,
                    "format": settings.get("fmt", "PNG"),
                    "size": settings.get("size", 10),
                    "fg_color": settings.get("fg", "black"),
                    "bg_color": settings.get("bg", "white"),
                }
                async with http_session.post(
                    f"{config_settings.api_url}/qr_codes/", json=data, headers=headers
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Failed to save QR to history via API: {response.status}"
                        )
                        if db_session:

                            await UserRepository.get_or_create_user(
                                telegram_id=telegram_id,
                                username=settings.get("username"),
                                first_name=settings.get("first_name"),
                                db=db_session,
                            )
                            await QRRepository.save_qr_code(
                                telegram_id, text, settings, db=db_session
                            )
                        else:
                            logger.error("No db_session provided for local QR save")
            else:
                if db_session:

                    await UserRepository.get_or_create_user(
                        telegram_id=telegram_id,
                        username=settings.get("username"),
                        first_name=settings.get("first_name"),
                        db=db_session,
                    )
                    await QRRepository.save_qr_code(
                        telegram_id, text, settings, db=db_session
                    )
                else:
                    logger.error("No db_session provided for local QR save")
        except Exception as e:
            logger.error(f"Error saving QR to history: {e}")
            raise
