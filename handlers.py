from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils import generate_qr_image
import logging

logger = logging.getLogger(__name__)

# Дефолтні налаштування
DEFAULT_SETTINGS = {
    "fmt": "PNG",
    "size": 10,
    "fg": "black",
    "bg": "white"
}

# Клавіатури для налаштувань
FORMAT_KEYS = [
    [InlineKeyboardButton("PNG", callback_data="set:fmt:PNG"),
     InlineKeyboardButton("SVG", callback_data="set:fmt:SVG")],
    [InlineKeyboardButton("⬅ Назад", callback_data="menu:settings")]
]

SIZE_KEYS = [
    [InlineKeyboardButton("5", callback_data="set:size:5"),
     InlineKeyboardButton("10", callback_data="set:size:10"),
     InlineKeyboardButton("15", callback_data="set:size:15")],
    [InlineKeyboardButton("⬅ Назад", callback_data="menu:settings")]
]

FG_KEYS = [
    [InlineKeyboardButton("black", callback_data="set:fg:black"),
     InlineKeyboardButton("blue", callback_data="set:fg:blue"),
     InlineKeyboardButton("red", callback_data="set:fg:red")],
    [InlineKeyboardButton("⬅ Назад", callback_data="menu:settings")]
]

BG_KEYS = [
    [InlineKeyboardButton("white", callback_data="set:bg:white"),
     InlineKeyboardButton("yellow", callback_data="set:bg:yellow"),
     InlineKeyboardButton("gray", callback_data="set:bg:gray")],
    [InlineKeyboardButton("⬅ Назад", callback_data="menu:settings")]
]

MAIN_REPLY_KEYBOARD = [
    [KeyboardButton("Генерувати QR-код")],
    [KeyboardButton("Налаштування QR-коду")],
    [KeyboardButton("Допомога")]
]

# Клавіатура в режимі очікування тексту (з "Скасувати")
AWAITING_REPLY_KEYBOARD = [
    [KeyboardButton("Скасувати")],
    [KeyboardButton("Налаштування QR-коду")],
    [KeyboardButton("Допомога")]
]

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Стартова команда"""
    context.user_data["qr_settings"] = DEFAULT_SETTINGS.copy()
    context.user_data["awaiting_text"] = False

    main_reply_markup = ReplyKeyboardMarkup(MAIN_REPLY_KEYBOARD, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Привіт! Використовуйте меню нижче.",
        reply_markup=main_reply_markup
    )
# ===== HANDLE TEXT =====
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip() if update.message else None

    if not text:
        await update.message.reply_text("⚠️ Надішліть текст для генерації QR-коду.")
        return

    # Спочатку перевіряємо, чи текст є командою меню або "Скасувати" (пріоритетно)
    if text in ["Генерувати QR-код", "Налаштування QR-коду", "Допомога", "Скасувати"]:
        await handle_menu_option(update, context)
        return

    # Якщо не команда меню і awaiting_text True — генеруємо QR
    if context.user_data.get("awaiting_text"):
        settings = context.user_data.get("qr_settings", DEFAULT_SETTINGS)
        try:
            qr_image = generate_qr_image(
                text,
                size=settings.get("size", 10),
                fg_color=settings.get("fg", "black"),
                bg_color=settings.get("bg", "white"),
                fmt=settings.get("fmt", "PNG")
            )
            if settings.get("fmt", "PNG").upper() == "PNG":
                await update.message.reply_photo(photo=qr_image, caption="✅ Ось ваш QR-код (PNG)")
            else:
                await update.message.reply_document(document=qr_image, caption="✅ Ось ваш QR-код (SVG)")
        except Exception:
            logger.exception("QR generation failed")
            await update.message.reply_text("❌ Виникла помилка при генерації QR-коду.")
        finally:
            context.user_data["awaiting_text"] = False
            # Повертаємо стандартну клавіатуру після генерації
            main_reply_markup = ReplyKeyboardMarkup(MAIN_REPLY_KEYBOARD, resize_keyboard=True)
            await update.message.reply_text("✅ Готово! Використовуйте меню.", reply_markup=main_reply_markup)
        return

    # Якщо не awaiting_text і не команда — попередження
    await update.message.reply_text("⚠️ Невідома команда. Використовуйте меню.")

# ===== HANDLE MENU OPTION =====
async def handle_menu_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    main_reply_markup = ReplyKeyboardMarkup(MAIN_REPLY_KEYBOARD, resize_keyboard=True)
    awaiting_reply_markup = ReplyKeyboardMarkup(AWAITING_REPLY_KEYBOARD, resize_keyboard=True)

    if text == "Генерувати QR-код":
        context.user_data["awaiting_text"] = True
        await update.message.reply_text(
            "✏️ Надішліть текст або посилання для генерації QR-коду.",
            reply_markup=awaiting_reply_markup  # Оновлюємо клавіатуру з "Скасувати"
        )
    elif text == "Скасувати":
        context.user_data["awaiting_text"] = False
        await update.message.reply_text(
            "❌ Генерацію скасовано. Використовуйте меню.",
            reply_markup=main_reply_markup  # Повертаємо стандартну клавіатуру
        )
    elif text == "Налаштування QR-коду":
        context.user_data["awaiting_text"] = False  # Скидаємо awaiting_text
        await show_settings_menu(update, context)
    elif text == "Допомога":
        context.user_data["awaiting_text"] = False  # Скидаємо awaiting_text
        await update.message.reply_text(
            "ℹ️ Інструкція:\n"
            "- Натисніть 'Генерувати QR-код', щоб надіслати текст.\n"
            "- Налаштування дозволяють змінити розмір, кольори, формат.\n"
            "- Після вибору налаштувань надішліть текст для генерації.",
            reply_markup=main_reply_markup if context.user_data.get("awaiting_text") else None
        )
    else:
        await update.message.reply_text("⚠️ Невідома команда. Використовуйте меню.")

# ===== SHOW SETTINGS MENU =====
async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["awaiting_text"] = False  # Скидаємо awaiting_text при вході в налаштування
    settings = context.user_data.get("qr_settings", DEFAULT_SETTINGS.copy())
    keyboard = [
        [InlineKeyboardButton(f"Формат: {settings['fmt']}", callback_data="menu:fmt"),
         InlineKeyboardButton(f"Колір: {settings['fg']}", callback_data="menu:fg")],
        [InlineKeyboardButton(f"Фон: {settings['bg']}", callback_data="menu:bg"),
         InlineKeyboardButton(f"Розмір: {settings['size']}", callback_data="menu:size")],
        [InlineKeyboardButton("Скинути до дефолту", callback_data="menu:reset")],
        [InlineKeyboardButton("Готово", callback_data="menu:done")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔧 Налаштування QR-коду:", reply_markup=reply_markup)

# ===== BUTTON CALLBACK =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    settings = context.user_data.get("qr_settings", DEFAULT_SETTINGS.copy())

    # Обробка налаштувань
    if data.startswith("set:"):
        _, key, value = data.split(":")
        settings[key] = int(value) if key == "size" else value
        context.user_data["qr_settings"] = settings
        await show_settings_inline(query, settings)
        logger.info(f"User {query.from_user.id} set {key} to {value}")
        return

    # Обробка меню
    if data == "menu:reset":
        context.user_data["qr_settings"] = DEFAULT_SETTINGS.copy()
        context.user_data["awaiting_text"] = False
        await query.edit_message_text("♻️ Налаштування скинуто до стандартних.", reply_markup=None)
    elif data == "menu:done":
        context.user_data["awaiting_text"] = False
        await query.edit_message_text("✅ Налаштування збережено! Надішліть текст для QR-коду.", reply_markup=None)
    elif data == "menu:fmt":
        reply_markup = InlineKeyboardMarkup(FORMAT_KEYS)
        await query.edit_message_text("📄 Виберіть формат:", reply_markup=reply_markup)
    elif data == "menu:fg":
        reply_markup = InlineKeyboardMarkup(FG_KEYS)
        await query.edit_message_text("🎨 Виберіть колір тексту:", reply_markup=reply_markup)
    elif data == "menu:bg":
        reply_markup = InlineKeyboardMarkup(BG_KEYS)
        await query.edit_message_text("🎨 Виберіть колір фону:", reply_markup=reply_markup)
    elif data == "menu:size":
        reply_markup = InlineKeyboardMarkup(SIZE_KEYS)
        await query.edit_message_text("📏 Виберіть розмір:", reply_markup=reply_markup)
    elif data == "menu:settings":
        await show_settings_inline(query, settings)
    else:
        await show_settings_inline(query, settings)

# ===== SHOW SETTINGS INLINE =====
async def show_settings_inline(query, settings):
    keyboard = [
        [InlineKeyboardButton(f"Формат: {settings['fmt']}", callback_data="menu:fmt"),
         InlineKeyboardButton(f"Колір: {settings['fg']}", callback_data="menu:fg")],
        [InlineKeyboardButton(f"Фон: {settings['bg']}", callback_data="menu:bg"),
         InlineKeyboardButton(f"Розмір: {settings['size']}", callback_data="menu:size")],
        [InlineKeyboardButton("Скинути до дефолту", callback_data="menu:reset")],
        [InlineKeyboardButton("Готово", callback_data="menu:done")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    import time
    text = (
        f"🔧 Налаштування QR-коду:\n"
        f"Формат: {settings['fmt']}\n"
        f"Колір: {settings['fg']}\n"
        f"Фон: {settings['bg']}\n"
        f"Розмір: {settings['size']}\n"
        f"⏰ {int(time.time())}"
    )
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"Не вдалося змінити повідомлення: {e}")