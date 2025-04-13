from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_session import Session  # Добавлено для работы с сессиями
import os
import logging
import json
from datetime import datetime
from db_utils import (
    init_db, get_password, set_password, 
    load_products_data, save_products_data,
    load_hoz_data, load_fish_data
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Определение путей для данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')  # Храним данные в подкаталоге приложения

app = Flask(__name__)
app.secret_key = 'f7c8392f8a9e234b8f92e8c9d1a2b3c4'  # Случайный секретный ключ
# Добавляем настройки для сессий
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.join(BASE_DIR, 'flask_session')
Session(app)  # Инициализация Flask-Session

# Настройки Telegram бота
BOT_TOKEN = '7937013933:AAF_iuBecx-o0etgGZhEzWGxv3cBHWfDpYQ'
GROUP_ID = '-1002633190524'

# Создание необходимых директорий
def ensure_directories():
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logger.info(f"Директория {DATA_DIR} успешно создана")
        
        # Создаем директорию для сессий
        session_dir = os.path.join(BASE_DIR, 'flask_session')
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            logger.info(f"Директория {session_dir} успешно создана")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании директории: {e}")
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/check_password', methods=['POST'])
def check_password():
    try:
        entered_password = request.form.get('password')
        logger.info(f"Попытка входа с паролем: {entered_password}")
        
        correct_password = get_password('user')
        
        if correct_password and entered_password == correct_password:
            session['logged_in'] = True
            logger.info("Вход успешен, перенаправление на /menu")
            return redirect('/menu')
        else:
            logger.info("Неверный пароль")
    except Exception as e:
        logger.error(f"Ошибка проверки пароля: {e}")
    
    logger.info("Вход не удался, перенаправление на /login")
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
        return redirect('/login')
    
    hoz_products = load_hoz_data()
    
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
    
    return render_template('hoz.html', products=hoz_products)

@app.route('/fish', methods=['GET', 'POST'])
def fish():
    if not session.get('logged_in'):
        return redirect('/login')
    
    fish_products = load_fish_data()
    
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
    
    return render_template('fish.html', products=fish_products)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            correct_password = get_password('admin')
            
            entered_password = request.form.get('password')
            if correct_password and entered_password == correct_password:
                session['admin_logged_in'] = True
                return redirect('/admin')
        except Exception as e:
            logger.error(f"Ошибка входа в админ-панель: {e}")
        return redirect('/admin_login')
    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    products_data = load_products_data()
    return render_template('admin.html', products_data=products_data)

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
            set_password('user', new_password)
            logger.info("Пароль пользователя успешно изменен")
        elif password_type == 'admin':
            set_password('admin', new_password)
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

# Инициализация необходимых директорий и базы данных
ensure_directories()
init_db()

# Запуск приложения
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
