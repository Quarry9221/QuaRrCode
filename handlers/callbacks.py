from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest, NetworkError
from handlers.templates import TemplatesHandler
from handlers.settings import SettingsHandler
from handlers.base import BaseHandler
from config import settings
import aiohttp
import logging
from keyboards.inline import InlineKeyboards
from states.user_states import UserState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="bot.log",
    filemode="a",
)
logger = logging.getLogger(__name__)


class CallbackHandler:
    @staticmethod
    async def handle_callback_query(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        await query.answer()
        data: str = query.data

        logger.info(f"Callback received: {data}")

        try:
            if data.startswith("action:"):
                await CallbackHandler._handle_action(query, context, data.split(":")[1])
            elif data.startswith("template:"):
                await CallbackHandler._handle_template(
                    query, context, data.split(":")[1]
                )
            elif data.startswith("setting:"):
                await CallbackHandler._handle_setting(
                    query, context, data.split(":")[1]
                )
            elif data.startswith("set:"):
                await SettingsHandler.set_setting_value(
                    query, context, data.split(":")[1], data.split(":")[2]
                )
        except BadRequest as e:
            logger.error(f"Telegram API error: {e}")
            await query.edit_message_text("❌ Помилка Telegram API. Спробуйте ще раз.")
        except NetworkError as e:
            logger.error(f"Network error: {e}")
            await query.edit_message_text("🌐 Проблеми з мережею. Спробуйте пізніше.")
        except Exception as e:
            logger.exception(f"Unexpected error handling callback: {data}")
            await query.edit_message_text(
                "❌ Сталася неочікувана помилка. Спробуйте ще раз."
            )

    @staticmethod
    async def _handle_action(
        query, context: ContextTypes.DEFAULT_TYPE, action: str
    ) -> None:
        async def generate_handler(q, c):
            BaseHandler.set_user_state(c, UserState.WAITING_TEXT)
            await q.edit_message_text(
                "✏️ Надішліть текст або посилання для створення QR коду:\n\nАбо оберіть шаблон:",
                reply_markup=InlineKeyboards.templates_menu(),
            )

        actions = {
            "main": lambda q, c: q.edit_message_text(
                "🤖 Головне меню:", reply_markup=InlineKeyboards.main_menu()
            ),
            "generate": generate_handler,
            "settings": SettingsHandler.show_settings,
            "templates": lambda q, c: q.edit_message_text(
                "📋 Оберіть шаблон:", reply_markup=InlineKeyboards.templates_menu()
            ),
            "help": lambda q, c: q.edit_message_text(
                (
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
                ),
                reply_markup=InlineKeyboards.back_to_main(),
            ),
            "stats": CallbackHandler._show_stats,
            "history": CallbackHandler._show_history,
        }
        handler = actions.get(action)
        if handler:

            if (
                hasattr(handler, "__call__")
                and hasattr(handler, "__code__")
                and handler.__code__.co_flags & 0x80
            ):
                await handler(query, context)
            else:
                await handler(query, context)
        else:
            await query.edit_message_text("❌ Невідома дія.")

    @staticmethod
    async def _show_stats(query, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = query.from_user
        http_session: aiohttp.ClientSession = context.bot_data["http_session"]
        try:
            async with http_session.get(
                f"{settings.api_url}/users/{user.id}/stats",
                headers={"X-API-Key": settings.api_key},
            ) as response:
                if response.status == 200:
                    stats = await response.json()
                    text = (
                        f"📊 Ваша статистика:\n\n"
                        f"👤 Ім'я: {user.first_name or 'Невідоме'}\n"
                        f"🔢 Створено QR кодів: {stats['total_qr_codes']}\n"
                        f"📅 Учасник з: {stats['member_since']}"
                    )
                    await query.edit_message_text(
                        text, reply_markup=InlineKeyboards.back_to_main()
                    )
                else:
                    await query.edit_message_text("❌ Не вдалося отримати статистику.")
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            await query.edit_message_text(
                "🌐 Помилка зв’язку з сервером. Спробуйте пізніше."
            )

    @staticmethod
    async def _show_history(query, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = context.user_data.get("user_id", query.from_user.id)
        http_session: aiohttp.ClientSession = context.bot_data["http_session"]
        try:
            async with http_session.get(
                f"{settings.api_url}/qr_codes/{user_id}/history?limit=5",
                headers={"X-API-Key": settings.api_key},
            ) as response:
                if response.status == 200:
                    history = await response.json()
                    text = "📜 Останні QR коди:\n\n" + (
                        "\n".join(
                            [
                                f"{i+1}. {item['text_content'][:50]}..."
                                for i, item in enumerate(history)
                            ]
                        )
                        if history
                        else "ℹ️ Історія порожня."
                    )
                    await query.edit_message_text(
                        text, reply_markup=InlineKeyboards.back_to_main()
                    )
                else:
                    await query.edit_message_text("❌ Не вдалося отримати історію.")
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            await query.edit_message_text(
                "🌐 Помилка зв’язку з сервером. Спробуйте пізніше."
            )

    @staticmethod
    async def _handle_template(
        query, context: ContextTypes.DEFAULT_TYPE, template: str
    ) -> None:
        template_handlers = {
            "wifi": TemplatesHandler.handle_wifi_template,
            "contact": TemplatesHandler.handle_contact_template,
            "email": TemplatesHandler.handle_email_template_selection,
            "url": TemplatesHandler.handle_url_template_selection,
            "phone": TemplatesHandler.handle_phone_template_selection,
        }
        handler = template_handlers.get(template)
        if handler:
            await handler(query, context)
        else:
            await query.edit_message_text("❌ Невідомий шаблон.")

    @staticmethod
    async def _handle_setting(
        query, context: ContextTypes.DEFAULT_TYPE, setting: str
    ) -> None:
        setting_handlers = {
            "format": SettingsHandler.handle_format_setting,
            "size": SettingsHandler.handle_size_setting,
            "fg_color": SettingsHandler.handle_fg_color_setting,
            "bg_color": SettingsHandler.handle_bg_color_setting,
            "reset": SettingsHandler.reset_settings,
        }
        handler = setting_handlers.get(setting)
        if handler:
            await handler(query, context)
        else:
            await query.edit_message_text("❌ Невідоме налаштування.")
