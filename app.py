from flask import Flask, render_template, request, redirect, session, url_for
import json
import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'f7c8392f8a9e234b8f92e8c9d1a2b3c4'  # Случайный секретный ключ

# Настройки Telegram бота
BOT_TOKEN = '7937013933:AAF_iuBecx-o0etgGZhEzWGxv3cBHWfDpYQ'
GROUP_ID = '-1002633190524'

# Определение путей для данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join('/tmp', 'data')  # Используем /tmp для Render
PASSWORD_FILE = os.path.join(DATA_DIR, 'password.txt')
ADMIN_PASSWORD_FILE = os.path.join(DATA_DIR, 'admin_password.txt')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')

# Создание необходимых директорий
def ensure_directories():
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logger.info(f"Директория {DATA_DIR} успешно создана")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании директории {DATA_DIR}: {e}")
        return False

# Инициализация файлов с паролями
def init_password_files():
    try:
        if not os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write('4444')
            logger.info(f"Создан файл с паролем пользователя: {PASSWORD_FILE}")

        if not os.path.exists(ADMIN_PASSWORD_FILE):
            with open(ADMIN_PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write('880088')
            logger.info(f"Создан файл с паролем администратора: {ADMIN_PASSWORD_FILE}")
    except Exception as e:
        logger.error(f"Ошибка инициализации файлов паролей: {e}")

# Инициализация необходимых файлов и папок
ensure_directories()
init_password_files()

@app.route('/')
def index():
    return "Приложение работает! Telegram бот будет добавлен позже."

# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
