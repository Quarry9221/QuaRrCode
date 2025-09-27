# QR Code Generator Telegram Bot

This project contains a simple Telegram bot for generating QR codes from user input.

## Структура
- qr_bot/
  - main.py
  - requirements.txt
  - README.md

## Запуск
1. Встановіть залежності:
   pip install -r requirements.txt
2. Додайте токен Telegram бота у main.py (замість YOUR_TELEGRAM_BOT_TOKEN)
3. Запустіть:
   python main.py

## Обробка помилок
- Якщо бот не відповідає, перевірте правильність токена та підключення до інтернету.
- Якщо не генерується QR-код, переконайтесь, що текст не порожній.
- Всі помилки логуються у консоль.

## Функціонал
- Приймає текст/посилання від користувача
- Відправляє QR-код у відповідь

## Вимоги
- Python 3.8+
- python-telegram-bot
- qrcode
- pillow
