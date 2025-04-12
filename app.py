from flask import Flask, render_template, request, redirect, session
import os
import logging
import json
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

# Функция для безопасной отправки сообщений в Telegram
def safe_send_message(chat_id, text):
    try:
        # Импортируем telebot только при необходимости отправки сообщения
        import telebot
        bot = telebot.TeleBot(BOT_TOKEN)
        message = bot.send_message(chat_id, text)
        logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
        return message
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return None

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

# Создание структуры данных по умолчанию
def create_default_products():
    default_data = {
        "Свит Лайф": [
            "Сыр полутвердый Моцарелла Пицца 40% Bonfesio Cooking 2.6кг",
            "Сыр Пармезан 9 Месяцев ЮКМП Цилиндр 45% 6-6.5кг",
            "Крабовое мясо Снежный краб охл. VICI 500гр"
        ],
        "Рафт": [
            "Масаго красная Санта-бремор",
            "Масаго черная Санта-бремор",
            "Масаго оранжевая Санта-бремор"
        ],
        "Оши": [
            "Соус Унаги OSHI 1.8л",
            "Соус Кимчи 1.8л OSHI",
            "Рис в/с Россия 25кг"
        ],
        "Хоз. товары": [
            "Перчатки нитриловые черные размер L",
            "Перчатки нитриловые черные размер M",
            "Перчатки нитриловые черные размер S"
        ],
        "Рыба": [
            "Филе форели охл."
        ]
    }
    save_products_data(default_data)
    return default_data

# Загрузка данных о продуктах
def load_products_data():
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Данные о продуктах успешно загружены из {PRODUCTS_FILE}")
                return data
    except Exception as e:
        logger.error(f"Ошибка загрузки products.json: {e}")
    
    logger.info("Создание структуры данных по умолчанию")
    return create_default_products()

def save_products_data(data):
    try:
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные о продуктах успешно сохранены в {PRODUCTS_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения products.json: {e}")

# Инициализация необходимых файлов и папок
ensure_directories()
init_password_files()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/check_password', methods=['POST'])
def check_password():
    try:
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
                correct_password = f.read().strip()
            
            entered_password = request.form.get('password')
            if entered_password == correct_password:
                session['logged_in'] = True
                return redirect('/menu')
        else:
            logger.warning(f"Файл с паролем не найден: {PASSWORD_FILE}")
    except Exception as e:
        logger.error(f"Ошибка проверки пароля: {e}")
    return redirect('/login')

@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('menu.html')

@app.route('/test_telegram')
def test_telegram():
    try:
        result = safe_send_message(GROUP_ID, "Тестовое сообщение с Render")
        if result:
            return "Сообщение успешно отправлено в Telegram!"
        else:
            return "Ошибка отправки сообщения. Проверьте логи."
    except Exception as e:
        logger.error(f"Ошибка в test_telegram: {e}")
        return f"Произошла ошибка: {str(e)}"

# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
