import qrcode
from qrcode.image.svg import SvgImage
from io import BytesIO
from dataclasses import dataclass
from typing import Literal, Optional
import logging
from core.validators import ContentTypeDetector

logger = logging.getLogger(__name__)

@dataclass
class QRResult:
    """Результат генерації QR коду"""
    file: BytesIO
    format: str
    caption: str
    content_type: str

class QRService:
    """Сервіс для генерації та управління QR кодами"""
    
    @staticmethod
    async def generate_qr_code(text: str, settings: dict) -> QRResult:
        """
        Генерує QR код з налаштуваннями
        
        Args:
            text: Текст для QR коду
            settings: Словник з налаштуваннями (fmt, size, fg, bg)
            
        Returns:
            QRResult: Об'єкт з файлом та метаданими
        """
        try:
            # Отримуємо налаштування з дефолтними значеннями
            fmt = settings.get("fmt", "PNG")
            size = settings.get("size", 10)
            fg_color = settings.get("fg", "black")
            bg_color = settings.get("bg", "white")
            
            # Визначаємо тип контенту
            content_type = ContentTypeDetector.detect_content_type(text)
            
            # Генеруємо QR код
            qr_file = QRService._generate_qr_image(text, size, fg_color, bg_color, fmt)
            
            # Формуємо підпис
            caption = f"✅ QR код готовий!\n🔍 Тип: {content_type}"
            
            return QRResult(
                file=qr_file,
                format=fmt.upper(),
                caption=caption,
                content_type=content_type
            )
            
        except Exception as e:
            logger.exception(f"Error generating QR code: {e}")
            raise
    
    @staticmethod
    def _generate_qr_image(text: str, size: int = 10, fg_color: str = "black", 
                          bg_color: str = "white", fmt: Literal["PNG", "SVG"] = "PNG") -> BytesIO:
        """
        Внутрішній метод генерації QR зображення
        
        Args:
            text: Текст для QR коду
            size: Розмір блоку
            fg_color: Колір переднього плану
            bg_color: Колір фону
            fmt: Формат (PNG або SVG)
            
        Returns:
            BytesIO: Файл з QR кодом
        """
        # Створюємо QR код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=4
        )
        qr.add_data(text)
        qr.make(fit=True)

        # Генеруємо зображення
        fmt_upper = fmt.upper()
        if fmt_upper == "PNG":
            img = qr.make_image(fill_color=fg_color, back_color=bg_color)
            filename = "qr.png"
        elif fmt_upper == "SVG":
            img = qr.make_image(image_factory=SvgImage, fill_color=fg_color, back_color=bg_color)
            filename = "qr.svg"
        else:
            raise ValueError(f"Непідтримуваний формат: {fmt}")

        # Зберігаємо в BytesIO
        bio = BytesIO()
        bio.name = filename
        img.save(bio)
        bio.seek(0)
        
        return bio
    
    @staticmethod
    async def save_to_history(user_id: int, text: str, settings: dict):
        """
        Зберігає QR код в історію користувача
        
        Args:
            user_id: ID користувача
            text: Текст QR коду
            settings: Налаштування QR коду
        """
        try:
            # Тут буде логіка збереження в БД
            # Наразі просто логуємо
            logger.info(f"Saving QR to history for user {user_id}: {text[:50]}...")
            
            # Якщо є репозиторії - використовуємо їх
            try:
                from database.repository import QRRepository
                from database.repository import UserRepository
                
                QRRepository.save_qr_code(user_id, text, settings)
                UserRepository.increment_qr_count(user_id)
                
            except ImportError:
                # Репозиторії недоступні - пропускаємо збереження
                pass
                
        except Exception as e:
            logger.error(f"Error saving QR to history: {e}")
            # Не піднімаємо виняток, щоб не блокувати основний процес

# ==== handlers/qr_generation.py (виправлений) ====
"""Handler для генерації QR кодів"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base import BaseHandler
from states.user_states import UserState
from services.qr_service import QRService
from core.validators import TextValidator
import logging

logger = logging.getLogger(__name__)

class QRGenerationHandler(BaseHandler):
    @staticmethod
    async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка текстового вводу для генерації QR"""
        await QRGenerationHandler.ensure_user_exists(update, context)
        
        text = update.message.text
        state = QRGenerationHandler.get_user_state(context)
        
        logger.info(f"Processing text input in state: {state}")
        
        if state == UserState.WAITING_TEXT:
            await QRGenerationHandler._process_qr_generation(update, context, text)
        else:
            await QRGenerationHandler._show_main_menu(update, context)
    
    @staticmethod
    async def _process_qr_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Процес генерації QR коду"""
        logger.info(f"Starting QR generation for text: {text[:50]}...")
        
        # Валідація
        is_valid, error_msg = TextValidator.validate_qr_text(text)
        if not is_valid:
            logger.warning(f"Text validation failed: {error_msg}")
            await update.message.reply_text(f"❌ {error_msg}")
            return
        
        # Показуємо процес
        processing_msg = await update.message.reply_text("🔄 Генерую QR код...")
        
        try:
            # Генерація
            settings = context.user_data.get("qr_settings", {
                "fmt": "PNG",
                "size": 10, 
                "fg": "black",
                "bg": "white"
            })
            
            logger.info(f"Generating QR with settings: {settings}")
            qr_result = await QRService.generate_qr_code(text, settings)
            
            # Видаляємо повідомлення про обробку
            await processing_msg.delete()
            
            # Відправляємо результат
            if qr_result.format == "PNG":
                await update.message.reply_photo(
                    photo=qr_result.file, 
                    caption=qr_result.caption
                )
            else:
                await update.message.reply_document(
                    document=qr_result.file, 
                    caption=qr_result.caption
                )
            
            # Збереження в історію
            user_id = context.user_data.get("user_id", update.effective_user.id)
            await QRService.save_to_history(user_id, text, settings)
            
            # Повернення в головне меню
            QRGenerationHandler.set_user_state(context, UserState.MAIN_MENU)
            
            # Показуємо опції
            keyboard = [
                [InlineKeyboardButton("🔄 Ще один QR", callback_data="action:generate")],
                [InlineKeyboardButton("🏠 Головне меню", callback_data="action:main")]
            ]
            
            await update.message.reply_text(
                "🎉 Готово! Що далі?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            logger.info("QR generation completed successfully")
            
        except Exception as e:
            logger.exception("QR generation failed")
            
            try:
                await processing_msg.edit_text("❌ Помилка генерації. Спробуйте ще раз.")
            except:
                await update.message.reply_text("❌ Помилка генерації. Спробуйте ще раз.")
            
            # Показуємо опції після помилки
            keyboard = [
                [InlineKeyboardButton("🔄 Спробувати ще раз", callback_data="action:generate")],
                [InlineKeyboardButton("🏠 Головне меню", callback_data="action:main")]
            ]
            
            await update.message.reply_text(
                "Оберіть дію:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    @staticmethod
    async def _show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ головного меню"""
        try:
            from keyboards.inline import InlineKeyboards
            keyboard = InlineKeyboards.main_menu()
        except ImportError:
            # Fallback клавіатура
            keyboard_buttons = [
                [InlineKeyboardButton("📱 Генерувати QR", callback_data="action:generate")],
                [InlineKeyboardButton("🔧 Налаштування", callback_data="action:settings")],
                [InlineKeyboardButton("ℹ️ Допомога", callback_data="action:help")]
            ]
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
        
        await update.message.reply_text(
            "🤖 Використовуйте меню:",
            reply_markup=keyboard
        )