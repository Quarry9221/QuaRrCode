from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class InlineKeyboards:
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Головне меню"""
        keyboard = [
            [InlineKeyboardButton("📱 Генерувати QR", callback_data="action:generate")],
            [InlineKeyboardButton("🔧 Налаштування", callback_data="action:settings"),
             InlineKeyboardButton("📊 Статистика", callback_data="action:stats")],
            [InlineKeyboardButton("📋 Шаблони", callback_data="action:templates"),
             InlineKeyboardButton("📜 Історія", callback_data="action:history")],
            [InlineKeyboardButton("ℹ️ Допомога", callback_data="action:help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def templates_menu() -> InlineKeyboardMarkup:
        """Меню шаблонів"""
        keyboard = [
            [InlineKeyboardButton("📶 WiFi", callback_data="template:wifi"),
             InlineKeyboardButton("👤 Контакт", callback_data="template:contact")],
            [InlineKeyboardButton("📧 Email", callback_data="template:email"),
             InlineKeyboardButton("📞 Телефон", callback_data="template:phone")],
            [InlineKeyboardButton("🌐 URL", callback_data="template:url")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="action:main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu(settings: dict) -> InlineKeyboardMarkup:
        """Меню налаштувань"""
        keyboard = [
            [InlineKeyboardButton(f"📄 Формат: {settings['fmt']}", callback_data="setting:format"),
             InlineKeyboardButton(f"📏 Розмір: {settings['size']}", callback_data="setting:size")],
            [InlineKeyboardButton(f"🎨 Колір: {settings['fg']}", callback_data="setting:fg_color"),
             InlineKeyboardButton(f"🎨 Фон: {settings['bg']}", callback_data="setting:bg_color")],
            [InlineKeyboardButton("♻️ Скинути", callback_data="setting:reset"),
             InlineKeyboardButton("✅ Готово", callback_data="action:main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Кнопка назад до головного меню"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Назад", callback_data="action:main")
        ]])