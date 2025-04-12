from flask import Flask, render_template, request, redirect, session, g
import sqlite3
import os
import datetime
import telebot
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'database.db'
GROUP_ID = -4707270576

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_bot():
    db = get_db()
    bot_token = db.execute('SELECT token FROM bot_token LIMIT 1').fetchone()
    if bot_token:
        return telebot.TeleBot(bot_token['token'])
    return None

def safe_send_message(chat_id, message):
    bot = get_bot()
    if bot:
        try:
            bot.send_message(chat_id, message)
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {e}")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE name = ?', (name,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user'] = name
            return redirect('/menu')
        return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html')

@app.route('/menu')
def menu():
    if 'user' not in session:
        return redirect('/')
    return render_template('menu.html', name=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/products', methods=['GET', 'POST'])
def products():
    if 'user' not in session:
        return redirect('/')
    db = get_db()
    suppliers = db.execute('SELECT DISTINCT supplier FROM products').fetchall()

    selected_supplier = request.form.get('supplier') if request.method == 'POST' else None
    products = []
    if selected_supplier:
        products = db.execute('SELECT name FROM products WHERE supplier = ?', (selected_supplier,)).fetchall()

    if request.method == 'POST' and request.form.get('send'):
        name = request.form['name']
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        target_date = request.form['target_date']
        branch = request.form['branch']
        items = []
        for key in request.form:
            if key not in ['name', 'date', 'target_date', 'branch', 'supplier', 'send']:
                value = request.form.get(key)
                if value and value.strip():
                    items.append(f"🔹 {key}: {value}")
        if items:
            message = (
                f"🛒 Заявка на продукты\n"
                f"🏢 Филиал: {branch}\n"
                f"👨‍🍳 Повар: {name}\n"
                f"📅 Дата заявки: {target_date}\n"
                f"📝 Дата заполнения: {date}\n"
                f"🚚 Поставщик: {selected_supplier}\n\n" +
                "\n".join(items)
            )
            safe_send_message(GROUP_ID, message)
        return redirect('/menu')

    return render_template('products.html', suppliers=suppliers, products=products, selected_supplier=selected_supplier)

@app.route('/hoz', methods=['GET', 'POST'])
def hoz():
    if 'user' not in session:
        return redirect('/')
    db = get_db()
    hoz_products = db.execute("SELECT name FROM hoz_products").fetchall()

    if request.method == 'POST':
        name = request.form['name']
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        target_date = request.form['target_date']
        branch = request.form['branch']
        items = []
        for key in request.form:
            if key not in ['name', 'date', 'target_date', 'branch', 'send']:
                value = request.form.get(key)
                if value and value.strip():
                    items.append(f"🔹 {key}: {value}")
        if items:
            message = (
                f"🧼 Хозтовары\n"
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
    if 'user' not in session:
        return redirect('/')
    db = get_db()
    fish_products = db.execute("SELECT name FROM fish_products").fetchall()

    if request.method == 'POST':
        name = request.form['name']
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        target_date = request.form['target_date']
        branch = request.form['branch']
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

if __name__ == '__main__':
    app.run(debug=True)
