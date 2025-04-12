from flask import Flask, render_template, request, redirect, session, url_for
import telebot
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
DATA_DIR = os.path.join(BASE_DIR, 'data')
PASSWORD_FILE = os.path.join(DATA_DIR, 'password.txt')
ADMIN_PASSWORD_FILE = os.path.join(DATA_DIR, 'admin_password.txt')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')

# Инициализация бота с обработкой ошибок
try:
    bot = telebot.TeleBot(BOT_TOKEN)
    logger.info("Бот успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации бота: {e}")
    bot = None

# Создание необходимых директорий
def ensure_directories():
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logger.info(f"Директория {DATA_DIR} успешно создана")
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании директории {DATA_DIR}: {e}")
        try:
            # Попробуем создать в /tmp для Render
            tmp_data_dir = os.path.join('/tmp', 'data')
            if not os.path.exists(tmp_data_dir):
                os.makedirs(tmp_data_dir)
                logger.info(f"Создана альтернативная директория: {tmp_data_dir}")
            global DATA_DIR, PASSWORD_FILE, ADMIN_PASSWORD_FILE, PRODUCTS_FILE
            DATA_DIR = tmp_data_dir
            PASSWORD_FILE = os.path.join(DATA_DIR, 'password.txt')
            ADMIN_PASSWORD_FILE = os.path.join(DATA_DIR, 'admin_password.txt')
            PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
            return True
        except Exception as e2:
            logger.error(f"Не удалось создать альтернативную директорию: {e2}")
            return False

# Функция для безопасной отправки сообщений
def safe_send_message(chat_id, text):
    if bot:
        try:
            message = bot.send_message(chat_id, text)
            logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
            return message
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            logger.debug(f"Текст сообщения: {text}")
    else:
        logger.warning("Бот не инициализирован")

# Инициализация файлов с паролями
def init_password_files():
    try:
        if not os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write('1234')
            logger.info(f"Создан файл с паролем пользователя: {PASSWORD_FILE}")

        if not os.path.exists(ADMIN_PASSWORD_FILE):
            with open(ADMIN_PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write('admin')
            logger.info(f"Создан файл с паролем администратора: {ADMIN_PASSWORD_FILE}")
    except Exception as e:
        logger.error(f"Ошибка инициализации файлов паролей: {e}")

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

# Создание структуры данных по умолчанию
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
        ],
        "Хоз. товары": [
            "Перчатки нитриловые черные размер L",
            "Перчатки нитриловые черные размер M",
            "Перчатки нитриловые черные размер S",
            "Салфетки бумажные белые 24х24 400шт",
            "Контейнер ПС-115 500мл с крышкой",
            "Контейнер ПС-115 750мл с крышкой",
            "Пакет фасовочный ПНД 24х37",
            "Пакет фасовочный ПНД 30х40",
            "Пленка пищевая 300мм х 200м",
            "Фольга алюминиевая 300мм х 100м",
            "Пакеты для мусора 120л (10шт)"
        ],
        "Рыба": [
            "Филе форели охл.",
            "Лосось атлантический охл.",
            "Тунец филе охл."
        ]
    }
    save_products_data(default_data)
    return default_data

def save_products_data(data):
    try:
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные о продуктах успешно сохранены в {PRODUCTS_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения products.json: {e}")

# Инициализация необходимых файлов и папок
if ensure_directories():
    init_password_files()
else:
    logger.critical("Не удалось создать необходимые директории. Приложение может работать некорректно.")

@app.route('/')
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
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('menu.html')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if not session.get('logged_in'):
        return redirect('/')
    
    products_data = load_products_data()
    
    if request.method == 'POST':
        supplier = request.form.get('supplier')
        name = request.form.get('name', '')
        date = request.form.get('date', '')
        target_date = request.form.get('target_date', '')
        branch = request.form.get('branch', '')
        
        if request.form.get('send'):
            items = []
            for key in request.form:
                if key not in ['supplier', 'name', 'date', 'target_date', 'branch', 'send']:
                    value = request.form.get(key)
                    if value and value.strip():
                        items.append(f"🔹 {key}: {value}")
            
            if items:
                message = (
                    f"📦 {supplier}\n"
                    f"🏢 Филиал: {branch}\n"
                    f"👨‍🍳 Повар: {name}\n"
                    f"📅 Дата заявки: {target_date}\n"
                    f"📝 Дата заполнения: {date}\n\n" +
                    "\n".join(items)
                )
                safe_send_message(GROUP_ID, message)
            return redirect('/menu')
        
        if supplier in products_data:
            products = products_data[supplier]
            return render_template('products.html', supplier=supplier, products=products)
    
    return render_template('products.html', supplier=None, suppliers=list(products_data.keys()))

@app.route('/hoz', methods=['GET', 'POST'])
def hoz():
    if not session.get('logged_in'):
        return redirect('/')
    
    products_data = load_products_data()
    
    if request.method == 'POST':
        name = request.form.get('name', '')
        date = request.form.get('date', '')
        target_date = request.form.get('target_date', '')
        branch = request.form.get('branch', '')
        
        items = []
        for key in request.form:
            if key not in ['name', 'date', 'target_date', 'branch', 'send']:
                value = request.form.get(key)
                if value and value.strip():
                    items.append(f"🔹 {key}: {value}")
        
        if items:
            message = (
                f"🧹 Хоз. товары\n"
                f"🏢 Филиал: {branch}\n"
                f"👨‍🍳 Повар: {name}\n"
                f"📅 Дата заявки: {target_date}\n"
                f"📝 Дата заполнения: {date}\n\n" +
                "\n".join(items)
            )
            safe_send_message(GROUP_ID, message)
        return redirect('/menu')
    
    return render_template('hoz.html', products=products_data.get("Хоз. товары", []))

@app.route('/fish', methods=['GET', 'POST'])
def fish():
    if not session.get('logged_in'):
        return redirect('/')
    
    products_data = load_products_data()
    
    if request.method == 'POST':
        name = request.form.get('name', '')
        date = request.form.get('date', '')
        target_date = request.form.get('target_date', '')
        branch = request.form.get('branch', '')
        
        items = []
        for key in request.form:
            if key not in ['name', 'date', 'target_date', 'branch', 'send']:
                value = request.form.get(key)
                if value and value.strip():
                    items.append(f"🔹 {key}: {value}")
        
        if items:
            message = (
                f"🐟 Рыба\n"
                f"🏢 Филиал: {branch}\n"
                f"👨‍🍳 Повар: {name}\n"
                f"📅 Дата заявки: {target_date}\n"
                f"📝 Дата заполнения: {date}\n\n" +
                "\n".join(items)
            )
            safe_send_message(GROUP_ID, message)
        return redirect('/menu')
    
    return render_template('fish.html', products=products_data.get("Рыба", []))

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    products_data = load_products_data()
    return render_template('admin.html', products_data=products_data)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            if os.path.exists(ADMIN_PASSWORD_FILE):
                with open(ADMIN_PASSWORD_FILE, 'r', encoding='utf-8') as f:
                    correct_password = f.read().strip()
                
                entered_password = request.form.get('password')
                if entered_password == correct_password:
                    session['admin_logged_in'] = True
                    return redirect('/admin')
            else:
                logger.warning(f"Файл с паролем администратора не найден: {ADMIN_PASSWORD_FILE}")
        except Exception as e:
            logger.error(f"Ошибка входа в админ-панель: {e}")
        return redirect('/admin_login')
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/')

@app.route('/change_password', methods=['POST'])
def change_password():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        password_type = request.form.get('password_type')
        new_password = request.form.get('new_password')
        
        if password_type == 'user':
            with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write(new_password)
            logger.info("Пароль пользователя успешно изменен")
        elif password_type == 'admin':
            with open(ADMIN_PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write(new_password)
            logger.info("Пароль администратора успешно изменен")
    except Exception as e:
        logger.error(f"Ошибка смены пароля: {e}")
    
    return redirect('/admin')

@app.route('/add_section', methods=['POST'])
def add_section():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        section_name = request.form.get('section_name')
        products_data = load_products_data()
        
        if section_name and section_name not in products_data:
            products_data[section_name] = []
            save_products_data(products_data)
            logger.info(f"Добавлен новый раздел: {section_name}")
    except Exception as e:
        logger.error(f"Ошибка добавления раздела: {e}")
    
    return redirect('/admin')

@app.route('/delete_section', methods=['POST'])
def delete_section():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        section_name = request.form.get('section_name')
        products_data = load_products_data()
        
        if section_name in products_data:
            del products_data[section_name]
            save_products_data(products_data)
            logger.info(f"Удален раздел: {section_name}")
    except Exception as e:
        logger.error(f"Ошибка удаления раздела: {e}")
    
    return redirect('/admin')

@app.route('/add_product', methods=['POST'])
def add_product():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        section_name = request.form.get('section_name')
        product_name = request.form.get('product_name')
        products_data = load_products_data()
        
        if section_name in products_data and product_name:
            if product_name not in products_data[section_name]:
                products_data[section_name].append(product_name)
                save_products_data(products_data)
                logger.info(f"Добавлен товар '{product_name}' в раздел '{section_name}'")
    except Exception as e:
        logger.error(f"Ошибка добавления товара: {e}")
    
    return redirect('/admin')

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        section_name = request.form.get('section_name')
        product_name = request.form.get('product_name')
        products_data = load_products_data()
        
        if section_name in products_data and product_name in products_data[section_name]:
            products_data[section_name].remove(product_name)
            save_products_data(products_data)
            logger.info(f"Удален товар '{product_name}' из раздела '{section_name}'")
    except Exception as e:
        logger.error(f"Ошибка удаления товара: {e}")
    
    return redirect('/admin')

# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
