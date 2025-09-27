from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.templates import TemplatesHandler
from handlers.settings import SettingsHandler
from states.user_states import UserState
import logging


logger = logging.getLogger(__name__)

class CallbackHandler:
    @staticmethod
    async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Центральний обробник всіх callback queries"""
        query = update.callback_query
        await query.answer()
        data = query.data
        
        logger.info(f"Callback received: {data}")
        
        try:
            if data.startswith("action:"):
                await CallbackHandler._handle_action(query, context, data.split(":")[1])
            elif data.startswith("template:"):
                await CallbackHandler._handle_template(query, context, data.split(":")[1])
            elif data.startswith("setting:"):
                await CallbackHandler._handle_setting(query, context, data.split(":")[1])
            elif data.startswith("set:"):
                await CallbackHandler._handle_set_value(query, context, data)
        except Exception as e:
            logger.exception(f"Error handling callback: {data}")
            await query.edit_message_text("❌ Сталася помилка. Спробуйте ще раз.")

    @staticmethod
    async def _handle_action(query, context, action):
        """Обробка дій callback action"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        from states.user_states import UserState
        # Головне меню
        if action == "main":
            CallbackHandler._set_user_state(context, UserState.MAIN_MENU)
            keyboard = [
                [InlineKeyboardButton("📱 Генерувати QR", callback_data="action:generate")],
                [InlineKeyboardButton("🔧 Налаштування", callback_data="action:settings")],
                [InlineKeyboardButton("📋 Шаблони", callback_data="action:templates")],
                [InlineKeyboardButton("ℹ️ Допомога", callback_data="action:help")]
            ]
            await query.edit_message_text("🤖 Головне меню:", reply_markup=InlineKeyboardMarkup(keyboard))
        elif action == "generate":
            CallbackHandler._set_user_state(context, UserState.WAITING_TEXT)
            keyboard = [
                [InlineKeyboardButton("📶 WiFi", callback_data="template:wifi"), InlineKeyboardButton("👤 Контакт", callback_data="template:contact")],
                [InlineKeyboardButton("📧 Email", callback_data="template:email"), InlineKeyboardButton("📞 Телефон", callback_data="template:phone")],
                [InlineKeyboardButton("🌐 URL", callback_data="template:url")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="action:main")]
            ]
            await query.edit_message_text(
                "✏️ Надішліть текст або посилання для створення QR коду:\n\nАбо оберіть шаблон:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif action == "settings":
            # Always use the latest settings from context.user_data
            settings = context.user_data.get("qr_settings")
            if settings is None:
                from constants import DEFAULT_QR_SETTINGS
                settings = DEFAULT_QR_SETTINGS.copy()
            from keyboards.inline import InlineKeyboards
            await query.edit_message_text(
                "🔧 Налаштування QR коду:",
                reply_markup=InlineKeyboards.settings_menu(settings)
            )
        elif action == "templates":
            keyboard = [
                [InlineKeyboardButton("📶 WiFi", callback_data="template:wifi"), InlineKeyboardButton("👤 Контакт", callback_data="template:contact")],
                [InlineKeyboardButton("📧 Email", callback_data="template:email"), InlineKeyboardButton("📞 Телефон", callback_data="template:phone")],
                [InlineKeyboardButton("🌐 URL", callback_data="template:url")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="action:main")]
            ]
            await query.edit_message_text("📋 Оберіть шаблон:", reply_markup=InlineKeyboardMarkup(keyboard))
        elif action == "help":
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
    async def _handle_template(query, context, template: str):
        """Обробка template callbacks через TemplatesHandler"""
        if template == "wifi":
            await TemplatesHandler.handle_wifi_template(query, context)
        elif template == "contact":
            await TemplatesHandler.handle_contact_template(query, context)
        elif template == "email":
            CallbackHandler._set_user_state(context, UserState.WAITING_EMAIL)
            await query.edit_message_text("📧 Введіть email адресу:")
        elif template == "url":
            CallbackHandler._set_user_state(context, UserState.WAITING_URL)
            await query.edit_message_text("🌐 Введіть URL:")
        elif template == "phone":
            CallbackHandler._set_user_state(context, UserState.WAITING_TEXT)
            await query.edit_message_text("📞 Введіть номер телефону:")

    @staticmethod
    async def _handle_setting(query, context, setting):
        """Делегуємо обробку налаштувань у SettingsHandler"""
        if setting == "format":
            await SettingsHandler.handle_format_setting(query, context)
        elif setting == "size":
            await SettingsHandler.handle_size_setting(query, context)
        elif setting == "fg_color":
            await SettingsHandler.handle_fg_color_setting(query, context)
        elif setting == "bg_color":
            await SettingsHandler.handle_bg_color_setting(query, context)
        elif setting == "reset":
            context.user_data["qr_settings"] = {"fmt": "PNG", "size": 10, "fg": "black", "bg": "white"}
            await CallbackHandler._handle_action(query, context, "main")

    @staticmethod
    async def _handle_set_value(query, context, data):
        """Делегуємо встановлення значення у SettingsHandler"""
        parts = data.split(":")
        if len(parts) == 3:
            key, value = parts[1], parts[2]
            await SettingsHandler.set_setting_value(query, context, key, value)
        else:
            await query.edit_message_text("❌ Некоректний формат даних для налаштування.", reply_markup=None)
    
    @staticmethod
    def _set_user_state(context: ContextTypes.DEFAULT_TYPE, state: UserState):
        """Допоміжний метод для встановлення стану"""
        context.user_data["state"] = state.value

    @staticmethod
    async def _show_stats(query, context):
        """Показ статистики користувача"""
        from database.repository import UserRepository
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
        from database.repository import QRRepository
        user_id = context.user_data.get("user_id", query.from_user.id)
        history = QRRepository.get_user_history(user_id, limit=5)
        if history:
            text = "📜 Останні QR коди:\n\n" + "\n".join([f"{i+1}. {item['text'][:50]}..." for i, item in enumerate(history)])
        else:
            text = "ℹ️ Історія порожня."
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

    