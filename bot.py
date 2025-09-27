import aiohttp
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.start import StartHandler
from handlers.callbacks import CallbackHandler
from utils.message_handler import MessageRouter
from config import settings
import logging
import nest_asyncio

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Застосовуємо nest_asyncio для Windows
nest_asyncio.apply()

async def main():
    async with aiohttp.ClientSession() as session:
        application = Application.builder().token(settings.bot_token).build()
        application.bot_data["http_session"] = session
        
        # Реєстрація хендлерів
        application.add_handler(CommandHandler("start", StartHandler.start_command))
        application.add_handler(CallbackQueryHandler(CallbackHandler.handle_callback_query))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, MessageRouter.route_message))
        
        logger.info("Starting bot...")
        await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())