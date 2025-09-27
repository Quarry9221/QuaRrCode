"""Базовий клас для всіх handlers"""
from telegram import Update
from telegram.ext import ContextTypes
from states.user_states import UserState
import logging

logger = logging.getLogger(__name__)

class BaseHandler:
    @staticmethod
    async def ensure_user_exists(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Забезпечує існування користувача"""
        user = update.effective_user
        if user:
            context.user_data["user_id"] = user.id
            context.user_data["username"] = user.username
            context.user_data["first_name"] = user.first_name
    
    @staticmethod
    def get_user_state(context: ContextTypes.DEFAULT_TYPE) -> UserState:
        """Отримує поточний стан користувача"""
        state_str = context.user_data.get("state", UserState.MAIN_MENU.value)
        try:
            return UserState(state_str)
        except ValueError:
            return UserState.MAIN_MENU
    
    @staticmethod
    def set_user_state(context: ContextTypes.DEFAULT_TYPE, state: UserState):
        """Встановлює стан користувача"""
        context.user_data["state"] = state.value
        logger.info(f"User state changed to: {state.value}")