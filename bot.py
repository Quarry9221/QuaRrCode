# У bot.py
import aiohttp
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.start import StartHandler
from handlers.callbacks import CallbackHandler
from utils.message_handler import MessageRouter
from config import settings
import logging
import nest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.repository import init_db

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Застосовуємо nest_asyncio для Windows
nest_asyncio.apply()

async def main():
    # Ініціалізація бази даних
    engine = create_async_engine(settings.database_url, echo=settings.log_level == "DEBUG")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Створюємо таблиці в базі даних
    await init_db()
    
    async with aiohttp.ClientSession() as http_session, async_session() as db_session:
        logger.debug("Initializing application with db_session")
        application = Application.builder().token(settings.bot_token).build()
        application.bot_data["http_session"] = http_session
        application.bot_data["db_session"] = db_session
        
        # Перевірка, що db_session додано
        logger.debug(f"db_session in bot_data: {application.bot_data.get('db_session') is not None}")
        
        # Реєстрація хендлерів
        application.add_handler(CommandHandler("start", StartHandler.start_command))
        application.add_handler(CallbackQueryHandler(CallbackHandler.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, MessageRouter.route_message))
        
        logger.info("Starting bot...")
        await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())