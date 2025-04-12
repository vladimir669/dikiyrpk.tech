import os
import json
import logging
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

DB_PATH = 'data.db'
DATA_DIR = '/tmp/data'
PRODUCTS_PATH = os.path.join(DATA_DIR, 'products.json')

os.makedirs(DATA_DIR, exist_ok=True)

# === База данных ===
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        conn.commit()
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('admin', 'adminpass'))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('telegram_token', 'YOUR_BOT_TOKEN'))
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('telegram_chat_id', '-4707270576'))
        conn.commit()

def get_setting(key):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None

def set_setting(key, value):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()

# === Работа с файлами ===
def save_products(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRODUCTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info("Данные о продуктах успешно сохранены в %s", PRODUCTS_PATH)

def load_products():
    if not os.path.exists(PRODUCTS_PATH):
        data = {
            "Свит Лайф": ["Шоколад", "Конфеты", "Вафли"],
            "Рафт": ["Молоко", "Сметана", "Йогурт"],
            "Оши": ["Рис", "Соевый соус", "Нори"]
        }
        save_products(data)
    with open(PRODUCTS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# === Авторизация ===
def check_user(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result and result[0] == password

# === Telegram ===
def send_to_telegram(message):
    token = get_setting("telegram_token")
    chat_id = get_setting("telegram_chat_id")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload)
    else:
        logging.warning("Токен или chat_id Telegram не установлен!")

# === Маршруты ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/check_password', methods=['POST'])
def check_password():
    password = request.form['password']
    if check_user('user', password):
        session['user'] = 'user'
        return redirect(url_for('menu'))
    flash("Неверный пароль")
    return redirect(url_for('login_page'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['admin'] = username
            return redirect(url_for('admin_panel'))
        flash("Неверный логин или пароль")
    return render_template('admin_login.html')

@app.route('/admin')
def admin_panel():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    products = load_products()
    return render_template('admin.html', products=products)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    new_pass = request.form['new_password']
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_pass,))
        conn.commit()
    logging.info("Пароль пользователя успешно изменен")
    return redirect(url_for('admin_panel'))

@app.route('/update_products', methods=['POST'])
def update_products():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    data = request.form.get('products')
    try:
        save_products(json.loads(data))
    except Exception as e:
        logging.error("Ошибка при сохранении: %s", e)
        flash("Ошибка в JSON")
    return redirect(url_for('admin_panel'))

@app.route('/submit_request', methods=['POST'])
def submit_request():
    supplier = request.form['supplier']
    chef_name = request.form['chef_name']
    order_date = request.form['order_date']
    completion_date = request.form['completion_date']
    branch = request.form['branch']

    items = []
    for key, value in request.form.items():
        if key.startswith('product_') and value:
            item_name = key.replace('product_', '')
            items.append(f"{item_name}: {value} г")

    message = f"📦 *Заявка от повара*\n🍽️ Повар: {chef_name}\n🏢 Филиал: {branch}\n🗓️ Дата заказа: {order_date}\n🕐 Срок исполнения: {completion_date}\n📚 Поставщик: {supplier}\n\n" + "\n".join(items)
    send_to_telegram(message)
    return redirect(url_for('menu'))

# === Инициализация ===
if __name__ == '__main__':
    init_db()
    load_products()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
