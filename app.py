from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import os
from datetime import datetime
import requests
import json
import logging
import inspect

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('app')

# Импортируем модули Supabase
try:
    from config import BOT_TOKEN, GROUP_ID
    from supabase_py_config import supabase, get_suppliers, get_products_by_supplier, get_all_products
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    # Если модуль не найден, создаем его
    if not os.path.exists('supabase_py_config.py'):
        with open('supabase_py_config.py', 'w') as f:
            f.write('''
from supabase import create_client
import os
import logging

logger = logging.getLogger('app')

# Получаем URL и ключ Supabase из переменных окружения или используем значения по умолчанию
url = os.environ.get("SUPABASE_URL", "https://wxlrektensoxrnwipsbs.supabase.co")
key = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4bHJla3RlbnNveHJud2lwc2JzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDU1NDk3NCwiZXhwIjoyMDYwMTMwOTc0fQ.45X6uk_ZfNvwLjmBOum2s3JZnm6KehUvImzzec0iWMc")

try:
    supabase = create_client(url, key)
    logger.info("Supabase клиент успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка при инициализации Supabase: {e}")
    raise

def get_suppliers():
    """Получить всех поставщиков"""
    response = supabase.table("suppliers").select("*").order("name").execute()
    return response.data

def get_products_by_supplier(supplier_id):
    """Получить все продукты по поставщику"""
    response = supabase.table("products").select("*").eq("supplier_id", supplier_id).order("name").execute()
    return response.data

def get_all_products():
    """Получить все продукты"""
    response = supabase.table("products").select("*, suppliers(name)").order("name").execute()
    return response.data

def get_request_with_items(request_id):
    """Получить заявку с товарами"""
    request = supabase.table("requests").select("*, suppliers(name), branches(name)").eq("id", request_id).single().execute()
    items = supabase.table("request_items").select("*, products(*)").eq("request_id", request_id).execute()
    
    return {
        "request": request.data,
        "items": items.data
    }

def get_password(password_type):
    """Получить пароль из базы данных"""
    response = supabase.table("settings").select("value").eq("key", f"{password_type}_password").single().execute()
    if response.data:
        return response.data['value']
    
    # Если пароль не найден, устанавливаем значение по умолчанию
    default_password = "1234" if password_type == "user" else "admin"
    supabase.table("settings").insert({"key": f"{password_type}_password", "value": default_password}).execute()
    return default_password

def set_password(password_type, new_password):
    """Установить пароль в базе данных"""
    response = supabase.table("settings").select("*").eq("key", f"{password_type}_password").execute()
    if response.data:
        supabase.table("settings").update({"value": new_password}).eq("key", f"{password_type}_password").execute()
    else:
        supabase.table("settings").insert({"key": f"{password_type}_password", "value": new_password}).execute()
    return True
''')
    
    # Создаем файл config.py, если его нет
    if not os.path.exists('config.py'):
        with open('config.py', 'w') as f:
            f.write('''
# Telegram Bot API Token
BOT_TOKEN = '7937013933:AAF_iuBecx-o0etgGZhEzWGxv3cBHWfDpYQ'

# Telegram Group ID
GROUP_ID = '-1002633190524'
''')
    
    # Перезагружаем модули
    from config import BOT_TOKEN, GROUP_ID
    from supabase_py_config import supabase, get_suppliers, get_products_by_supplier, get_all_products

# Проверяем наличие функций get_password и set_password в supabase_py_config
# Если их нет, добавляем их динамически
import supabase_py_config
import types

if not hasattr(supabase_py_config, 'get_password'):
    def get_password(password_type):
        """Получить пароль из базы данных"""
        try:
            response = supabase_py_config.supabase.table("settings").select("value").eq("key", f"{password_type}_password").single().execute()
            if response.data:
                return response.data['value']
            
            # Если пароль не найден, устанавливаем значение по умолчанию
            default_password = "1234" if password_type == "user" else "admin"
            supabase_py_config.supabase.table("settings").insert({"key": f"{password_type}_password", "value": default_password}).execute()
            return default_password
        except Exception as e:
            logger.error(f"Ошибка при получении пароля: {e}")
            return "1234" if password_type == "user" else "admin"
    
    # Добавляем функцию в модуль
    supabase_py_config.get_password = get_password

if not hasattr(supabase_py_config, 'set_password'):
    def set_password(password_type, new_password):
        """Установить пароль в базе данных"""
        try:
            response = supabase_py_config.supabase.table("settings").select("*").eq("key", f"{password_type}_password").execute()
            if response.data:
                supabase_py_config.supabase.table("settings").update({"value": new_password}).eq("key", f"{password_type}_password").execute()
            else:
                supabase_py_config.supabase.table("settings").insert({"key": f"{password_type}_password", "value": new_password}).execute()
            return True
        except Exception as e:
            logger.error(f"Ошибка при установке пароля: {e}")
            return False
    
    # Добавляем функцию в модуль
    supabase_py_config.set_password = set_password

# Теперь можно импортировать функции
from supabase_py_config import get_password, set_password

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Создаем директорию static, если её нет
if not os.path.exists('static'):
    os.makedirs('static')

# Создаем CSS файл, если его нет
if not os.path.exists('static/style.css'):
    with open('static/style.css', 'w') as f:
        f.write('''
/* Основные стили */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: "Roboto", Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1,
h2,
h3,
h4 {
  margin-bottom: 15px;
  color: #333;
}

a {
  color: #0066cc;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Формы */
.form-group {
  margin-bottom: 15px;
}

input,
select,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

textarea {
  resize: vertical;
}

.btn {
  display: inline-block;
  padding: 10px 15px;
  background-color: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  text-align: center;
}

.btn-primary {
  background-color: #0066cc;
}

.btn-secondary {
  background-color: #6c757d;
}

.btn-danger {
  background-color: #dc3545;
}

.btn-small {
  padding: 5px 10px;
  font-size: 14px;
}

.btn:hover {
  opacity: 0.9;
  text-decoration: none;
}

.btn-outline {
  background-color: transparent;
  color: #0066cc;
  border: 1px solid #0066cc;
}

.btn-outline:hover {
  background-color: #0066cc;
  color: white;
}

/* Сообщения */
.flash-messages {
  margin-bottom: 20px;
}

.flash-message {
  padding: 10px 15px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.flash-message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.flash-message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.flash-message.warning {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
}

.error-message {
  color: #dc3545;
  margin-top: 10px;
}

/* Страница входа */
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.login-form {
  margin-top: 20px;
}

.login-links {
  margin-top: 15px;
  text-align: center;
}

/* Меню */
.menu-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #eee;
  text-decoration: none;
  color: #333;
  transition: transform 0.2s, box-shadow 0.2s;
}

.menu-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  text-decoration: none;
}

.menu-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.menu-title {
  font-weight: bold;
  text-align: center;
}

/* Форма заявки */
.form-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.form-header {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.products-container {
  margin-bottom: 30px;
}

.products-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.product-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #eee;
}

.product-controls {
  display: flex;
  align-items: center;
}

.product-controls input {
  width: 80px;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}

/* Убираем стрелки у полей ввода чисел */
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { 
    -webkit-appearance: none; 
    margin: 0; 
}
input[type=number] {
    -moz-appearance: textfield; /* Firefox */
}

/* Админ-панель */
.admin-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.admin-sections {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

.section {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #eee;
}

.add-form {
  margin-bottom: 20px;
}

.add-form .form-group {
  display: flex;
  gap: 10px;
}

.add-form input,
.add-form select {
  flex: 1;
}

.add-form button {
  white-space: nowrap;
}

.suppliers-list,
.branches-list,
.products-list {
  list-style: none;
}

.supplier-item,
.branch-item,
.product-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin-bottom: 10px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #eee;
}

.inline-form {
  display: inline;
}

.supplier-name,
.branch-name,
.product-name {
  font-weight: bold;
}

.supplier-products {
  margin-bottom: 20px;
}

.password-forms {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.password-form {
  padding: 15px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #eee;
}

/* Таблицы */
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

th,
td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
}

tbody tr:hover {
  background-color: #f5f5f5;
}

/* Статусы заказов */
.status {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
}

.status-new {
  background-color: #cce5ff;
  color: #004085;
}

.status-processing {
  background-color: #fff3cd;
  color: #856404;
}

.status-delivering {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-completed {
  background-color: #d4edda;
  color: #155724;
}

.status-cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

/* Детали заявки */
.request-details-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.request-info {
  margin-bottom: 30px;
}

.info-section {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #eee;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  margin-bottom: 10px;
}

.label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
  color: #666;
}

/* Адаптивность */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .products-list {
    grid-template-columns: 1fr;
  }

  .add-form .form-group {
    flex-direction: column;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .password-forms {
    grid-template-columns: 1fr;
  }
}
''')

# Инициализация бота
logger.info("Бот успешно инициализирован")

def send_to_telegram(message):
    """Отправка сообщения в Telegram группу"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": GROUP_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при отправке в Telegram: {e}")
        return None

# Создаем таблицу settings, если её нет
def create_settings_table():
    try:
        # Проверяем, существует ли таблица settings
        try:
            response = supabase.table("settings").select("count").limit(1).execute()
            logger.info("Таблица settings существует")
        except Exception as e:
            logger.error(f"Ошибка при проверке таблицы settings: {e}")
            # Создаем таблицу settings через SQL
            try:
                # Проверяем, существуют ли пароли в таблице
                try:
                    user_password = get_password('user')
                    admin_password = get_password('admin')
                    logger.info("Пароли успешно получены из базы данных")
                except Exception as e:
                    logger.error(f"Ошибка при получении паролей: {e}")
                    # Добавляем пароли по умолчанию
                    try:
                        supabase.table("settings").insert({"key": "user_password", "value": "1234"}).execute()
                        supabase.table("settings").insert({"key": "admin_password", "value": "admin"}).execute()
                        logger.info("Пароли по умолчанию добавлены в базу данных")
                    except Exception as e:
                        logger.error(f"Ошибка при добавлении паролей по умолчанию: {e}")
            except Exception as e:
                logger.error(f"Ошибка при создании таблицы settings: {e}")
    except Exception as e:
        logger.error(f"Общая ошибка при создании таблицы settings: {e}")

# Вызываем функцию создания таблицы при запуске
create_settings_table()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        try:
            user_password = get_password('user')
            admin_password = get_password('admin')
            
            if password == user_password:
                session['user'] = True
                return redirect(url_for('menu'))
            elif password == admin_password:
                session['admin'] = True
                return redirect(url_for('admin'))
            return render_template('login.html', error='Неверный пароль')
        except Exception as e:
            logger.error(f"Ошибка при входе: {e}")
            # Если не удалось получить пароли из базы данных, используем значения по умолчанию
            if password == "1234":
                session['user'] = True
                return redirect(url_for('menu'))
            elif password == "admin":
                session['admin'] = True
                return redirect(url_for('admin'))
            return render_template('login.html', error='Неверный пароль')
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            password = request.form.get('password')
            try:
                admin_password = get_password('admin')
            except Exception as e:
                logger.error(f"Ошибка при получении пароля администратора: {e}")
                admin_password = "admin"  # Значение по умолчанию
            
            if password == admin_password:
                session['admin'] = True
                return redirect(url_for('admin'))
            else:
                flash('Неверный пароль', 'error')
        except Exception as e:
            logger.error(f"Ошибка входа в админ-панель: {e}")
            flash('Произошла ошибка при входе', 'error')
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if not session.get('user') and not session.get('admin'):
        return redirect(url_for('login'))
    
    # Получаем всех поставщиков
    suppliers = get_suppliers()
    return render_template('menu.html', suppliers=suppliers)

@app.route('/supplier/<supplier_id>', methods=['GET', 'POST'])
def supplier_form(supplier_id):
    if not session.get('user') and not session.get('admin'):
        return redirect(url_for('login'))
    
    # Получаем информацию о поставщике
    supplier_response = supabase.table("suppliers").select("*").eq("id", supplier_id).execute()
    if not supplier_response.data:
        flash('Поставщик не найден', 'error')
        return redirect(url_for('menu'))
    
    supplier = supplier_response.data[0]
    
    # Получаем продукты поставщика
    products = get_products_by_supplier(supplier_id)
    
    # Получаем список филиалов
    branches_response = supabase.table("branches").select("*").order("name").execute()
    branches = branches_response.data
    
    if request.method == 'POST':
        # Получаем данные формы
        cook_name = request.form.get('cook_name')
        fill_date = request.form.get('fill_date')
        request_date = request.form.get('request_date')
        branch_id = request.form.get('branch_id')
        
        # Проверяем, что все обязательные поля заполнены
        if not cook_name or not fill_date or not request_date or not branch_id:
            flash('Пожалуйста, заполните все обязательные поля формы', 'error')
            return render_template('supplier_form.html', 
                                  supplier=supplier, 
                                  products=products, 
                                  branches=branches, 
                                  today=datetime.now().strftime('%Y-%m-%d'))
        
        # Получаем название филиала
        branch_name = "Неизвестный филиал"
        for branch in branches:
            if str(branch['id']) == branch_id:
                branch_name = branch['name']
                break
        
        # Создаем новую заявку
        request_data = {
            "cook_name": cook_name,
            "fill_date": fill_date,
            "request_date": request_date,
            "branch_id": branch_id,
            "supplier_id": supplier_id,
            "created_at": datetime.now().isoformat()
        }
        
        request_response = supabase.table("requests").insert(request_data).execute()
        
        if len(request_response.data) > 0:
            request_id = request_response.data[0]['id']
            
            # Добавляем товары в заявку
            request_items = []
            selected_products = []
            
            for product in products:
                quantity_str = request.form.get(f'product_{product["id"]}')
                # Проверяем, что значение не пустое и содержит только цифры
                if quantity_str and quantity_str.strip() and quantity_str.strip().isdigit():
                    quantity = int(quantity_str.strip())
                    if quantity > 0:
                        request_items.append({
                            "request_id": request_id,
                            "product_id": product["id"],
                            "quantity": quantity
                        })
                        
                        selected_products.append({
                            "name": product["name"],
                            "quantity": quantity
                        })
            
            # Добавляем товары в заявку, если они есть
            if request_items:
                supabase.table("request_items").insert(request_items).execute()
            
            # Формируем сообщение для Telegram
            emoji = "📦"
            if supplier['name'] == "Рыба":
                emoji = "🐟"
            elif supplier['name'] == "Хоз. товары":
                emoji = "🧹"
            
            message = f"{emoji} <b>{supplier['name']}</b>\n"
            message += f"🏢 <b>Филиал:</b> {branch_name}\n"
            message += f"👨‍🍳 <b>Повар:</b> {cook_name}\n"
            message += f"📅 <b>Дата заявки:</b> {request_date}\n"
            message += f"📝 <b>Дата заполнения:</b> {fill_date}\n\n"
            
            if selected_products:
                for item in selected_products:
                    message += f"🔹 {item['name']}: {item['quantity']}\n"
            else:
                message += "Товары не выбраны\n"
            
            # Отправляем сообщение в Telegram
            telegram_response = send_to_telegram(message)
            
            if telegram_response and telegram_response.get('ok'):
                flash('Заявка успешно отправлена в Telegram!', 'success')
            else:
                flash('Заявка создана, но возникла проблема с отправкой в Telegram', 'warning')
            
            return redirect(url_for('menu'))
        else:
            flash('Ошибка при создании заявки', 'error')
    
    # Форматируем текущую дату для полей формы
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('supplier_form.html', 
                          supplier=supplier, 
                          products=products, 
                          branches=branches, 
                          today=today)

@app.route('/hoz', methods=['GET', 'POST'])
def hoz_form():
    if not session.get('user') and not session.get('admin'):
        return redirect(url_for('login'))
    
    # Получаем информацию о поставщике "Хоз. товары"
    supplier_response = supabase.table("suppliers").select("*").eq("name", "Хоз. товары").execute()
    if supplier_response.data:
        supplier_id = supplier_response.data[0]['id']
        return redirect(url_for('supplier_form', supplier_id=supplier_id))
    
    flash('Поставщик "Хоз. товары" не найден', 'error')
    return redirect(url_for('menu'))

@app.route('/fish', methods=['GET', 'POST'])
def fish_form():
    if not session.get('user') and not session.get('admin'):
        return redirect(url_for('login'))
    
    # Получаем информацию о поставщике "Рыба"
    supplier_response = supabase.table("suppliers").select("*").eq("name", "Рыба").execute()
    if supplier_response.data:
        supplier_id = supplier_response.data[0]['id']
        return redirect(url_for('supplier_form', supplier_id=supplier_id))
    
    flash('Поставщик "Рыба" не найден', 'error')
    return redirect(url_for('menu'))

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    # Получаем всех поставщиков
    suppliers = get_suppliers()
    
    # Получаем все продукты с информацией о поставщиках
    products_response = supabase.table("products").select("*, suppliers(id, name)").order("name").execute()
    products = products_response.data
    
    # Группируем продукты по поставщикам для удобного отображения
    products_by_supplier = {}
    for product in products:
        supplier_id = product['supplier_id']
        if supplier_id not in products_by_supplier:
            products_by_supplier[supplier_id] = []
        products_by_supplier[supplier_id].append(product)
    
    # Получаем все филиалы
    branches_response = supabase.table("branches").select("*").order("name").execute()
    branches = branches_response.data
    
    # Получаем все заявки
    requests_response = supabase.table("requests").select(
        "*, suppliers(name), branches(name)"
    ).order("created_at", desc=True).execute()
    requests = requests_response.data
    
    return render_template('admin.html', 
                          suppliers=suppliers, 
                          products=products, 
                          products_by_supplier=products_by_supplier,
                          branches=branches, 
                          requests=requests)

@app.route('/admin/add_supplier', methods=['POST'])
def add_supplier():
    if not session.get('admin'):
        return redirect(url_for('login'))
    name = request.form.get('name')
    supabase.table("suppliers").insert({"name": name}).execute()
    flash('Поставщик добавлен', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_supplier/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    supabase.table("suppliers").delete().eq("id", supplier_id).execute()
    flash('Поставщик удален', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('login'))
    name = request.form.get('name')
    supplier_id = request.form.get('supplier_id')
    
    supabase.table("products").insert({
        "name": name, 
        "supplier_id": supplier_id
    }).execute()
    
    flash('Товар добавлен', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    supabase.table("products").delete().eq("id", product_id).execute()
    flash('Товар удален', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/add_branch', methods=['POST'])
def add_branch():
    if not session.get('admin'):
        return redirect(url_for('login'))
    name = request.form.get('name')
    supabase.table("branches").insert({"name": name}).execute()
    flash('Филиал добавлен', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_branch/<int:branch_id>', methods=['POST'])
def delete_branch(branch_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    supabase.table("branches").delete().eq("id", branch_id).execute()
    flash('Филиал удален', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/change_password', methods=['POST'])
def change_password():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    password_type = request.form.get('password_type')
    new_password = request.form.get('new_password')
    
    try:
        # Сохраняем пароль в базе данных
        set_password(password_type, new_password)
        flash(f'Пароль {"пользователя" if password_type == "user" else "администратора"} изменен', 'success')
    except Exception as e:
        logger.error(f"Ошибка при изменении пароля: {e}")
        flash(f'Ошибка при изменении пароля: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/requests/<int:request_id>', methods=['GET'])
def view_request(request_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    request_response = supabase.table("requests").select(
        "*, suppliers(name), branches(name)"
    ).eq("id", request_id).execute()
    
    if not request_response.data:
        flash('Заявка не найдена', 'error')
        return redirect(url_for('admin'))
    
    request_data = request_response.data[0]
    
    # Получаем товары заявки с информацией о продуктах
    items_response = supabase.table("request_items").select(
        "*, products(id, name)"
    ).eq("request_id", request_id).execute()
    
    request_items = items_response.data
    
    return render_template('request_details.html', request=request_data, items=request_items)

@app.route('/admin/test_telegram', methods=['GET'])
def test_telegram():
    """Тестовый маршрут для проверки отправки в Telegram"""
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    message = "<b>🧪 Тестовое сообщение</b>\n\nПроверка работы отправки сообщений в Telegram."
    response = send_to_telegram(message)
    
    if response and response.get('ok'):
        flash('Тестовое сообщение успешно отправлено в Telegram!', 'success')
    else:
        flash(f'Ошибка при отправке в Telegram: {json.dumps(response)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/import_default_data', methods=['POST'])
def import_default_data():
    """Импорт данных по умолчанию"""
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    # Создаем поставщиков, если их нет
    suppliers = {
        'Свит Лайф': None,
        'Рафт': None,
        'Оши': None,
        'Хоз. товары': None,
        'Рыба': None
    }
    
    for supplier_name in suppliers.keys():
        result = supabase.table("suppliers").select("*").eq("name", supplier_name).execute()
        if result.data:
            suppliers[supplier_name] = result.data[0]['id']
        else:
            result = supabase.table("suppliers").insert({"name": supplier_name}).execute()
            suppliers[supplier_name] = result.data[0]['id']
    
    # Создаем филиалы, если их нет
    branches = ['Центральный', 'Северный', 'Южный', 'Западный', 'Восточный']
    for branch_name in branches:
        result = supabase.table("branches").select("*").eq("name", branch_name).execute()
        if not result.data:
            supabase.table("branches").insert({"name": branch_name}).execute()
    
    # Список продуктов для импорта
    default_products = {
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
    
    # Импортируем продукты
    for supplier_name, products_list in default_products.items():
        supplier_id = suppliers[supplier_name]
        for product_name in products_list:
            # Проверяем, существует ли уже такой продукт
            result = supabase.table("products").select("*").eq("name", product_name).execute()
            if not result.data:
                supabase.table("products").insert({
                    "name": product_name,
                    "supplier_id": supplier_id
                }).execute()
    
    flash('Данные по умолчанию успешно импортированы', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
