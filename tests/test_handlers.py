import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, ANY
from telegram import Update, Message, User, Chat, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
import handlers
from handlers import start, handle_text, handle_menu_option, button_callback, show_settings_inline, DEFAULT_SETTINGS, MAIN_REPLY_KEYBOARD, AWAITING_REPLY_KEYBOARD
from utils import generate_qr_image  # Припускаємо, що це імпортується

# Налаштування pytest для асинхронних тестів
pytestmark = pytest.mark.asyncio

# Фікстура для створення мок-об’єктів Update та Context
@pytest.fixture
def update():
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.from_user = MagicMock(spec=User)
    update.message.from_user.id = 12345
    update.message.chat = MagicMock(spec=Chat)
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    update.message.reply_document = AsyncMock()
    return update

@pytest.fixture
def context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context

@pytest.fixture
def callback_query_update():
    update = MagicMock(spec=Update)
    update.callback_query = MagicMock()
    update.callback_query.from_user = MagicMock(spec=User)
    update.callback_query.from_user.id = 12345
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    return update

# Тести для start
async def test_start_initializes_user_data_and_sends_message(update, context):
    await start(update, context)
    assert context.user_data == {"qr_settings": DEFAULT_SETTINGS.copy(), "awaiting_text": False}
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args
    assert call_args[0][0] == "👋 Привіт! Використовуйте меню нижче."
    assert isinstance(call_args[1]["reply_markup"], ReplyKeyboardMarkup)
    assert call_args[1]["reply_markup"].keyboard == MAIN_REPLY_KEYBOARD

# Тести для handle_text
async def test_handle_text_empty_text(update, context):
    update.message.text = ""
    await handle_text(update, context)
    update.message.reply_text.assert_called_once_with("⚠️ Надішліть текст для генерації QR-коду.")

async def test_handle_text_menu_option(update, context, mocker):
    update.message.text = "Налаштування QR-коду"
    mocker.patch("handlers.handle_menu_option", new=AsyncMock())
    await handle_text(update, context)
    handlers.handle_menu_option.assert_called_once_with(update, context)

async def test_handle_text_generate_qr_png(update, context, mocker):
    context.user_data["awaiting_text"] = True
    context.user_data["qr_settings"] = DEFAULT_SETTINGS.copy()
    update.message.text = "https://example.com"
    mock_qr_image = b"mocked_image_data"
    mocker.patch("utils.generate_qr_image", return_value=mock_qr_image)
    await handle_text(update, context)
    update.message.reply_photo.assert_called_once_with(photo=mock_qr_image, caption="✅ Ось ваш QR-код (PNG)")
    assert context.user_data["awaiting_text"] is False
    update.message.reply_text.assert_called_once_with("✅ Готово! Використовуйте меню.", reply_markup=mocker.ANY)

async def test_handle_text_generate_qr_svg(update, context, mocker):
    context.user_data["awaiting_text"] = True
    context.user_data["qr_settings"] = DEFAULT_SETTINGS.copy()
    context.user_data["qr_settings"]["fmt"] = "SVG"
    update.message.text = "https://example.com"
    mock_qr_image = b"mocked_svg_data"
    mocker.patch("utils.generate_qr_image", return_value=mock_qr_image)
    await handle_text(update, context)
    update.message.reply_document.assert_called_once_with(document=mock_qr_image, caption="✅ Ось ваш QR-код (SVG)")
    assert context.user_data["awaiting_text"] is False

async def test_handle_text_generate_qr_error(update, context, mocker):
    context.user_data["awaiting_text"] = True
    context.user_data["qr_settings"] = DEFAULT_SETTINGS.copy()
    update.message.text = "https://example.com"
    mocker.patch("utils.generate_qr_image", side_effect=Exception("QR generation failed"))
    await handle_text(update, context)
    update.message.reply_text.assert_called_once_with("❌ Виникла помилка при генерації QR-коду.")
    assert context.user_data["awaiting_text"] is False

async def test_handle_text_unknown_text(update, context):
    update.message.text = "random text"
    await handle_text(update, context)
    update.message.reply_text.assert_called_once_with("⚠️ Невідома команда. Використовуйте меню.")

# Тести для handle_menu_option
async def test_handle_menu_option_generate_qr(update, context):
    update.message.text = "Генерувати QR-код"
    await handle_menu_option(update, context)
    assert context.user_data["awaiting_text"] is True
    update.message.reply_text.assert_called_once_with(
        "✏️ Надішліть текст або посилання для генерації QR-коду.",
        reply_markup=ANY
    )

async def test_handle_menu_option_cancel(update, context):
    update.message.text = "Скасувати"
    context.user_data["awaiting_text"] = True
    await handle_menu_option(update, context)
    assert context.user_data["awaiting_text"] is False
    update.message.reply_text.assert_called_once_with(
        "❌ Генерацію скасовано. Використовуйте меню.",
        reply_markup=ANY
    )

async def test_handle_menu_option_settings(update, context, mocker):
    update.message.text = "Налаштування QR-коду"
    context.user_data["awaiting_text"] = True
    mocker.patch("handlers.show_settings_menu", new=AsyncMock())
    await handle_menu_option(update, context)
    assert context.user_data["awaiting_text"] is False
    handlers.show_settings_menu.assert_called_once_with(update, context)

async def test_handle_menu_option_help(update, context):
    update.message.text = "Допомога"
    context.user_data["awaiting_text"] = True
    await handle_menu_option(update, context)
    assert context.user_data["awaiting_text"] is False
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args
    assert "ℹ️ Інструкція:" in call_args[0][0]

async def test_handle_menu_option_unknown(update, context):
    update.message.text = "Невідома команда"
    await handle_menu_option(update, context)
    update.message.reply_text.assert_called_once_with("⚠️ Невідома команда. Використовуйте меню.")

# Тести для button_callback
async def test_button_callback_set_format(callback_query_update, context):
    callback_query_update.callback_query.data = "set:fmt:SVG"
    await button_callback(callback_query_update, context)
    assert context.user_data["qr_settings"]["fmt"] == "SVG"
    callback_query_update.callback_query.edit_message_text.assert_called_once()

async def test_button_callback_reset(callback_query_update, context):
    context.user_data["qr_settings"] = {"fmt": "SVG", "size": 15, "fg": "blue", "bg": "yellow"}
    context.user_data["awaiting_text"] = True
    callback_query_update.callback_query.data = "menu:reset"
    await button_callback(callback_query_update, context)
    assert context.user_data["qr_settings"] == DEFAULT_SETTINGS.copy()
    assert context.user_data["awaiting_text"] is False
    callback_query_update.callback_query.edit_message_text.assert_called_once_with(
        "♻️ Налаштування скинуто до стандартних.", reply_markup=None
    )

async def test_button_callback_done(callback_query_update, context):
    context.user_data["awaiting_text"] = True
    callback_query_update.callback_query.data = "menu:done"
    await button_callback(callback_query_update, context)
    assert context.user_data["awaiting_text"] is False
    callback_query_update.callback_query.edit_message_text.assert_called_once_with(
        "✅ Налаштування збережено! Надішліть текст для QR-коду.", reply_markup=None
    )

async def test_button_callback_show_format_menu(callback_query_update, context):
    callback_query_update.callback_query.data = "menu:fmt"
    await button_callback(callback_query_update, context)
    callback_query_update.callback_query.edit_message_text.assert_called_once_with(
        "📄 Виберіть формат:", reply_markup=ANY
    )

# Тести для show_settings_inline
async def test_show_settings_inline(callback_query_update, context):
    context.user_data["qr_settings"] = DEFAULT_SETTINGS.copy()
    await show_settings_inline(callback_query_update.callback_query, context.user_data["qr_settings"])
    callback_query_update.callback_query.edit_message_text.assert_called_once()
    call_args = callback_query_update.callback_query.edit_message_text.call_args
    assert "🔧 Налаштування QR-коду:" in call_args[0][0]
    assert isinstance(call_args[1]["reply_markup"], InlineKeyboardMarkup)