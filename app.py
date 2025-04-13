from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_session import Session
import os
import logging
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Папки
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = '/tmp/persistent'
os.makedirs(DATA_DIR, exist_ok=True)

# Flask и сессии
app = Flask(__name__)
app.secret_key = 'f7c8392f8a9e234b8f92e8c9d1a2b3c4'
app.config.update(
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=False,
    SESSION_USE_SIGNER=True,
    SESSION_FILE_DIR=os.path.join(DATA_DIR, 'flask_session')
)
Session(app)

# Telegram
BOT_TOKEN = '7937013933:AAF_iuBecx-o0etgGZhEzWGxv3cBHWfDpYQ'
GROUP_ID = '-1002633190524'

# Инициализация БД
session_dir = app.config['SESSION_FILE_DIR']
os.makedirs(session_dir, exist_ok=True)
init_db()
save_products_data(create_default_products())
save_hoz_data(create_default_hoz())
save_fish_data(create_default_fish())
save_chicken_data(create_default_chicken())
logger.info("Данные успешно обновлены")

# --- Роуты ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == get_password('user'):
            session['logged_in'] = True
            return redirect(url_for('menu'))
        return render_template('login.html', error='Неверный пароль')
    return render_template('login.html')

@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    products = load_products_data()
    return render_template('menu.html', products=products)

@app.route('/hoz')
def hoz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('hoz.html', hoz_items=load_hoz_data())

@app.route('/fish')
def fish():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('fish.html', fish_items=load_fish_data())

@app.route('/chicken')
def chicken():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('chicken.html', chicken_items=load_chicken_data())

@app.route('/order', methods=['POST'])
def order():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    try:
        from telebot import TeleBot
        data = request.get_json()
        if not data.get('items'):
            return jsonify({'success': False, 'message': 'Пустой заказ'})
        now = datetime.now()
        message_text = f"Новый заказ от {now.strftime('%d.%m.%Y %H:%M')}\n\n"
        message_text += '\n'.join(f"• {item}" for item in data['items'])
        bot = TeleBot(BOT_TOKEN)
        bot.send_message(GROUP_ID, message_text)
        return jsonify({'success': True, 'message': 'Заказ успешно отправлен'})
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- Админка ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == get_password('admin'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        return render_template('admin_login.html', error='Неверный пароль')
    return render_template('admin_login.html')

@app.route('/admin')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html',
        products=load_products_data(),
        hoz_items=load_hoz_data(),
        fish_items=load_fish_data(),
        chicken_items=load_chicken_data()
    )

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# --- API ---

@app.route('/api/products', methods=['POST'])
def update_products():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти'})
    try:
        save_products_data(request.get_json().get('products', {}))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/hoz', methods=['POST'])
def update_hoz():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти'})
    try:
        save_hoz_data(request.get_json().get('hoz_items', []))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/fish', methods=['POST'])
def update_fish():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти'})
    try:
        save_fish_data(request.get_json().get('fish_items', []))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/chicken', methods=['POST'])
def update_chicken():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти'})
    try:
        save_chicken_data(request.get_json().get('chicken_items', []))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/password', methods=['POST'])
def update_password():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти'})
    try:
        data = request.get_json()
        if data['type'] not in ['user', 'admin']:
            return jsonify({'success': False, 'message': 'Тип пароля неверен'})
        set_password(data['type'], data['password'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# --- Запуск локально ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
