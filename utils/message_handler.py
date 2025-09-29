from telegram import Update
from telegram.ext import ContextTypes
from handlers.qr_generation import QRGenerationHandler
from handlers.templates import TemplatesHandler
from states.user_states import UserState
import logging

logger = logging.getLogger(__name__)


class MessageRouter:

    STATE_HANDLERS = {
        UserState.WAITING_TEXT: QRGenerationHandler.handle_text_input,
        UserState.WAITING_WIFI_SSID: TemplatesHandler.handle_wifi_ssid,
        UserState.WAITING_WIFI_PASSWORD: TemplatesHandler.handle_wifi_password,
        UserState.WAITING_CONTACT_NAME: TemplatesHandler.handle_contact_name,
        UserState.WAITING_CONTACT_PHONE: TemplatesHandler.handle_contact_phone,
        UserState.WAITING_EMAIL: TemplatesHandler.handle_email_template,
        UserState.WAITING_URL: TemplatesHandler.handle_url_template,
    }

    @staticmethod
    async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        state = QRGenerationHandler.get_user_state(context)
        logger.info(f"Routing message in state: {state}")

        handler = MessageRouter.STATE_HANDLERS.get(state)
        if handler:
            await handler(update, context)
        else:
            logger.info(f"No handler for state: {state}, showing main menu")
            await QRGenerationHandler._show_main_menu(update, context)
