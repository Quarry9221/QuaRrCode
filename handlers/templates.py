from telegram import Update
from telegram.ext import ContextTypes
from handlers.base import BaseHandler
from handlers.qr_generation import QRGenerationHandler
from states.user_states import UserState
from core.text_processor import TextProcessor
from core.validators import TextValidator
import logging

logger = logging.getLogger(__name__)

class TemplatesHandler(BaseHandler):
    @staticmethod
    async def handle_wifi_template(query, context):
        """WiFi шаблон"""
        TemplatesHandler.set_user_state(context, UserState.WAITING_WIFI_SSID)
        await query.edit_message_text(
            "📶 Створення WiFi QR коду\n\nВведіть назву мережі (SSID):"
        )
    
    @staticmethod
    async def handle_wifi_ssid(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка SSID для WiFi"""
        ssid = update.message.text.strip()
        
        # Валідація SSID
        is_valid, error_msg = TextValidator.validate_wifi_ssid(ssid)
        if not is_valid:
            await update.message.reply_text(f"❌ {error_msg}\nСпробуйте ще раз:")
            return
        
        context.user_data["wifi_ssid"] = ssid
        TemplatesHandler.set_user_state(context, UserState.WAITING_WIFI_PASSWORD)
        await update.message.reply_text(
            "🔐 Введіть пароль від WiFi:\n"
            "(або напишіть 'пропустити' для відкритої мережі)"
        )
    
    @staticmethod
    async def handle_wifi_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка паролю для WiFi"""
        password = update.message.text.strip()
        
        # Перевіряємо чи користувач хоче пропустити пароль
        if password.lower() in ['пропустити', 'skip', 'без пароля']:
            password = ""
            security = "nopass"
        else:
            # Валідація паролю
            is_valid, error_msg = TextValidator.validate_wifi_password(password)
            if not is_valid:
                await update.message.reply_text(f"❌ {error_msg}\nСпробуйте ще раз:")
                return
            security = "WPA"
        
        ssid = context.user_data.get("wifi_ssid")
        wifi_text = TextProcessor.create_wifi_qr_text(ssid, password, security)
        
        logger.info(f"Generated WiFi QR text: {wifi_text}")
        
        # Передаємо на генерацію
        await QRGenerationHandler._process_qr_generation(update, context, wifi_text)
    
    @staticmethod
    async def handle_contact_template(query, context):
        """Контакт шаблон"""
        TemplatesHandler.set_user_state(context, UserState.WAITING_CONTACT_NAME)
        await query.edit_message_text(
            "👤 Створення контакту\n\nВведіть ім'я:"
        )
    
    @staticmethod
    async def handle_contact_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка імені для контакту"""
        name = update.message.text.strip()
        
        if not name:
            await update.message.reply_text("❌ Ім'я не може бути порожнім. Спробуйте ще раз:")
            return
        
        context.user_data["contact_name"] = name
        TemplatesHandler.set_user_state(context, UserState.WAITING_CONTACT_PHONE)
        await update.message.reply_text(
            "📞 Введіть номер телефону:\n"
            "(або напишіть 'пропустити')"
        )
    
    @staticmethod
    async def handle_contact_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка телефону для контакту"""
        phone = update.message.text.strip()
        name = context.user_data.get("contact_name")
        
        # Перевіряємо чи користувач хоче пропустити телефон
        if phone.lower() in ['пропустити', 'skip']:
            phone = ""
        else:
            # Валідація телефону
            is_valid, error_msg = TextValidator.validate_phone(phone)
            if not is_valid:
                await update.message.reply_text(f"❌ {error_msg}\nСпробуйте ще раз або напишіть 'пропустити':")
                return
        
        # Створюємо vCard
        contact_text = TextProcessor.create_contact_qr_text(name, phone)
        
        logger.info(f"Generated contact QR text: {contact_text[:100]}...")
        
        # Передаємо на генерацію
        await QRGenerationHandler._process_qr_generation(update, context, contact_text)
    
    @staticmethod
    async def handle_email_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка email шаблону"""
        email = update.message.text.strip()
        
        # Валідація email
        is_valid, error_msg = TextValidator.validate_email(email)
        if not is_valid:
            await update.message.reply_text(f"❌ {error_msg}\nСпробуйте ще раз:")
            return
        
        # Створюємо mailto посилання
        email_text = f"mailto:{email}"
        
        # Передаємо на генерацію
        await QRGenerationHandler._process_qr_generation(update, context, email_text)
    
    @staticmethod
    async def handle_url_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка URL шаблону"""
        url = update.message.text.strip()
        
        # Додаємо https:// якщо немає протоколу
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = f"https://{url}"
        
        # Валідація URL
        is_valid, error_msg = TextValidator.validate_url(url)
        if not is_valid:
            await update.message.reply_text(f"❌ {error_msg}\nСпробуйте ще раз:")
            return
        
        # Передаємо на генерацію
        await QRGenerationHandler._process_qr_generation(update, context, url)



    @staticmethod
    async def handle_email_template_selection(query, context):
        TemplatesHandler.set_user_state(context, UserState.WAITING_EMAIL)
        await query.edit_message_text("📧 Введіть email адресу:")

    @staticmethod
    async def handle_url_template_selection(query, context):
        TemplatesHandler.set_user_state(context, UserState.WAITING_URL)
        await query.edit_message_text("🌐 Введіть URL:")

    @staticmethod
    async def handle_phone_template_selection(query, context):
        TemplatesHandler.set_user_state(context, UserState.WAITING_TEXT)
        await query.edit_message_text("📞 Введіть номер телефону:")