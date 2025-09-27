from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.repository import QRRepository, UserRepository
from api.schemas import QRCode, QRCodeCreate
from api.dependencies import get_db, get_api_key
from config import settings
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/", response_model=QRCode)
async def create_qr_code(qr: QRCodeCreate, db: AsyncSession = Depends(get_db), api_key: str = Depends(get_api_key)):
    # Перевірка довжини тексту
    if len(qr.text_content) > settings.max_qr_text_length:
        raise HTTPException(status_code=400, detail="Text too long for QR code")

    # Перевірка формату, розміру та кольорів
    if qr.format.upper() not in settings.allowed_qr_formats:
        raise HTTPException(status_code=400, detail=f"Invalid format. Allowed: {settings.allowed_qr_formats}")
    if qr.size not in settings.allowed_qr_sizes:
        raise HTTPException(status_code=400, detail=f"Invalid size. Allowed: {settings.allowed_qr_sizes}")
    if qr.fg_color not in settings.allowed_colors or qr.bg_color not in settings.allowed_colors:
        raise HTTPException(status_code=400, detail=f"Invalid color. Allowed: {settings.allowed_colors}")

    # Перевірка існування користувача
    user = await UserRepository.get_or_create_user(telegram_id=qr.user_id, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Створення QR-коду
    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=qr.size,
        border=4,
    )
    qr_code.add_data(qr.text_content)
    qr_code.make(fit=True)
    qr_image = qr_code.make_image(fill_color=qr.fg_color, back_color=qr.bg_color)

    # Збереження в базі даних
    qr_settings = {
        "fmt": qr.format,
        "size": qr.size,
        "fg": qr.fg_color,
        "bg": qr.bg_color
    }
    db_qr = await QRRepository.save_qr_code(user_id=user.id, text_content=qr.text_content, settings=qr_settings, db=db)

    # Збереження зображення в буфер
    buffer = BytesIO()
    qr_image.save(buffer, format=qr.format.upper())
    buffer.seek(0)

    # Повернення зображення
    return StreamingResponse(
        buffer,
        media_type=f"image/{qr.format.lower()}",
        headers={"Content-Disposition": f"attachment; filename=qr_code_{db_qr.id}.{qr.format.lower()}"}
    )

@router.get("/{user_id}/history")
async def get_qr_history(user_id: int, db: AsyncSession = Depends(get_db), api_key: str = Depends(get_api_key)):
    qr_codes = await QRRepository.get_user_history(user_id=user_id, db=db)
    if not qr_codes:
        raise HTTPException(status_code=404, detail="No QR codes found")
    return qr_codes