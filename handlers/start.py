from telegram import Update
from telegram.ext import ContextTypes
from handlers.base import BaseHandler
from keyboards.inline import InlineKeyboards
from states.user_states import UserState
from constants import DEFAULT_QR_SETTINGS, WELCOME_MESSAGE
from database.repository import AsyncSessionLocal


class StartHandler(BaseHandler):
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        async with AsyncSessionLocal() as db_session:
            context.bot_data["db_session"] = db_session
            await StartHandler.ensure_user_exists(update, context)
        context.user_data["qr_settings"] = DEFAULT_QR_SETTINGS.copy()
        StartHandler.set_user_state(context, UserState.MAIN_MENU)

        await update.message.reply_text(
            WELCOME_MESSAGE, reply_markup=InlineKeyboards.main_menu()
        )
