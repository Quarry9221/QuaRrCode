def get_qr_settings(context):
    settings = context.user_data.get("qr_settings", {}).copy()
    from constants import DEFAULT_QR_SETTINGS

    for k, v in DEFAULT_QR_SETTINGS.items():
        if k not in settings:
            settings[k] = v
    return settings


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base import BaseHandler
from keyboards.inline import InlineKeyboards
from constants import DEFAULT_QR_SETTINGS


class SettingsHandler(BaseHandler):
    @staticmethod
    async def handle_fg_color_setting(query, context):
        keyboard = [
            [
                InlineKeyboardButton("⚫ Чорний", callback_data="set:fg:black"),
                InlineKeyboardButton("🔵 Синій", callback_data="set:fg:blue"),
            ],
            [
                InlineKeyboardButton("🔴 Червоний", callback_data="set:fg:red"),
                InlineKeyboardButton("🟢 Зелений", callback_data="set:fg:green"),
            ],
            [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")],
        ]
        await query.edit_message_text(
            "🎨 Оберіть колір QR коду:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @staticmethod
    async def handle_bg_color_setting(query, context):
        keyboard = [
            [
                InlineKeyboardButton("⚪ Білий", callback_data="set:bg:white"),
                InlineKeyboardButton("🟡 Жовтий", callback_data="set:bg:yellow"),
            ],
            [
                InlineKeyboardButton("🟢 Зелений", callback_data="set:bg:green"),
                InlineKeyboardButton("🔵 Синій", callback_data="set:bg:blue"),
            ],
            [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")],
        ]
        await query.edit_message_text(
            "🎨 Оберіть колір фону QR коду:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    @staticmethod
    async def show_settings(query, context):
        settings = get_qr_settings(context)
        try:
            await query.edit_message_text(
                "🔧 Налаштування QR коду:",
                reply_markup=InlineKeyboards.settings_menu(settings),
            )
        except Exception as e:
            if hasattr(e, "message") and "Message is not modified" in str(e):

                pass
            elif "Message is not modified" in str(e):
                pass
            else:
                raise

    @staticmethod
    async def handle_format_setting(query, context):
        keyboard = [
            [
                InlineKeyboardButton("PNG", callback_data="set:fmt:PNG"),
                InlineKeyboardButton("SVG", callback_data="set:fmt:SVG"),
            ],
            [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")],
        ]
        await query.edit_message_text(
            "📄 Оберіть формат:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @staticmethod
    async def handle_size_setting(query, context):
        keyboard = [
            [
                InlineKeyboardButton("5", callback_data="set:size:5"),
                InlineKeyboardButton("10", callback_data="set:size:10"),
                InlineKeyboardButton("15", callback_data="set:size:15"),
            ],
            [
                InlineKeyboardButton("20", callback_data="set:size:20"),
                InlineKeyboardButton("25", callback_data="set:size:25"),
            ],
            [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")],
        ]
        await query.edit_message_text(
            "📏 Оберіть розмір:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @staticmethod
    async def set_setting_value(query, context, key: str, value: str):
        settings = get_qr_settings(context)

        if key == "fg_color":
            key = "fg"
        elif key == "bg_color":
            key = "bg"
        if key == "size":
            settings[key] = int(value)
        else:
            settings[key] = value
        context.user_data["qr_settings"] = settings
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")]]
        await query.edit_message_text(
            f"✅ {key.upper()} встановлено: {value}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    @staticmethod
    async def reset_settings(query, context):
        context.user_data["qr_settings"] = DEFAULT_QR_SETTINGS.copy()
        await query.edit_message_text(
            "✅ Налаштування скинуто до стандартних",
            reply_markup=InlineKeyboards.settings_menu(DEFAULT_QR_SETTINGS),
        )
