from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import os
from datetime import datetime
import requests
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('app')

# Импортируем модули Supabase
try:
    from config import USER_PASSWORD, ADMIN_PASSWORD, BOT_TOKEN, GROUP_ID
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
''')
    
    # Создаем файл config.py, если его нет
    if not os.path.exists('config.py'):
        with open('config.py', 'w') as f:
            f.write('''
# Пароль для обычных пользователей
USER_PASSWORD = "1234"

# Пароль для администратора
ADMIN_PASSWORD = "admin"

# Telegram Bot API Token
BOT_TOKEN = '7937013933:AAF_iuBecx-o0etgGZhEzWGxv3cBHWfDpYQ'

# Telegram Group ID
GROUP_ID = '-1002633190524'
''')
    
    # Перезагружаем модули
    from config import USER_PASSWORD, ADMIN_PASSWORD, BOT_TOKEN, GROUP_ID
    from supabase_py_config import supabase, get_suppliers, get_products_by_supplier, get_all_products

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

/* Остальные стили не изменены */
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

@app.route('/')
def index():
    return redirect(url_for('login'))

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
        
        # Получаем название филиала
        branch_name = next((branch['name'] for branch in branches if str(branch['id']) == branch_id), "Неизвестный филиал")
        
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
                quantity = request.form.get(f'product_{product["id"]}')
                try:
                    if quantity and int(quantity) > 0:
                        request_items.append({
                            "request_id": request_id,
                            "product_id": product["id"],
                            "quantity": int(quantity)
                        })
                        
                        selected_products.append({
                            "name": product["name"],
                            "quantity": int(quantity)
                        })
                except ValueError:
                    continue
            
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
                
                for item in selected_products:
                    message += f"🔹 {item['name']}: {item['quantity']}\n"
                
                # Отправляем сообщение в Telegram
                telegram_response = send_to_telegram(message)
                
                if telegram_response and telegram_response.get('ok'):
                    flash('Заявка успешно отправлена в Telegram!', 'success')
                else:
                    flash('Заявка создана, но возникла проблема с отправкой в Telegram', 'warning')
                
                return redirect(url_for('menu'))
            else:
                # Если нет товаров, удаляем созданную заявку
                supabase.table("requests").delete().eq("id", request_id).execute()
                flash('Пожалуйста, выберите хотя бы один товар', 'error')
        else:
            flash('Ошибка при создании заявки', 'error')
    
    # Форматируем текущую дату для полей формы
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('supplier_form.html', 
                          supplier=supplier, 
                          products=products, 
                          branches=branches, 
                          today=today)

# Остальные маршруты остаются без изменений
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
