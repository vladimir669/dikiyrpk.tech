from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import os
import logging
import json
from datetime import datetime
import telebot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'f7c8392f8a9e234b8f92e8c9d1a2b3c4'  # Секретный ключ

# Настройки Telegram бота
BOT_TOKEN = '7937013933:AAF_iuBecx-o0etgGZhEzWGxv3cBHWfDpYQ'
GROUP_ID = '-1002633190524'

# Определение путей для данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join('/tmp', 'data')  # Для Render
PASSWORD_FILE = os.path.join(DATA_DIR, 'password.txt')
ADMIN_PASSWORD_FILE = os.path.join(DATA_DIR, 'admin_password.txt')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
HOZ_FILE = os.path.join(DATA_DIR, 'hoz.json')
FISH_FILE = os.path.join(DATA_DIR, 'fish.json')

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

# Создание структуры данных по умолчанию для продуктов
def create_default_products():
    default_data = {
        "Свит Лайф": [
            "Сыр полутвердый Моцарелла Пицца 40% Bonfesio Cooking 2.6кг",
            "Сыр Пармезан 9 Месяцев ЮКМП Цилиндр 45% 6-6.5кг",
            "Сыр \"Hochland\" плавленный ломтевой Бистро Чеддер 1.107кг (90 ломтиков)",
            "Крабовое мясо Снежный краб охл. (имитация из сурими) VICI 500гр",
            "Креветки б/г в панцире с/м Empacadora Bibo SA Эквадор 16/20 1кг",
            "Майонез классический SoPro 67% 9.6кг",
            "Соус Ореховый (кунжутный) Smart Chef 1л",
            "Соус Шрирача 0.815кг Uni-Eagle",
            "Соус Соевый classic Smart Chef 20л",
            "Кетчуп Smart Chef Томатный 2кг Балк",
            "Соус Smart Chef Сырный 1кг",
            "Соус Цезарь Астория 1кг",
            "Палочки Сырные Фрост-а Моцарелла в Панировке Замороженные 1кг",
            "Сухари Панировочные Smart Chef Панко Голд 4мм 1кг",
            "Имбирь Маринованный белый 1кг",
            "Водоросли цветные желтые (сухие) Мамэ нори 80гр*20л",
            "Водоросли цветные розовые (сухие) Мамэ нори 80гр*20л",
            "Масло Подсолнечное Smart Chef для фритюра 5л",
            "Мука пшеничная Царица Кубанская Высший Сорт 5кг",
            "Сахарный песок сумка Россия 5кг",
            "Порошок Васаби Tamaki 2кг"
        ],
        "Рафт": [
            "Масаго красная Санта-бремор",
            "Масаго черная Санта-бремор",
            "Масаго оранжевая Санта-бремор",
            "Водоросли Нори 100 листов, 240 г/уп, 72шт/кор, 17,28 кг/кор, Россия",
            "Соус Чили-манго \"Food Service\", 1кг, 6 шт/кор, 10415806, Гурмикс, Россия",
            "Картофельные дольки в кожуре со специями, уп. 0,9кг, замороженный, 9кг/кор, Tayyebat, Ливан",
            "Кунжутное семя обжаренное белое 1 кг, 15 шт/кор, СКМ, Россия",
            "Лук жареный 1 кг, 10 шт/кор, Нидерланды",
            "Сыр творожный Cream cheese 69% м.д.ж, 2,5кг, BeChef, БелСыр",
            "Луковые кольца",
            "Нагетсы серволюкс"
        ],
        "Оши": [
            "Угорь жаренный Унаги ТЕХ (в уп 10%)",
            "Тунец филе \"Елоу Фин\" Премиум",
            "Соус Унаги OSHI 1.8л",
            "Соус Кимчи 1.8л OSHI",
            "Картофель Фри Брусок 9*9 2.5кг*5, Lamb Weston",
            "Рис в/с Россия 25кг",
            "Уксус Рисовый OSHI 20л пр-во Космос"
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

# Функция сохранения данных о продуктах
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

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('menu.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if not session.get('logged_in'):
        return redirect('/login')
    
    products_data = load_products_data()
    
    if request.method == 'POST':
        supplier = request.form
