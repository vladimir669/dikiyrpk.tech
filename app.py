from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from supabase_config import supabase, get_suppliers, get_products_by_supplier, get_all_products
from config import USER_PASSWORD, ADMIN_PASSWORD, BOT_TOKEN, GROUP_ID
import os
from datetime import datetime
import requests
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

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
        print(f"Ошибка при отправке в Telegram: {e}")
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == USER_PASSWORD:
            session['user'] = True
            return redirect(url_for('menu'))
        elif password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        return render_template('login.html', error='Неверный пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if not session.get('user') and not session.get('admin'):
        return redirect(url_for('login'))
    return render_template('menu.html')

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
                quantity = request.form.get(f'product_{product["id"]}')
                if quantity and quantity.isdigit() and int(quantity) > 0:
                    request_items.append({
                        "request_id": request_id,
                        "product_id": product["id"],
                        "quantity": int(quantity)
                    })
                    
                    selected_products.append({
                        "name": product["name"],
                        "quantity": int(quantity)
                    })
            
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
    
    suppliers = get_suppliers()
    products = get_all_products()
    
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
    
    if password_type == 'user':
        # Обновляем пароль пользователя в config.py
        with open('config.py', 'r') as f:
            lines = f.readlines()
        
        with open('config.py', 'w') as f:
            for line in lines:
                if line.startswith('USER_PASSWORD'):
                    f.write(f'USER_PASSWORD = "{new_password}"\n')
                else:
                    f.write(line)
        
        flash('Пароль пользователя изменен', 'success')
    
    elif password_type == 'admin':
        # Обновляем пароль администратора в config.py
        with open('config.py', 'r') as f:
            lines = f.readlines()
        
        with open('config.py', 'w') as f:
            for line in lines:
                if line.startswith('ADMIN_PASSWORD'):
                    f.write(f'ADMIN_PASSWORD = "{new_password}"\n')
                else:
                    f.write(line)
        
        flash('Пароль администратора изменен', 'success')
    
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
