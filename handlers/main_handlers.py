# ==== handlers/main_handlers.py ====
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

# Імпорти з інших модулів (припускаючи що вони в тій же папці проекту)
try:
    from keyboards.inline import InlineKeyboards
except ImportError:
    # Якщо структура папок інша, використовуємо відносні імпорти
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from keyboards.inline import InlineKeyboards

try:
    from handlers.base import BaseHandler
except ImportError:
    # Fallback версія BaseHandler
    class BaseHandler:
        @staticmethod
        async def ensure_user_exists(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Забезпечує існування користувача в БД"""
            user = update.effective_user
            if user:
                # Простий варіант без БД
                context.user_data["user_id"] = user.id
                context.user_data["username"] = user.username
                context.user_data["first_name"] = user.first_name
        
        @staticmethod
        def get_user_state(context: ContextTypes.DEFAULT_TYPE) -> str:
            """Отримує поточний стан користувача"""
            return context.user_data.get("state", "MAIN_MENU")
        
        @staticmethod
        def set_user_state(context: ContextTypes.DEFAULT_TYPE, state: str):
            """Встановлює стан користувача"""
            context.user_data["state"] = state

try:
    from states import BotState
except ImportError:
    # Fallback - використовуємо строки замість enum
    class BotState:
        MAIN_MENU = "main_menu"
        WAITING_TEXT = "waiting_text"
        WAITING_WIFI_SSID = "waiting_wifi_ssid"
        WAITING_WIFI_PASSWORD = "waiting_wifi_password"
        WAITING_CONTACT_NAME = "waiting_contact_name"
        WAITING_CONTACT_PHONE = "waiting_contact_phone"
        WAITING_URL = "waiting_url"
        WAITING_EMAIL = "waiting_email"

try:
    from database.repository import UserRepository, QRRepository
except ImportError:
    # Fallback репозиторії без БД
    class UserRepository:
        @staticmethod
        def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None):
            return {"id": telegram_id, "username": username, "first_name": first_name}
        
        @staticmethod
        def increment_qr_count(telegram_id: int):
            pass
        
        @staticmethod
        def get_user_stats(telegram_id: int):
            return {"total_qr_codes": 0, "member_since": "01.01.2024"}
    
    class QRRepository:
        @staticmethod
        def save_qr_code(user_id: int, text_content: str, settings: dict):
            pass
        
        @staticmethod
        def get_user_history(user_id: int, limit: int = 10):
            return []

try:
    from services.qr_service import QRService
except ImportError:
    # Fallback QR сервіс
    import qrcode
    from qrcode.image.svg import SvgImage
    from io import BytesIO
    import re
    
    try:
        import validators
    except ImportError:
        validators = None
    
    class QRService:
        @staticmethod
        def validate_text(text: str) -> tuple[bool, str]:
            """Валідація тексту для QR коду"""
            if not text or not text.strip():
                return False, "Текст не може бути порожнім"
            
            if len(text) > 2048:
                return False, "Текст занадто довгий (максимум 2048 символів)"
            
            return True, ""
        
        @staticmethod
        def detect_content_type(text: str) -> str:
            """Визначення типу контенту"""
            if validators and validators.url(text):
                return "🌐 URL"
            elif validators and validators.email(text):
                return "📧 Email"
            elif re.match(r'^\+?[\d\s\-\(\)]+$', text):
                return "📞 Телефон"
            elif text.upper().startswith("WIFI:"):
                return "📶 WiFi"
            elif text.startswith("BEGIN:VCARD"):
                return "👤 Контакт"
            else:
                return "📝 Текст"
        
        @staticmethod
        def generate_qr_image(text: str, size: int = 10, fg_color: str = "black", 
                             bg_color: str = "white", fmt: str = "PNG") -> BytesIO:
            """Генерація QR коду"""
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=size,
                border=4
            )
            qr.add_data(text)
            qr.make(fit=True)

            fmt_upper = fmt.upper()
            if fmt_upper == "PNG":
                img = qr.make_image(fill_color=fg_color, back_color=bg_color)
                filename = "qr.png"
            elif fmt_upper == "SVG":
                img = qr.make_image(image_factory=SvgImage, fill_color=fg_color, back_color=bg_color)
                filename = "qr.svg"
            else:
                raise ValueError(f"Непідтримуваний формат: {fmt}")

            bio = BytesIO()
            bio.name = filename
            img.save(bio)
            bio.seek(0)
            return bio

try:
    from services.text_processor import TextProcessor
except ImportError:
    # Fallback TextProcessor
    class TextProcessor:
        @staticmethod
        def create_wifi_qr_text(ssid: str, password: str, security: str = "WPA", hidden: bool = False) -> str:
            """Створює текст для WiFi QR коду"""
            return f"WIFI:T:{security};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"
        
        @staticmethod
        def create_contact_qr_text(name: str, phone: str = "", email: str = "", organization: str = "") -> str:
            """Створює vCard для контакту"""
            vcard = "BEGIN:VCARD\nVERSION:3.0\n"
            vcard += f"FN:{name}\n"
            if phone:
                vcard += f"TEL:{phone}\n"
            if email:
                vcard += f"EMAIL:{email}\n"
            if organization:
                vcard += f"ORG:{organization}\n"
            vcard += "END:VCARD"
            return vcard

logger = logging.getLogger(__name__)

# Дефолтні налаштування
DEFAULT_SETTINGS = {
    "fmt": "PNG",
    "size": 10,
    "fg": "black",
    "bg": "white"
}

class MainHandlers(BaseHandler):
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        await MainHandlers.ensure_user_exists(update, context)
        context.user_data["qr_settings"] = DEFAULT_SETTINGS.copy()
        MainHandlers.set_user_state(context, BotState.MAIN_MENU)
        
        # Створюємо inline клавіатуру прямо тут, якщо немає InlineKeyboards
        keyboard = [
            [InlineKeyboardButton("📱 Генерувати QR", callback_data="action:generate")],
            [InlineKeyboardButton("🔧 Налаштування", callback_data="action:settings"),
             InlineKeyboardButton("📊 Статистика", callback_data="action:stats")],
            [InlineKeyboardButton("📋 Шаблони", callback_data="action:templates"),
             InlineKeyboardButton("📜 Історія", callback_data="action:history")],
            [InlineKeyboardButton("ℹ️ Допомога", callback_data="action:help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 Вітаю в QR Bot!\n\n"
            "Я можу створити QR коди для:\n"
            "• 📝 Текст\n"
            "• 🌐 Посилання\n"
            "• 📶 WiFi\n"
            "• 👤 Контакти\n"
            "• 📧 Email\n\n"
            "Оберіть дію:",
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник callback запитів"""
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data.startswith("action:"):
            await MainHandlers._handle_action(query, context, data.split(":")[1])
        elif data.startswith("template:"):
            await MainHandlers._handle_template(query, context, data.split(":")[1])
        elif data.startswith("setting:"):
            await MainHandlers._handle_setting(query, context, data.split(":")[1])
        elif data.startswith("set:"):
            await MainHandlers._handle_set_value(query, context, data)
    
    @staticmethod
    async def _handle_action(query, context, action):
        """Обробка дій"""
        if action == "generate":
            MainHandlers.set_user_state(context, BotState.WAITING_TEXT)
            
            # Шаблони меню
            keyboard = [
                [InlineKeyboardButton("📶 WiFi", callback_data="template:wifi"),
                 InlineKeyboardButton("👤 Контакт", callback_data="template:contact")],
                [InlineKeyboardButton("📧 Email", callback_data="template:email"),
                 InlineKeyboardButton("📞 Телефон", callback_data="template:phone")],
                [InlineKeyboardButton("🌐 URL", callback_data="template:url")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="action:main")]
            ]
            
            await query.edit_message_text(
                "✏️ Надішліть текст або посилання для створення QR коду:\n\n"
                "Або оберіть шаблон:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif action == "settings":
            settings = context.user_data.get("qr_settings", DEFAULT_SETTINGS)
            
            keyboard = [
                [InlineKeyboardButton(f"📄 Формат: {settings['fmt']}", callback_data="setting:format"),
                 InlineKeyboardButton(f"📏 Розмір: {settings['size']}", callback_data="setting:size")],
                [InlineKeyboardButton(f"🎨 Колір: {settings['fg']}", callback_data="setting:fg_color"),
                 InlineKeyboardButton(f"🎨 Фон: {settings['bg']}", callback_data="setting:bg_color")],
                [InlineKeyboardButton("♻️ Скинути", callback_data="setting:reset"),
                 InlineKeyboardButton("✅ Готово", callback_data="action:main")]
            ]
            
            await query.edit_message_text(
                "🔧 Налаштування QR коду:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif action == "stats":
            await MainHandlers._show_stats(query, context)
        elif action == "history":
            await MainHandlers._show_history(query, context)
        elif action == "help":
            await MainHandlers._show_help(query, context)
        elif action == "main":
            keyboard = [
                [InlineKeyboardButton("📱 Генерувати QR", callback_data="action:generate")],
                [InlineKeyboardButton("🔧 Налаштування", callback_data="action:settings"),
                 InlineKeyboardButton("📊 Статистика", callback_data="action:stats")],
                [InlineKeyboardButton("📋 Шаблони", callback_data="action:templates"),
                 InlineKeyboardButton("📜 Історія", callback_data="action:history")],
                [InlineKeyboardButton("ℹ️ Допомога", callback_data="action:help")]
            ]
            
            await query.edit_message_text(
                "🤖 Головне меню:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif action == "templates":
            keyboard = [
                [InlineKeyboardButton("📶 WiFi", callback_data="template:wifi"),
                 InlineKeyboardButton("👤 Контакт", callback_data="template:contact")],
                [InlineKeyboardButton("📧 Email", callback_data="template:email"),
                 InlineKeyboardButton("📞 Телефон", callback_data="template:phone")],
                [InlineKeyboardButton("🌐 URL", callback_data="template:url")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="action:main")]
            ]
            
            await query.edit_message_text(
                "📋 Оберіть шаблон:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    @staticmethod
    async def _handle_template(query, context, template):
        """Обробка шаблонів"""
        if template == "wifi":
            MainHandlers.set_user_state(context, BotState.WAITING_WIFI_SSID)
            await query.edit_message_text(
                "📶 Створення WiFi QR коду\n\n"
                "Введіть назву мережі (SSID):"
            )
        elif template == "contact":
            MainHandlers.set_user_state(context, BotState.WAITING_CONTACT_NAME)
            await query.edit_message_text(
                "👤 Створення контакту\n\n"
                "Введіть ім'я:"
            )
        elif template == "email":
            MainHandlers.set_user_state(context, BotState.WAITING_EMAIL)
            await query.edit_message_text(
                "📧 Введіть email адресу:"
            )
        elif template == "url":
            MainHandlers.set_user_state(context, BotState.WAITING_URL)
            await query.edit_message_text(
                "🌐 Введіть URL (з http:// або https://):"
            )
        elif template == "phone":
            MainHandlers.set_user_state(context, BotState.WAITING_TEXT)
            await query.edit_message_text(
                "📞 Введіть номер телефону:"
            )
    
    @staticmethod
    async def _handle_setting(query, context, setting):
        """Обробка налаштувань"""
        if setting == "format":
            keyboard = [
                [InlineKeyboardButton("PNG", callback_data="set:fmt:PNG"),
                 InlineKeyboardButton("SVG", callback_data="set:fmt:SVG")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")]
            ]
            await query.edit_message_text(
                "📄 Оберіть формат:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif setting == "size":
            keyboard = [
                [InlineKeyboardButton("5", callback_data="set:size:5"),
                 InlineKeyboardButton("10", callback_data="set:size:10"),
                 InlineKeyboardButton("15", callback_data="set:size:15")],
                [InlineKeyboardButton("20", callback_data="set:size:20"),
                 InlineKeyboardButton("25", callback_data="set:size:25")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")]
            ]
            await query.edit_message_text(
                "📏 Оберіть розмір:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif setting == "fg_color":
            keyboard = [
                [InlineKeyboardButton("⚫ Чорний", callback_data="set:fg:black"),
                 InlineKeyboardButton("🔵 Синій", callback_data="set:fg:blue")],
                [InlineKeyboardButton("🔴 Червоний", callback_data="set:fg:red"),
                 InlineKeyboardButton("🟢 Зелений", callback_data="set:fg:green")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")]
            ]
            await query.edit_message_text(
                "🎨 Оберіть колір QR коду:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif setting == "bg_color":
            keyboard = [
                [InlineKeyboardButton("⚪ Білий", callback_data="set:bg:white"),
                 InlineKeyboardButton("🟡 Жовтий", callback_data="set:bg:yellow")],
                [InlineKeyboardButton("🔘 Сірий", callback_data="set:bg:gray"),
                 InlineKeyboardButton("🟣 Прозорий", callback_data="set:bg:transparent")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")]
            ]
            await query.edit_message_text(
                "🎨 Оберіть колір фону:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif setting == "reset":
            context.user_data["qr_settings"] = DEFAULT_SETTINGS.copy()
            keyboard = [
                [InlineKeyboardButton("✅ ОК", callback_data="action:settings")]
            ]
            await query.edit_message_text(
                "♻️ Налаштування скинуто до стандартних!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    @staticmethod
    async def _handle_set_value(query, context, data):
        """Обробка встановлення значень"""
        try:
            _, key, value = data.split(":")
            settings = context.user_data.get("qr_settings", DEFAULT_SETTINGS.copy())
            
            if key == "size":
                settings[key] = int(value)
            else:
                settings[key] = value
            
            context.user_data["qr_settings"] = settings
            
            keyboard = [
                [InlineKeyboardButton("⬅️ Назад до налаштувань", callback_data="action:settings")]
            ]
            await query.edit_message_text(
                f"✅ {key.upper()} встановлено: {value}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error setting value: {e}")
            await query.edit_message_text("❌ Помилка збереження налаштування")
    
    @staticmethod
    async def _show_stats(query, context):
        """Показ статистики користувача"""
        user = query.from_user
        stats = UserRepository.get_user_stats(user.id)
        
        text = (
            f"📊 Ваша статистика:\n\n"
            f"👤 Ім'я: {user.first_name or 'Невідоме'}\n"
            f"🔢 Створено QR кодів: {stats['total_qr_codes']}\n"
            f"📅 Учасник з: {stats['member_since']}"
        )
        
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="action:main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def _show_history(query, context):
        """Показ історії QR кодів"""
        user_id = context.user_data.get("user_id", query.from_user.id)
        history = QRRepository.get_user_history(user_id, limit=5)
        
        if history:
            text = "📜 Останні QR коди:\n\n"
            for i, qr in enumerate(history, 1):
                content_preview = qr.text_content[:30] + "..." if len(qr.text_content) > 30 else qr.text_content
                text += f"{i}. {content_preview}\n"
                text += f"   📅 {qr.created_at.strftime('%d.%m %H:%M')}\n\n"
        else:
            text = "📜 Історія порожня\n\nСтворіть свій перший QR код!"
        
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="action:main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def _show_help(query, context):
        """Показ допомоги"""
        text = (
            "ℹ️ Довідка по QR Bot:\n\n"
            "🔹 Генерувати QR - створення QR коду з тексту\n"
            "🔹 Шаблони - готові шаблони для WiFi, контактів тощо\n"
            "🔹 Налаштування - зміна розміру, кольорів, формату\n"
            "🔹 Статистика - ваша статистика використання\n"
            "🔹 Історія - останні створені QR коди\n\n"
            "📱 Підтримувані формати: PNG, SVG\n"
            "🎨 Різні кольори та розміри\n"
            "📊 Автовизначення типу контенту\n\n"
            "💡 Просто надішліть текст після натискання 'Генерувати QR'!"
        )
        
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="action:main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник текстових повідомлень"""
        await MainHandlers.ensure_user_exists(update, context)
        state = MainHandlers.get_user_state(context)
        text = update.message.text
        
        if state == BotState.WAITING_TEXT:
            await MainHandlers._process_qr_generation(update, context, text)
        elif state == BotState.WAITING_WIFI_SSID:
            context.user_data["wifi_ssid"] = text
            MainHandlers.set_user_state(context, BotState.WAITING_WIFI_PASSWORD)
            await update.message.reply_text("🔐 Тепер введіть пароль від WiFi:")
        elif state == BotState.WAITING_WIFI_PASSWORD:
            ssid = context.user_data.get("wifi_ssid")
            wifi_text = TextProcessor.create_wifi_qr_text(ssid, text)
            await MainHandlers._process_qr_generation(update, context, wifi_text)
        elif state == BotState.WAITING_CONTACT_NAME:
            context.user_data["contact_name"] = text
            MainHandlers.set_user_state(context, BotState.WAITING_CONTACT_PHONE)
            await update.message.reply_text("📞 Введіть номер телефону (або напишіть 'пропустити'):")
        elif state == BotState.WAITING_CONTACT_PHONE:
            name = context.user_data.get("contact_name")
            phone = text if text.lower() != "пропустити" else ""
            contact_text = TextProcessor.create_contact_qr_text(name, phone)
            await MainHandlers._process_qr_generation(update, context, contact_text)
        elif state == BotState.WAITING_EMAIL:
            if "@" in text:
                await MainHandlers._process_qr_generation(update, context, f"mailto:{text}")
            else:
                await update.message.reply_text("❌ Неправильний формат email. Спробуйте ще раз:")
        elif state == BotState.WAITING_URL:
            if text.startswith(("http://", "https://")):
                await MainHandlers._process_qr_generation(update, context, text)
            else:
                await update.message.reply_text("❌ URL повинен починатися з http:// або https://")
        else:
            # Користувач надіслав текст поза контекстом - показуємо головне меню
            keyboard = [
                [InlineKeyboardButton("📱 Генерувати QR", callback_data="action:generate")],
                [InlineKeyboardButton("🔧 Налаштування", callback_data="action:settings"),
                 InlineKeyboardButton("📊 Статистика", callback_data="action:stats")],
                [InlineKeyboardButton("ℹ️ Допомога", callback_data="action:help")]
            ]
            
            await update.message.reply_text(
                "🤖 Використовуйте меню для навігації:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    @staticmethod
    async def _process_qr_generation(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обробка генерації QR коду"""
        # Валідація тексту
        is_valid, error_msg = QRService.validate_text(text)
        if not is_valid:
            await update.message.reply_text(f"❌ {error_msg}")
            return
        
        # Генерація QR коду
        settings = context.user_data.get("qr_settings", DEFAULT_SETTINGS)
        content_type = QRService.detect_content_type(text)
        
        # Показуємо що працюємо
        processing_msg = await update.message.reply_text("🔄 Генерую QR код...")
        
        try:
            qr_image = QRService.generate_qr_image(
                text,
                size=settings.get("size", 10),
                fg_color=settings.get("fg", "black"),
                bg_color=settings.get("bg", "white"),
                fmt=settings.get("fmt", "PNG")
            )
            
            caption = f"✅ QR код готовий!\n🔍 Тип: {content_type}"
            
            # Видаляємо повідомлення про обробку
            await processing_msg.delete()
            
            if settings.get("fmt", "PNG").upper() == "PNG":
                await update.message.reply_photo(photo=qr_image, caption=caption)
            else:
                await update.message.reply_document(document=qr_image, caption=caption)
            
            # Збереження в історію (якщо є БД)
            try:
                user_id = context.user_data.get("user_id", update.effective_user.id)
                QRRepository.save_qr_code(user_id, text, settings)
                UserRepository.increment_qr_count(update.effective_user.id)
            except:
                pass  # Ігноруємо помилки БД
            
            # Повернення в головне меню
            MainHandlers.set_user_state(context, BotState.MAIN_MENU)
            
            keyboard = [
                [InlineKeyboardButton("🔄 Ще один QR код", callback_data="action:generate")],
                [InlineKeyboardButton("🏠 Головне меню", callback_data="action:main")]
            ]
            
            await update.message.reply_text(
                "🎉 Готово! Що будемо робити далі?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.exception("QR generation failed")
            await processing_msg.edit_text("❌ Помилка при створенні QR коду. Спробуйте ще раз.")
            
            # Показуємо головне меню після помилки
            keyboard = [
                [InlineKeyboardButton("🔄 Спробувати ще раз", callback_data="action:generate")],
                [InlineKeyboardButton("🏠 Головне меню", callback_data="action:main")]
            ]
            
            await update.message.reply_text(
                "Оберіть дію:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )