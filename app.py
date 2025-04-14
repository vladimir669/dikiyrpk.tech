from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_session import Session  # Добавлено для работы с сессиями
import os
import logging
import json
from datetime import datetime
from db_supabase import (
    init_db, get_password, set_password, 
    load_products_data, save_products_data,
    load_hoz_data, save_hoz_data,
    load_fish_data, save_fish_data,
    load_chicken_data, save_chicken_data,
    create_default_products, create_default_hoz,
    create_default_fish, create_default_chicken
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Определение путей для данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = '/tmp/persistent'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

app = Flask(__name__)
app.secret_key = 'f7c8392f8a9e234b8f92e8c9d1a2b3c4'  # Случайный секретный ключ
# Добавляем настройки для сессий
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.join(DATA_DIR, 'flask_session')
Session(app)  # Инициализация Flask-Session

# Настройки Telegram бота
BOT_TOKEN = '7937013933:AAF_iuBecx-o0etgGZhEzWGxv3cBHWfDpYQ'
GROUP_ID = '-1002633190524'

# Создание необходимых директорий
def ensure_directories():
    try:
        # Создаем директорию для сессий
        session_dir = os.path.join(DATA_DIR, 'flask_session')
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

# Инициализация базы данных при запуске
@app.before_first_request
def initialize():
    ensure_directories()
    init_db()
    
    # Принудительное обновление данных
    products_data = create_default_products()
    save_products_data(products_data)
    
    hoz_data = create_default_hoz()
    save_hoz_data(hoz_data)
    
    fish_data = create_default_fish()
    save_fish_data(fish_data)
    
    chicken_data = create_default_chicken()
    save_chicken_data(chicken_data)
    
    logger.info("Данные успешно обновлены")

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = get_password('user')
        
        if password == correct_password:
            session['logged_in'] = True
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error='Неверный пароль')
    
    return render_template('login.html')

# Страница меню
@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    products = load_products_data()
    return render_template('menu.html', products=products)

# Страница хоз. товаров
@app.route('/hoz')
def hoz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    hoz_items = load_hoz_data()
    return render_template('hoz.html', hoz_items=hoz_items)

# Страница рыбы
@app.route('/fish')
def fish():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    fish_items = load_fish_data()
    return render_template('fish.html', fish_items=fish_items)

# Страница курицы
@app.route('/chicken')
def chicken():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    chicken_items = load_chicken_data()
    return render_template('chicken.html', chicken_items=chicken_items)

# Обработка заказа
@app.route('/order', methods=['POST'])
def order():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    try:
        data = request.get_json()
        order_items = data.get('items', [])
        
        if not order_items:
            return jsonify({'success': False, 'message': 'Пустой заказ'})
        
        # Формируем текст сообщения
        now = datetime.now()
        message_text = f"Новый заказ от {now.strftime('%d.%m.%Y %H:%M')}\n\n"
        
        for item in order_items:
            message_text += f"• {item}\n"
        
        # Отправляем сообщение в Telegram
        result = safe_send_message(GROUP_ID, message_text)
        
        if result:
            return jsonify({'success': True, 'message': 'Заказ успешно отправлен'})
        else:
            return jsonify({'success': False, 'message': 'Ошибка отправки заказа'})
    
    except Exception as e:
        logger.error(f"Ошибка обработки заказа: {e}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# Страница входа в админку
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = get_password('admin')
        
        if password == correct_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('admin_login.html', error='Неверный пароль')
    
    return render_template('admin_login.html')

# Админ-панель
@app.route('/admin')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    products = load_products_data()
    hoz_items = load_hoz_data()
    fish_items = load_fish_data()
    chicken_items = load_chicken_data()
    
    return render_template('admin.html', 
                          products=products, 
                          hoz_items=hoz_items,
                          fish_items=fish_items,
                          chicken_items=chicken_items)

# API для обновления продуктов
@app.route('/api/products', methods=['POST'])
def update_products():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    try:
        data = request.get_json()
        products = data.get('products', {})
        
        if not products:
            return jsonify({'success': False, 'message': 'Нет данных для обновления'})
        
        # Сохраняем обновленные данные
        save_products_data(products)
        
        return jsonify({'success': True, 'message': 'Данные успешно обновлены'})
    
    except Exception as e:
        logger.error(f"Ошибка обновления продуктов: {e}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# API для обновления хоз. товаров
@app.route('/api/hoz', methods=['POST'])
def update_hoz():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    try:
        data = request.get_json()
        hoz_items = data.get('hoz_items', [])
        
        if not hoz_items:
            return jsonify({'success': False, 'message': 'Нет данных для обновления'})
        
        # Сохраняем обновленные данные
        save_hoz_data(hoz_items)
        
        return jsonify({'success': True, 'message': 'Данные успешно обновлены'})
    
    except Exception as e:
        logger.error(f"Ошибка обновления хоз. товаров: {e}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# API для обновления рыбы
@app.route('/api/fish', methods=['POST'])
def update_fish():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    try:
        data = request.get_json()
        fish_items = data.get('fish_items', [])
        
        if not fish_items:
            return jsonify({'success': False, 'message': 'Нет данных для обновления'})
        
        # Сохраняем обновленные данные
        save_fish_data(fish_items)
        
        return jsonify({'success': True, 'message': 'Данные успешно обновлены'})
    
    except Exception as e:
        logger.error(f"Ошибка обновления рыбы: {e}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# API для обновления курицы
@app.route('/api/chicken', methods=['POST'])
def update_chicken():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    try:
        data = request.get_json()
        chicken_items = data.get('chicken_items', [])
        
        if not chicken_items:
            return jsonify({'success': False, 'message': 'Нет данных для обновления'})
        
        # Сохраняем обновленные данные
        save_chicken_data(chicken_items)
        
        return jsonify({'success': True, 'message': 'Данные успешно обновлены'})
    
    except Exception as e:
        logger.error(f"Ошибка обновления курицы: {e}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# API для изменения пароля
@app.route('/api/password', methods=['POST'])
def update_password():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    try:
        data = request.get_json()
        password_type = data.get('type')
        new_password = data.get('password')
        
        if not password_type or not new_password:
            return jsonify({'success': False, 'message': 'Неверные параметры'})
        
        # Проверяем тип пароля
        if password_type not in ['user', 'admin']:
            return jsonify({'success': False, 'message': 'Неверный тип пароля'})
        
        # Сохраняем новый пароль
        set_password(password_type, new_password)
        
        return jsonify({'success': True, 'message': 'Пароль успешно изменен'})
    
    except Exception as e:
        logger.error(f"Ошибка изменения пароля: {e}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'})

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# Выход из админки
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
