import os
import json
import logging
import telebot
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from supabase import create_client, Client

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройки Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wxlrektensoxrnwipsbs.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4bHJla3RlbnNveHJud2lwc2JzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDU1NDk3NCwiZXhwIjoyMDYwMTMwOTc0fQ.45X6uk_ZfNvwLjmBOum2s3JZnm6KehUvImzzec0iWMc")

# Настройки Telegram бота
BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN', '7937013933:AAF_iuBecx-o0etgGZhEzWGxv3cBHWfDpYQ')
GROUP_ID = os.environ.get('TELEGRAM_CHAT_ID', '-1002633190524')

app = Flask(__name__)
app.secret_key = 'f7c8392f8a9e234b8f92e8c9d1a2b3c4'  # Секретный ключ для сессий

# Инициализация бота с обработкой ошибок
try:
    bot = telebot.TeleBot(BOT_TOKEN)
    logger.info("Бот успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации бота: {e}")
    bot = None

# Инициализация клиента Supabase
supabase = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase клиент успешно инициализирован")
    else:
        logger.warning("Отсутствуют переменные окружения SUPABASE_URL или SUPABASE_KEY")
except Exception as e:
    logger.error(f"Ошибка инициализации Supabase клиента: {e}")

# Определение путей для данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
HOZ_FILE = os.path.join(DATA_DIR, 'hoz.json')
FISH_FILE = os.path.join(DATA_DIR, 'fish.json')
CHICKEN_FILE = os.path.join(DATA_DIR, 'chicken.json')
PASSWORD_FILE = os.path.join(DATA_DIR, 'password.txt')
ADMIN_PASSWORD_FILE = os.path.join(DATA_DIR, 'admin_password.txt')

# Функция для безопасной отправки сообщений в Telegram
def safe_send_message(chat_id, text):
    if bot:
        try:
            message = bot.send_message(chat_id, text)
            logger.info(f"Сообщение успешно отправлено в чат {chat_id}")
            return message
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            logger.error(f"Текст сообщения: {text}")
    else:
        logger.warning("Бот не инициализирован")

# Инициализация файлов с паролями
def init_password_files():
    if not os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
            f.write('1234')

    if not os.path.exists(ADMIN_PASSWORD_FILE):
        with open(ADMIN_PASSWORD_FILE, 'w', encoding='utf-8') as f:
            f.write('admin')

# Функции для работы с данными
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
            "Имбирь Маринованный белый Premium Fujin Китай1.4кг",
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
            "Тунец филе Tellowfin, сім, 500-800гр, Saku (сяку) Аками, ААА, кор. -10хг., Babdian Food (Fujian) Co, Ltd / 3500/02248. Китай",
            "Луковые кольца в панировке (формованые) зам.уп 0,908 кг, 8шт/кор., 7,264 кг/кор, Baby Star, Китай",
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
        ]
    }
    return default_data

def create_default_hoz():
    return [
        "CL 850 Крышка карт.лам. CL 850 мл. 212*108 (1/100/1200), CLARITY",
        "CL 850 Форма алюминиевая 850 мл, L-край, 218*112/181*76 h 62 мм,  (1/100/600), CLARITY",
        "FOREST clean Концентрат для мытья пола \"Лайм и мята\"  нейтральный запах 5 л н, Forest",
        "GraSS Средство для мытья посуды Velly light (зеленое яблоко) 5кг (арт.125469) н , GraSS",
        "GraSS Средство чистящее дезинфиц. гель густой DOS GEL 5,3л (арт.125240) , GraSS",
        "Гель \"Белизна\" ЧИСТОЛЮБ 3 в1 750 мл Домбытхим (1/16), ДомБытХим",
        "Контейнер 1000мл ЧЕРНЫЙ 150*200*55 (50/300)  ONECLICK BOTTON  1000/bBLACK, 1ЕА",
        "Контейнер 500мл ЧЕРНЫЙ 120*160*45 (50/400) ONECLICK BOTTON  500/bBLACK , 1ЕА",
        "Контейнер 800мл ЧЕРНЫЙ 120*200*55 (50/300)  ONECLICK BOTTON  800/bBLACK , 1ЕА",
        "Крышка 20мм к контейнеру 500мл (50/400)  ONECLICK LID 500/20 , 1ЕА",
        "Крышка 20мм к контейнеру 800мл (50/300)  ONECLICK LID 800/20, 1ЕА",
        "Крышка плоская к контейнеру 1000мл (50/300) ONECLICK LID 1000/0, 1ЕА",
        "Мешок д/мусора ПВД 240л 50мкм 10 шт/рол (1/10 рол), Сфера",
        "Пакет КРАФТ без ручки 320*200*340 80гр (1/20/300) , ЭЛВИ Групп",
        "Пакет КРАФТ с крученной ручкой 240*140*280 (1/300)н, Монолит",
        "Пакет КРАФТ с плоской ручкой 280*150*320 (1/250), Монолит",
        "Палочки для суши в индив. полиэт. упаковке 20 см круглые+зубочистка 100шт/уп (1/20уп) ГТД н, Лигапроф",
        "Перчатки винил. неопудр. черные L SAF&TY 100шт/уп (1/10уп) (ндс 10%) ГТД, Сейфити",
        "Перчатки винил. неопудр. черные M SAF&TY 100шт/уп (1/10уп) (ндс 10%) ГТД, Сейфити",
        "Перчатки винил. неопудр. черные S SAF&TY 100шт/уп (1/10уп) (ндс 10%) ГТД, Сейфити",
        "Пищевая пленка 450*200  (5,5мк) белая \"ДЕСНОГОР\" 1/10, ASD",
        "Термолента  57*30 D ЭКО (1/8/216), ФОРМУЛА Т",
        "Упаковка OSQ 600мл Meal Box S 118х118х65мм (1/450), OSQ"
    ]

def create_default_fish():
    return ["Филе форели охл."]

def create_default_chicken():
    return ["Филе куриное копч."]

# Функции для загрузки и сохранения данных
def save_products_data(data):
    if supabase:
        try:
            # Получаем текущие данные
            current_data = {}
            response = supabase.table('products').select('*').execute()
            if response.data:
                for item in response.data:
                    supplier = item.get('supplier', '')
                    name = item.get('name', '')
                    id = item.get('id', '')
                    
                    if supplier and name and id:
                        if supplier not in current_data:
                            current_data[supplier] = {}
                        current_data[supplier][name] = id
            
            # Удаляем записи, которых нет в новых данных
            for supplier, items in current_data.items():
                if supplier not in data:
                    # Удаляем все записи этого поставщика
                    for name, id in items.items():
                        try:
                            supabase.table('products').delete().eq('id', id).execute()
                        except Exception as e:
                            logger.error(f"Ошибка удаления продукта {name}: {e}")
                else:
                    # Удаляем записи, которых нет в новых данных
                    for name, id in items.items():
                        if name not in data[supplier]:
                            try:
                                supabase.table('products').delete().eq('id', id).execute()
                            except Exception as e:
                                logger.error(f"Ошибка удаления продукта {name}: {e}")
            
            # Добавляем новые записи
            for supplier, items in data.items():
                for name in items:
                    if supplier in current_data and name in current_data[supplier]:
                        # Запись уже существует, пропускаем
                        continue
                    
                    # Добавляем новую запись
                    try:
                        supabase.table('products').insert({
                            'name': name,
                            'supplier': supplier
                        }).execute()
                    except Exception as e:
                        logger.error(f"Ошибка добавления продукта {name}: {e}")
            
            logger.info("Данные о продуктах успешно сохранены в Supabase")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных о продуктах в Supabase: {e}")
            # Если не удалось сохранить в Supabase, сохраняем локально
            _save(PRODUCTS_FILE, data)
    else:
        # Если Supabase не инициализирован, сохраняем локально
        _save(PRODUCTS_FILE, data)

def load_products_data():
    if supabase:
        try:
            # Получаем все продукты
            response = supabase.table('products').select('*').execute()
            
            # Группируем по поставщику
            result = {}
            if response.data:
                for item in response.data:
                    supplier = item.get('supplier', '')
                    name = item.get('name', '')
                    
                    if supplier and name:
                        if supplier not in result:
                            result[supplier] = []
                        result[supplier].append(name)
                
                logger.info("Данные о продуктах успешно загружены из Supabase")
                return result
            else:
                # Если данных нет, возвращаем значения по умолчанию
                default_data = create_default_products()
                # Сохраняем значения по умолчанию в базу
                save_products_data(default_data)
                return default_data
        except Exception as e:
            logger.error(f"Ошибка загрузки данных о продуктах из Supabase: {e}")
            # Если не удалось загрузить из Supabase, загружаем локально
            return _load(PRODUCTS_FILE) or create_default_products()
    else:
        # Если Supabase не инициализирован, загружаем локально
        return _load(PRODUCTS_FILE) or create_default_products()

def save_hoz_data(data):
    if supabase:
        try:
            # Получаем текущие данные
            current_data = {}
            response = supabase.table('hoz').select('*').execute()
            if response.data:
                for item in response.data:
                    name = item.get('name', '')
                    id = item.get('id', '')
                    
                    if name and id:
                        current_data[name] = id
            
            # Удаляем записи, которых нет в новых данных
            for name, id in current_data.items():
                if name not in data:
                    try:
                        supabase.table('hoz').delete().eq('id', id).execute()
                    except Exception as e:
                        logger.error(f"Ошибка удаления хоз. товара {name}: {e}")
            
            # Добавляем новые записи
            for name in data:
                if name in current_data:
                    # Запись уже существует, пропускаем
                    continue
                
                # Добавляем новую запись
                try:
                    supabase.table('hoz').insert({
                        'name': name,
                        'supplier': 'Хоз. товары'
                    }).execute()
                except Exception as e:
                    logger.error(f"Ошибка добавления хоз. товара {name}: {e}")
            
            logger.info("Данные о хоз. товарах успешно сохранены в Supabase")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных о хоз. товарах в Supabase: {e}")
            # Если не удалось сохранить в Supabase, сохраняем локально
            _save(HOZ_FILE, data)
    else:
        # Если Supabase не инициализирован, сохраняем локально
        _save(HOZ_FILE, data)

def load_hoz_data():
    if supabase:
        try:
            # Получаем все хоз. товары
            response = supabase.table('hoz').select('*').execute()
            
            # Преобразуем в список
            result = []
            if response.data:
                for item in response.data:
                    name = item.get('name', '')
                    if name:
                        result.append(name)
                
                logger.info("Данные о хоз. товарах успешно загружены из Supabase")
                return result
            else:
                # Если данных нет, возвращаем значения по умолчанию
                default_data = create_default_hoz()
                # Сохраняем значения по умолчанию в базу
                save_hoz_data(default_data)
                return default_data
        except Exception as e:
            logger.error(f"Ошибка загрузки данных о хоз. товарах из Supabase: {e}")
            # Если не удалось загрузить из Supabase, загружаем локально
            return _load(HOZ_FILE) or create_default_hoz()
    else:
        # Если Supabase не инициализирован, загружаем локально
        return _load(HOZ_FILE) or create_default_hoz()

def save_fish_data(data):
    if supabase:
        try:
            # Получаем текущие данные
            current_data = {}
            response = supabase.table('fish').select('*').execute()
            if response.data:
                for item in response.data:
                    name = item.get('name', '')
                    id = item.get('id', '')
                    
                    if name and id:
                        current_data[name] = id
            
            # Удаляем записи, которых нет в новых данных
            for name, id in current_data.items():
                if name not in data:
                    try:
                        supabase.table('fish').delete().eq('id', id).execute()
                    except Exception as e:
                        logger.error(f"Ошибка удаления рыбы {name}: {e}")
            
            # Добавляем новые записи
            for name in data:
                if name in current_data:
                    # Запись уже существует, пропускаем
                    continue
                
                # Добавляем новую запись
                try:
                    supabase.table('fish').insert({
                        'name': name,
                        'supplier': 'Рыба'
                    }).execute()
                except Exception as e:
                    logger.error(f"Ошибка добавления рыбы {name}: {e}")
            
            logger.info("Данные о рыбе успешно сохранены в Supabase")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных о рыбе в Supabase: {e}")
            # Если не удалось сохранить в Supabase, сохраняем локально
            _save(FISH_FILE, data)
    else:
        # Если Supabase не инициализирован, сохраняем локально
        _save(FISH_FILE, data)

def load_fish_data():
    if supabase:
        try:
            # Получаем все рыбные товары
            response = supabase.table('fish').select('*').execute()
            
            # Преобразуем в список
            result = []
            if response.data:
                for item in response.data:
                    name = item.get('name', '')
                    if name:
                        result.append(name)
                
                logger.info("Данные о рыбе успешно загружены из Supabase")
                return result
            else:
                # Если данных нет, возвращаем значения по умолчанию
                default_data = create_default_fish()
                # Сохраняем значения по умолчанию в базу
                save_fish_data(default_data)
                return default_data
        except Exception as e:
            logger.error(f"Ошибка загрузки данных о рыбе из Supabase: {e}")
            # Если не удалось загрузить из Supabase, загружаем локально
            return _load(FISH_FILE) or create_default_fish()
    else:
        # Если Supabase не инициализирован, загружаем локально
        return _load(FISH_FILE) or create_default_fish()

def save_chicken_data(data):
    if supabase:
        try:
            # Получаем текущие данные
            current_data = {}
            response = supabase.table('chicken').select('*').execute()
            if response.data:
                for item in response.data:
                    name = item.get('name', '')
                    id = item.get('id', '')
                    
                    if name and id:
                        current_data[name] = id
            
            # Удаляем записи, которых нет в новых данных
            for name, id in current_data.items():
                if name not in data:
                    try:
                        supabase.table('chicken').delete().eq('id', id).execute()
                    except Exception as e:
                        logger.error(f"Ошибка удаления курицы {name}: {e}")
            
            # Добавляем новые записи
            for name in data:
                if name in current_data:
                    # Запись уже существует, пропускаем
                    continue
                
                # Добавляем новую запись
                try:
                    supabase.table('chicken').insert({
                        'name': name,
                        'supplier': 'Курица'
                    }).execute()
                except Exception as e:
                    logger.error(f"Ошибка добавления курицы {name}: {e}")
            
            logger.info("Данные о курице успешно сохранены в Supabase")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных о курице в Supabase: {e}")
            # Если не удалось сохранить в Supabase, сохраняем локально
            _save(CHICKEN_FILE, data)
    else:
        # Если Supabase не инициализирован, сохраняем локально
        _save(CHICKEN_FILE, data)

def load_chicken_data():
    if supabase:
        try:
            # Получаем все куриные товары
            response = supabase.table('chicken').select('*').execute()
            
            # Преобразуем в список
            result = []
            if response.data:
                for item in response.data:
                    name = item.get('name', '')
                    if name:
                        result.append(name)
                
                logger.info("Данные о курице успешно загружены из Supabase")
                return result
            else:
                # Если данных нет, возвращаем значения по умолчанию
                default_data = create_default_chicken()
                # Сохраняем значения по умолчанию в базу
                save_chicken_data(default_data)
                return default_data
        except Exception as e:
            logger.error(f"Ошибка загрузки данных о курице из Supabase: {e}")
            # Если не удалось загрузить из Supabase, загружаем локально
            return _load(CHICKEN_FILE) or create_default_chicken()
    else:
        # Если Supabase не инициализирован, загружаем локально
        return _load(CHICKEN_FILE) or create_default_chicken()

def _save(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные успешно сохранены в {filepath}")
    except Exception as e:
        logger.error(f"Ошибка сохранения данных в {filepath}: {e}")

def _load(filepath):
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки данных из {filepath}: {e}")
        return None

def check_password(password, password_type='user'):
    if supabase:
        try:
            # Получаем пароли из Supabase
            response = supabase.table('passwords').select('*').execute()
            if response.data:
                passwords = response.data[0]
                correct_password = passwords.get('user_password' if password_type == 'user' else 'admin_password')
                return password == correct_password
            else:
                # Если записей нет, создаем запись с паролями по умолчанию
                default_user_password = '1234'
                default_admin_password = 'admin'
                data = {'user_password': default_user_password, 'admin_password': default_admin_password}
                supabase.table('passwords').insert(data).execute()
                logger.info("Созданы пароли по умолчанию")
                return password == (default_user_password if password_type == 'user' else default_admin_password)
        except Exception as e:
            logger.error(f"Ошибка проверки пароля в Supabase: {e}")
            # Если не удалось проверить в Supabase, проверяем локально
            return check_password_local(password, password_type)
    else:
        # Если Supabase не инициализирован, проверяем локально
        return check_password_local(password, password_type)

def check_password_local(password, password_type='user'):
    try:
        if password_type == 'user':
            with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
                correct_password = f.read().strip()
        else:
            with open(ADMIN_PASSWORD_FILE, 'r', encoding='utf-8') as f:
                correct_password = f.read().strip()
        
        return password == correct_password
    except Exception as e:
        logger.error(f"Ошибка проверки локального пароля: {e}")
        # Если файл не существует, используем пароли по умолчанию
        default_user_password = '1234'
        default_admin_password = 'admin'
        return password == (default_user_password if password_type == 'user' else default_admin_password)

def update_password(password_type, new_password):
    if supabase:
        try:
            # Получаем текущие пароли
            response = supabase.table('passwords').select('*').execute()
            if response.data:
                record_id = response.data[0]['id']
                field_name = 'user_password' if password_type == 'user' else 'admin_password'
                
                supabase.table('passwords').update({field_name: new_password}).eq('id', record_id).execute()
                logger.info(f"Пароль {password_type} успешно изменен в Supabase")
            else:
                field_name = 'user_password' if password_type == 'user' else 'admin_password'
                data = {'user_password': '1234', 'admin_password': 'admin'}
                data[field_name] = new_password
                supabase.table('passwords').insert(data).execute()
                logger.info(f"Пароль {password_type} успешно создан в Supabase")
        except Exception as e:
            logger.error(f"Ошибка обновления пароля в Supabase: {e}")
            # Если не удалось обновить в Supabase, обновляем локально
            update_password_local(password_type, new_password)
    else:
        # Если Supabase не инициализирован, обновляем локально
        update_password_local(password_type, new_password)

def update_password_local(password_type, new_password):
    try:
        if password_type == 'user':
            with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write(new_password)
        else:
            with open(ADMIN_PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write(new_password)
        logger.info(f"Пароль {password_type} успешно обновлен локально")
    except Exception as e:
        logger.error(f"Ошибка обновления локального пароля: {e}")

# Инициализация необходимых файлов и папок
os.makedirs(DATA_DIR, exist_ok=True)
init_password_files()

# Маршруты Flask
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/check_password', methods=['POST'])
def check_password():
    try:
        entered_password = request.form.get('password')
        if check_password(entered_password, 'user'):
            session['logged_in'] = True
            return redirect('/menu')
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
    
    hoz_items = load_hoz_data()
    
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
    
    return render_template('hoz.html', products=hoz_items)

@app.route('/fish', methods=['GET', 'POST'])
def fish():
    if not session.get('logged_in'):
        return redirect('/')
    
    fish_items = load_fish_data()
    
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
    
    return render_template('fish.html', products=fish_items)

@app.route('/chicken', methods=['GET', 'POST'])
def chicken():
    if not session.get('logged_in'):
        return redirect('/')
    
    chicken_items = load_chicken_data()
    
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
                f"🍗 Курица\n"
                f"🏢 Филиал: {branch}\n"
                f"👨‍🍳 Повар: {name}\n"
                f"📅 Дата заявки: {target_date}\n"
                f"📝 Дата заполнения: {date}\n\n" +
                "\n".join(items)
            )
            safe_send_message(GROUP_ID, message)
        return redirect('/menu')
    
    return render_template('chicken.html', products=chicken_items)

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    products_data = load_products_data()
    hoz_items = load_hoz_data()
    fish_items = load_fish_data()
    chicken_items = load_chicken_data()
    return render_template('admin.html', products_data=products_data, hoz_items=hoz_items, fish_items=fish_items, chicken_items=chicken_items)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            entered_password = request.form.get('password')
            if check_password(entered_password, 'admin'):
                session['admin_logged_in'] = True
                return redirect('/admin')
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
            update_password('user', new_password)
        elif password_type == 'admin':
            update_password('admin', new_password)
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
    except Exception as e:
        logger.error(f"Ошибка удаления товара: {e}")
    
    return redirect('/admin')

@app.route('/add_hoz_item', methods=['POST'])
def add_hoz_item():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        item_name = request.form.get('item_name')
        hoz_items = load_hoz_data()
        
        if item_name and item_name not in hoz_items:
            hoz_items.append(item_name)
            save_hoz_data(hoz_items)
    except Exception as e:
        logger.error(f"Ошибка добавления хоз. товара: {e}")
    
    return redirect('/admin')

@app.route('/delete_hoz_item', methods=['POST'])
def delete_hoz_item():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        item_name = request.form.get('item_name')
        hoz_items = load_hoz_data()
        
        if item_name in hoz_items:
            hoz_items.remove(item_name)
            save_hoz_data(hoz_items)
    except Exception as e:
        logger.error(f"Ошибка удаления хоз. товара: {e}")
    
    return redirect('/admin')

@app.route('/add_fish_item', methods=['POST'])
def add_fish_item():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        item_name = request.form.get('item_name')
        fish_items = load_fish_data()
        
        if item_name and item_name not in fish_items:
            fish_items.append(item_name)
            save_fish_data(fish_items)
    except Exception as e:
        logger.error(f"Ошибка добавления рыбы: {e}")
    
    return redirect('/admin')

@app.route('/delete_fish_item', methods=['POST'])
def delete_fish_item():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        item_name = request.form.get('item_name')
        fish_items = load_fish_data()
        
        if item_name in fish_items:
            fish_items.remove(item_name)
            save_fish_data(fish_items)
    except Exception as e:
        logger.error(f"Ошибка удаления рыбы: {e}")
    
    return redirect('/admin')

@app.route('/add_chicken_item', methods=['POST'])
def add_chicken_item():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        item_name = request.form.get('item_name')
        chicken_items = load_chicken_data()
        
        if item_name and item_name not in chicken_items:
            chicken_items.append(item_name)
            save_chicken_data(chicken_items)
    except Exception as e:
        logger.error(f"Ошибка добавления курицы: {e}")
    
    return redirect('/admin')

@app.route('/delete_chicken_item', methods=['POST'])
def delete_chicken_item():
    if not session.get('admin_logged_in'):
        return redirect('/admin_login')
    
    try:
        item_name = request.form.get('item_name')
        chicken_items = load_chicken_data()
        
        if item_name in chicken_items:
            chicken_items.remove(item_name)
            save_chicken_data(chicken_items)
    except Exception as e:
        logger.error(f"Ошибка удаления курицы: {e}")
    
    return redirect('/admin')

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
