import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import db_supabase

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Установка переменных окружения Supabase
os.environ['SUPABASE_URL'] = 'https://wxlrektensoxrnwipsbs.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4bHJla3RlbnNveHJud2lwc2JzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDU1NDk3NCwiZXhwIjoyMDYwMTMwOTc0fQ.45X6uk_ZfNvwLjmBOum2s3JZnm6KehUvImzzec0iWMc'

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на свой секретный ключ

# Определение путей для данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join('/tmp', 'data')  # Используем /tmp для Render
os.makedirs(DATA_DIR, exist_ok=True)

# Инициализация базы данных
db_supabase.initialize_db()

# Маршрут для инициализации базы данных
@app.route('/initialize')
def initialize():
    db_supabase.initialize_db()
    return "База данных инициализирована"

# Маршрут для статических файлов
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница входа
@app.route('/login')
def login():
    return render_template('login.html')

# Проверка пароля
@app.route('/check_password', methods=['POST'])
def check_password():
    password = request.form.get('password')
    if db_supabase.check_password(password, 'user'):
        session['logged_in'] = True
        return jsonify({'success': True, 'redirect': url_for('menu')})
    else:
        return jsonify({'success': False})

# Страница меню
@app.route('/menu')
def menu():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    products = db_supabase.get_products()
    return render_template('menu.html', products=products)

# Страница хоз. товаров
@app.route('/hoz')
def hoz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    hoz_items = db_supabase.get_hoz_items()
    return render_template('hoz.html', hoz_items=hoz_items)

# Страница рыбы
@app.route('/fish')
def fish():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    fish_items = db_supabase.get_fish_items()
    return render_template('fish.html', fish_items=fish_items)

# Страница курицы
@app.route('/chicken')
def chicken():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    chicken_items = db_supabase.get_chicken_items()
    return render_template('chicken.html', chicken_items=chicken_items)

# Отправка заказа
@app.route('/order', methods=['POST'])
def order():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    data = request.json
    items = data.get('items', [])
    
    if not items:
        return jsonify({'success': False, 'message': 'Не выбраны товары'})
    
    # Формируем сообщение для Telegram
    message = f"Новый заказ от {datetime.now().strftime('%d.%m.%Y %H:%M')}:\n\n"
    for item in items:
        message += f"- {item}\n"
    
    # Отправляем сообщение в Telegram
    try:
        telegram_token = os.environ.get('TELEGRAM_TOKEN', '6889051694:AAGnXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '-1002XXXXXXXXXX')
        
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return jsonify({'success': True})
        else:
            logger.error(f"Ошибка отправки в Telegram: {response.text}")
            return jsonify({'success': False, 'message': 'Ошибка отправки в Telegram'})
    
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# Страница входа в админ-панель
@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

# Проверка пароля администратора
@app.route('/admin_login', methods=['POST'])
def check_admin_password():
    password = request.form.get('password')
    if db_supabase.check_password(password, 'admin'):
        session['admin_logged_in'] = True
        return jsonify({'success': True, 'redirect': url_for('admin_panel')})
    else:
        return jsonify({'success': False})

# Админ-панель
@app.route('/admin')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    products = db_supabase.get_products()
    hoz_items = db_supabase.get_hoz_items()
    fish_items = db_supabase.get_fish_items()
    chicken_items = db_supabase.get_chicken_items()
    
    return render_template('admin.html', 
                          products=products, 
                          hoz_items=hoz_items, 
                          fish_items=fish_items, 
                          chicken_items=chicken_items)

# Выход из админ-панели
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# API для обновления продуктов
@app.route('/api/products', methods=['POST'])
def update_products():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    data = request.json
    products = data.get('products', {})
    
    if not products:
        return jsonify({'success': False, 'message': 'Нет данных для обновления'})
    
    try:
        db_supabase.update_products(products)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка обновления продуктов: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

# API для обновления хоз. товаров
@app.route('/api/hoz', methods=['POST'])
def update_hoz():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    data = request.json
    hoz_items = data.get('hoz_items', [])
    
    if not hoz_items:
        return jsonify({'success': False, 'message': 'Нет данных для обновления'})
    
    try:
        db_supabase.update_hoz_items(hoz_items)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка обновления хоз. товаров: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

# API для обновления рыбы
@app.route('/api/fish', methods=['POST'])
def update_fish():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    data = request.json
    fish_items = data.get('fish_items', [])
    
    if not fish_items:
        return jsonify({'success': False, 'message': 'Нет данных для обновления'})
    
    try:
        db_supabase.update_fish_items(fish_items)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка обновления рыбы: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

# API для обновления курицы
@app.route('/api/chicken', methods=['POST'])
def update_chicken():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    data = request.json
    chicken_items = data.get('chicken_items', [])
    
    if not chicken_items:
        return jsonify({'success': False, 'message': 'Нет данных для обновления'})
    
    try:
        db_supabase.update_chicken_items(chicken_items)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка обновления курицы: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

# API для обновления пароля
@app.route('/api/password', methods=['POST'])
def update_password():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Необходимо войти в систему'})
    
    data = request.json
    password_type = data.get('type')
    password = data.get('password')
    
    if not password_type or not password:
        return jsonify({'success': False, 'message': 'Не указан тип пароля или сам пароль'})
    
    try:
        db_supabase.update_password(password_type, password)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Ошибка обновления пароля: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

# Создаем директорию для статических файлов, если она не существует
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
css_dir = os.path.join(static_dir, 'css')
if not os.path.exists(css_dir):
    os.makedirs(css_dir, exist_ok=True)

# Создаем файл style.css, если он не существует
css_file = os.path.join(css_dir, 'style.css')
with open(css_file, 'w') as f:
    f.write("""
body {
    font-family: 'Roboto', Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: #4a76a8;
    color: white;
    padding: 15px 0;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

header h1 {
    margin: 0;
    font-size: 28px;
}

nav {
    display: flex;
    justify-content: center;
    background-color: #3a5e85;
    padding: 10px 0;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 0 15px;
    padding: 8px 15px;
    border-radius: 5px;
    transition: background-color 0.3s;
}

nav a:hover {
    background-color: #2c4a6b;
}

.login-form {
    max-width: 400px;
    margin: 50px auto;
    padding: 30px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.login-form h2 {
    text-align: center;
    margin-bottom: 30px;
    color: #4a76a8;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
    transition: border-color 0.3s;
}

.form-group input:focus {
    border-color: #4a76a8;
    outline: none;
}

.btn {
    display: inline-block;
    padding: 12px 20px;
    background-color: #4a76a8;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
    width: 100%;
}

.btn:hover {
    background-color: #3a5e85;
}

.error {
    color: #e74c3c;
    margin-bottom: 20px;
    padding: 10px;
    background-color: #fdecea;
    border-radius: 5px;
}

.product-list {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 30px;
}

.product-category {
    flex: 1;
    min-width: 300px;
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.05);
}

.product-category h3 {
    margin-top: 0;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
    color: #4a76a8;
}

.product-item {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 5px;
    transition: background-color 0.2s;
}

.product-item:hover {
    background-color: #f8f9fa;
}

.product-item input[type="checkbox"] {
    margin-right: 15px;
    transform: scale(1.2);
}

.product-item label {
    cursor: pointer;
    flex-grow: 1;
}

.product-item input[type="text"] {
    width: 60px;
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 3px;
    margin-left: 10px;
}

.order-btn {
    display: block;
    width: 100%;
    padding: 15px;
    background-color: #27ae60;
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 18px;
    cursor: pointer;
    margin-top: 30px;
    transition: background-color 0.3s;
}

.order-btn:hover {
    background-color: #219653;
}

.admin-panel {
    background-color: white;
    border-radius: 10px;
    padding: 30px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
    margin-top: 30px;
}

.admin-section {
    margin-bottom: 40px;
}

.admin-section h3 {
    margin-top: 0;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
    color: #4a76a8;
}

.admin-form {
    margin-top: 20px;
}

.admin-form textarea {
    width: 100%;
    height: 200px;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-family: monospace;
    font-size: 14px;
    resize: vertical;
}

.admin-form input[type="text"] {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-bottom: 15px;
    font-size: 16px;
}

.admin-form button {
    padding: 12px 20px;
    background-color: #4a76a8;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
}

.admin-form button:hover {
    background-color: #3a5e85;
}

.message {
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 5px;
}

.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.home-buttons {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    margin-top: 50px;
}

.home-button {
    display: block;
    width: 100%;
    max-width: 300px;
    padding: 15px 20px;
    background-color: #4a76a8;
    color: white;
    text-align: center;
    text-decoration: none;
    border-radius: 5px;
    font-size: 18px;
    transition: background-color 0.3s, transform 0.2s;
}

.home-button:hover {
    background-color: #3a5e85;
    transform: translateY(-2px);
}

.home-button.admin {
    background-color: #e74c3c;
}

.home-button.admin:hover {
    background-color: #c0392b;
}

.bot-check {
    margin-top: 50px;
    text-align: center;
    padding: 20px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.05);
}

.bot-check h3 {
    color: #4a76a8;
    margin-top: 0;
}

.bot-check p {
    margin-bottom: 20px;
}

.bot-check input {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 5px;
    width: 100%;
    max-width: 300px;
    margin-bottom: 15px;
    font-size: 16px;
}

.bot-check button {
    padding: 12px 20px;
    background-color: #4a76a8;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
}

.bot-check button:hover {
    background-color: #3a5e85;
}

@media (max-width: 768px) {
    .product-category {
        min-width: 100%;
    }
    
    nav {
        flex-direction: column;
        align-items: center;
    }
    
    nav a {
        margin: 5px 0;
        width: 80%;
        text-align: center;
    }
    
    .home-buttons {
        width: 90%;
        margin: 30px auto;
    }
    
    .home-button {
        width: 100%;
    }
    
    .login-form {
        width: 90%;
        margin: 30px auto;
    }
    
    .admin-panel {
        padding: 15px;
    }
    
    .admin-form textarea {
        height: 150px;
    }
    
    .product-item {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .product-item input[type="checkbox"] {
        margin-bottom: 10px;
    }
    
    .product-item input[type="text"] {
        width: 100%;
        margin-left: 0;
        margin-top: 10px;
    }
}
    """)

# Создаем директорию для шаблонов, если она не существует
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir, exist_ok=True)

# Создаем шаблон index.html
index_html = os.path.join(templates_dir, 'index.html')
with open(index_html, 'w') as f:
    f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Система заказов</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <div class="container">
            <h1>Система заказов</h1>
        </div>
    </header>
    
    <main class="container">
        <div class="home-buttons">
            <a href="{{ url_for('login') }}" class="home-button">Вход в систему</a>
            <a href="{{ url_for('admin_login') }}" class="home-button admin">Вход в админ-панель</a>
        </div>
        
        <div class="bot-check">
            <h3>Проверка бота</h3>
            <p>Введите код для проверки бота:</p>
            <input type="text" id="botCode" placeholder="Введите код">
            <button id="checkBot">Проверить</button>
            <div id="botResult"></div>
        </div>
    </main>
    
    <script>
        // Предотвращаем масштабирование на мобильных устройствах
        document.addEventListener('touchstart', function(event) {
            if (event.touches.length > 1) {
                event.preventDefault();
            }
        }, { passive: false });
        
        var lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            var now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // Проверка бота
        document.getElementById('checkBot').addEventListener('click', function() {
            var code = document.getElementById('botCode').value;
            var resultDiv = document.getElementById('botResult');
            
            if (code === '12345') {
                resultDiv.innerHTML = '<p style="color: green;">Бот работает!</p>';
            } else {
                resultDiv.innerHTML = '<p style="color: red;">Неверный код</p>';
            }
        });
    </script>
</body>
</html>""")

# Создаем шаблон login.html
login_html = os.path.join(templates_dir, 'login.html')
with open(login_html, 'w') as f:
    f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Вход | Система заказов</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <div class="container">
            <h1>Вход в систему</h1>
        </div>
    </header>
    
    <nav>
        <a href="{{ url_for('index') }}">Главная</a>
        <a href="{{ url_for('admin_login') }}">Админ</a>
    </nav>
    
    <main class="container">
        <div class="login-form">
            <h2>Вход</h2>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
            <form id="loginForm" method="post">
                <div class="form-group">
                    <label for="password">Пароль:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Войти</button>
            </form>
        </div>
    </main>
    
    <script>
        // Предотвращаем масштабирование на мобильных устройствах
        document.addEventListener('touchstart', function(event) {
            if (event.touches.length > 1) {
                event.preventDefault();
            }
        }, { passive: false });
        
        var lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            var now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            var password = document.getElementById('password').value;
            var formData = new FormData();
            formData.append('password', password);
            
            fetch('/check_password', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect;
                } else {
                    alert('Неверный пароль');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при входе');
            });
        });
    </script>
</body>
</html>""")

# Создаем шаблон admin_login.html
admin_login_html = os.path.join(templates_dir, 'admin_login.html')
with open(admin_login_html, 'w') as f:
    f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Админ | Система заказов</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <div class="container">
            <h1>Вход в админ-панель</h1>
        </div>
    </header>
    
    <nav>
        <a href="{{ url_for('index') }}">Главная</a>
        <a href="{{ url_for('login') }}">Вход</a>
    </nav>
    
    <main class="container">
        <div class="login-form">
            <h2>Вход в админ-панель</h2>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
            <form id="adminLoginForm" method="post">
                <div class="form-group">
                    <label for="password">Пароль:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Войти</button>
            </form>
        </div>
    </main>
    
    <script>
        // Предотвращаем масштабирование на мобильных устройствах
        document.addEventListener('touchstart', function(event) {
            if (event.touches.length > 1) {
                event.preventDefault();
            }
        }, { passive: false });
        
        var lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            var now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        document.getElementById('adminLoginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            var password = document.getElementById('password').value;
            var formData = new FormData();
            formData.append('password', password);
            
            fetch('/admin_login', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect;
                } else {
                    alert('Неверный пароль');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при входе');
            });
        });
    </script>
</body>
</html>""")

# Создаем шаблон menu.html
menu_html = os.path.join(templates_dir, 'menu.html')
with open(menu_html, 'w') as f:
    f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Меню | Система заказов</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <div class="container">
            <h1>Меню</h1>
        </div>
    </header>
    
    <nav>
        <a href="{{ url_for('index') }}">Главная</a>
        <a href="{{ url_for('menu') }}">Меню</a>
        <a href="{{ url_for('hoz') }}">Хоз. товары</a>
        <a href="{{ url_for('fish') }}">Рыба</a>
        <a href="{{ url_for('chicken') }}">Курица</a>
        <a href="{{ url_for('logout') }}">Выход</a>
    </nav>
    
    <main class="container">
        <div class="product-list">
            {% for supplier, items in products.items() %}
            <div class="product-category">
                <h3>{{ supplier }}</h3>
                {% for item in items %}
                <div class="product-item">
                    <input type="checkbox" id="product-{{ loop.index }}-{{ supplier|replace(' ', '-') }}" data-name="{{ item }}">
                    <label for="product-{{ loop.index }}-{{ supplier|replace(' ', '-') }}">{{ item }}</label>
                    <input type="text" placeholder="Кол-во" class="quantity">
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>

        <button id="orderBtn" class="order-btn">Отправить заказ</button>
    </main>
    
    <script>
        // Предотвращаем масштабирование на мобильных устройствах
        document.addEventListener('touchstart', function(event) {
            if (event.touches.length > 1) {
                event.preventDefault();
            }
        }, { passive: false });
        
        var lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            var now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        document.getElementById('orderBtn').addEventListener('click', function() {
            var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            var selectedItems = [];
            
            checkboxes.forEach(function(checkbox) {
                var quantity = checkbox.parentNode.querySelector('.quantity').value || '1';
                selectedItems.push(checkbox.dataset.name + ' (' + quantity + ')');
            });
            
            if (selectedItems.length === 0) {
                alert('Выберите хотя бы один товар');
                return;
            }
            
            fetch('/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    items: selectedItems
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Заказ успешно отправлен');
                    // Снимаем выделение со всех чекбоксов
                    checkboxes.forEach(function(checkbox) {
                        checkbox.checked = false;
                        checkbox.parentNode.querySelector('.quantity').value = '';
                    });
                } else {
                    alert('Ошибка: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке заказа');
            });
        });
    </script>
</body>
</html>""")

# Создаем шаблон hoz.html
hoz_html = os.path.join(templates_dir, 'hoz.html')
with open(hoz_html, 'w') as f:
    f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Хоз. товары | Система заказов</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <div class="container">
            <h1>Хоз. товары</h1>
        </div>
    </header>
    
    <nav>
        <a href="{{ url_for('index') }}">Главная</a>
        <a href="{{ url_for('menu') }}">Меню</a>
        <a href="{{ url_for('hoz') }}">Хоз. товары</a>
        <a href="{{ url_for('fish') }}">Рыба</a>
        <a href="{{ url_for('chicken') }}">Курица</a>
        <a href="{{ url_for('logout') }}">Выход</a>
    </nav>
    
    <main class="container">
        <div class="product-list">
            <div class="product-category">
                <h3>Хоз. товары</h3>
                {% for item in hoz_items %}
                <div class="product-item">
                    <input type="checkbox" id="hoz-{{ loop.index }}" data-name="{{ item }}">
                    <label for="hoz-{{ loop.index }}">{{ item }}</label>
                    <input type="text" placeholder="Кол-во" class="quantity">
                </div>
                {% endfor %}
            </div>
        </div>

        <button id="orderBtn" class="order-btn">Отправить заказ</button>
    </main>
    
    <script>
        // Предотвращаем масштабирование на мобильных устройствах
        document.addEventListener('touchstart', function(event) {
            if (event.touches.length > 1) {
                event.preventDefault();
            }
        }, { passive: false });
        
        var lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            var now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        document.getElementById('orderBtn').addEventListener('click', function() {
            var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            var selectedItems = [];
            
            checkboxes.forEach(function(checkbox) {
                var quantity = checkbox.parentNode.querySelector('.quantity').value || '1';
                selectedItems.push(checkbox.dataset.name + ' (' + quantity + ')');
            });
            
            if (selectedItems.length === 0) {
                alert('Выберите хотя бы один товар');
                return;
            }
            
            fetch('/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    items: selectedItems
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Заказ успешно отправлен');
                    // Снимаем выделение со всех чекбоксов
                    checkboxes.forEach(function(checkbox) {
                        checkbox.checked = false;
                        checkbox.parentNode.querySelector('.quantity').value = '';
                    });
                } else {
                    alert('Ошибка: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке заказа');
            });
        });
    </script>
</body>
</html>""")
