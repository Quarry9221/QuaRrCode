# У qr_generation.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base import BaseHandler
from states.user_states import UserState
from services.qr_service import QRService
from core.validators import TextValidator
from database.repository import AsyncSessionLocal
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
        
        if state == UserState.WAITING_TEXT or state == UserState.WAITING_PHONE:
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
                "bg": "white",
                "user_id": context.user_data.get("user_id", update.effective_user.id),
                "http_session": context.bot_data.get("http_session"),
                "db_session": context.bot_data.get("db_session")  # Додаємо db_session
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
                
            async with AsyncSessionLocal() as db_session:
                    settings["db_session"] = db_session
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