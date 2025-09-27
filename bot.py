# ==== bot.py (оновлений) ====
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers.start import StartHandler
from handlers.callbacks import CallbackHandler
from utils.message_handler import MessageRouter  # Новий роутер
from config import settings

def main():
    application = Application.builder().token(settings.bot_token).build()

    # Handlers
    application.add_handler(CommandHandler("start", StartHandler.start_command))
    application.add_handler(CallbackQueryHandler(CallbackHandler.handle_callback_query))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        MessageRouter.route_message  # Використовуємо роутер
    ))

    application.run_polling()

if __name__ == "__main__":
    main()