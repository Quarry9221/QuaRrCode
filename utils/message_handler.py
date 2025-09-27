from telegram import Update
from telegram.ext import ContextTypes
from handlers.base import BaseHandler
from handlers.qr_generation import QRGenerationHandler
from handlers.templates import TemplatesHandler
from states.user_states import UserState
import logging

logger = logging.getLogger(__name__)

class MessageRouter(BaseHandler):
    """Маршрутизатор повідомлень за станами"""
    
    @staticmethod
    async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Маршрутизує повідомлення відповідно до стану користувача"""
        state = MessageRouter.get_user_state(context)
        
        logger.info(f"Routing message in state: {state}")
        
        # Маршрутизація по станах
        if state == UserState.WAITING_TEXT:
            await QRGenerationHandler.handle_text_input(update, context)
        elif state == UserState.WAITING_WIFI_SSID:
            await TemplatesHandler.handle_wifi_ssid(update, context)
        elif state == UserState.WAITING_WIFI_PASSWORD:
            await TemplatesHandler.handle_wifi_password(update, context)
        elif state == UserState.WAITING_CONTACT_NAME:
            await TemplatesHandler.handle_contact_name(update, context)
        elif state == UserState.WAITING_CONTACT_PHONE:
            await TemplatesHandler.handle_contact_phone(update, context)
        elif state == UserState.WAITING_EMAIL:
            await TemplatesHandler.handle_email_template(update, context)
        elif state == UserState.WAITING_URL:
            await TemplatesHandler.handle_url_template(update, context)
        else:
            # Дефолтний стан - показати головне меню
            await QRGenerationHandler._show_main_menu(update, context)