

# QR Bot — Telegram бот для генерації QR-кодів

Цей проект — багатофункціональний Telegram-бот для створення QR-кодів з тексту, посилань, WiFi, контактів тощо.

## Структура проекту

- bot.py — головний файл запуску бота
- config.py — налаштування (токен, параметри)
- requirements.txt — залежності
- handlers/ — логіка обробки команд, callback, налаштувань
- services/ — генерація QR, обробка тексту
- database/ — моделі та репозиторії для зберігання історії
- keyboards/ — inline-клавіатури
- utils/ — допоміжні функції

## Швидкий старт

1. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```
2. Додайте токен Telegram у файл .env:
   ```env
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   ```
   (Токен автоматично підтягується через config.py)
3. Запустіть бота:
   ```bash
   python bot.py
   ```

## Запуск через Docker

1. Побудуйте образ:
   ```bash
   docker build -t qr-bot .
   ```
2. Запустіть контейнер:
   ```bash
   docker run -e BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN qr-bot
   ```

## Функціонал
- Генерація QR-кодів для тексту, посилань, WiFi, контактів, email
- Вибір кольору, розміру, формату QR
- Збереження історії та статистика
- Інтуїтивне меню та шаблони

## Вимоги
- Python 3.11+
- python-telegram-bot
- qrcode
- pillow

## Обробка помилок
- Перевірте токен та підключення до інтернету
- Всі помилки логуються у файл bot.log

---

# QR Bot — Telegram bot for generating QR codes

This project is a multifunctional Telegram bot for creating QR codes from text, links, WiFi, contacts, and more.

## Project structure

- bot.py — main bot file
- config.py — settings (token, parameters)
- requirements.txt — dependencies
- handlers/ — command, callback, settings logic
- services/ — QR generation, text processing
- database/ — models and repositories for history
- keyboards/ — inline keyboards
- utils/ — helper functions

## Quick start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your Telegram token to the .env file:
   ```env
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   ```
   (Token is loaded automatically via config.py)
3. Run the bot:
   ```bash
   python bot.py
   ```

## Run with Docker

1. Build the image:
   ```bash
   docker build -t qr-bot .
   ```
2. Run the container:
   ```bash
   docker run -e BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN qr-bot
   ```

## Features
- Generate QR codes for text, links, WiFi, contacts, email
- Choose QR color, size, format
- Save history and view statistics
- Intuitive menu and templates

## Requirements
- Python 3.11+
- python-telegram-bot
- qrcode
- pillow

## Error handling
- Check your token and internet connection
- All errors are logged to bot.log

---
