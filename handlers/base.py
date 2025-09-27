# У base.py
from telegram import Update
from telegram.ext import ContextTypes
from states.user_states import UserState
import logging
from database.repository import UserRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="bot.log",
    filemode="a"
)
logger = logging.getLogger(__name__)

class BaseHandler:
    @staticmethod
    async def ensure_user_exists(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Забезпечує існування користувача в user_data та базі даних"""
        user = update.effective_user
        if user:
            context.user_data["user_id"] = user.id
            context.user_data["username"] = user.username
            context.user_data["first_name"] = user.first_name
            
            try:
                db_session = context.bot_data.get("db_session")
                if not db_session:
                    logger.error("Database session not found in context.bot_data")
                    return
                
                logger.debug(f"Attempting to create or fetch user {user.id} with username {user.username}")
                user_obj = await UserRepository.get_or_create_user(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    db=db_session
                )
                logger.info(f"User {user.id} ensured in database with qr_count={user_obj.qr_count}")
            except Exception as e:
                logger.error(f"Failed to ensure user {user.id} in database: {e}")
    
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