"""Handler для налаштувань QR"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.base import BaseHandler
from keyboards.inline import InlineKeyboards
from constants import DEFAULT_QR_SETTINGS

class SettingsHandler(BaseHandler):
    @staticmethod
    async def show_settings(query, context):
        """Показ меню налаштувань"""
        settings = context.user_data.get("qr_settings", DEFAULT_QR_SETTINGS)
        await query.edit_message_text(
            "🔧 Налаштування QR коду:",
            reply_markup=InlineKeyboards.settings_menu(settings)
        )
    
    @staticmethod
    async def handle_format_setting(query, context):
        """Налаштування формату"""
        keyboard = [
            [InlineKeyboardButton("PNG", callback_data="set:fmt:PNG"),
             InlineKeyboardButton("SVG", callback_data="set:fmt:SVG")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")]
        ]
        await query.edit_message_text(
            "📄 Оберіть формат:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_size_setting(query, context):
        """Налаштування розміру"""
        keyboard = [
            [InlineKeyboardButton("5", callback_data="set:size:5"),
             InlineKeyboardButton("10", callback_data="set:size:10"),
             InlineKeyboardButton("15", callback_data="set:size:15")],
            [InlineKeyboardButton("20", callback_data="set:size:20"),
             InlineKeyboardButton("25", callback_data="set:size:25")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")]
        ]
        await query.edit_message_text(
            "📏 Оберіть розмір:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def set_setting_value(query, context, key: str, value: str):
        """Встановлення значення налаштування"""
        settings = context.user_data.get("qr_settings", DEFAULT_QR_SETTINGS.copy())
        
        if key == "size":
            settings[key] = int(value)
        else:
            settings[key] = value
        
        context.user_data["qr_settings"] = settings
        
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="action:settings")]]
        await query.edit_message_text(
            f"✅ {key.upper()} встановлено: {value}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )