
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
2. Додайте токен Telegram у config.py:
   ```python
   # config.py
   class settings:
       bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
   ```
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
