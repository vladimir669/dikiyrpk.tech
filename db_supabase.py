import os
import json
import logging
from supabase import create_client, Client

# Настройка логирования
logger = logging.getLogger(__name__)

# Настройки Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

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

def init_db():
    """Инициализация базы данных"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, используем локальное хранилище")
            return False
        
        # Проверяем существование таблиц
        logger.info("Проверка базы данных")
        
        # Создаем таблицы, если они не существуют
        try:
            # Проверяем таблицу products
            supabase.table('products').select('*').limit(1).execute()
        except Exception as e:
            logger.warning(f"Таблица products не существует: {e}")
            # Создаем таблицу products
            try:
                supabase.rpc('create_products_table').execute()
                logger.info("Таблица products успешно создана")
            except Exception as e:
                logger.error(f"Ошибка создания таблицы products: {e}")
        
        try:
            # Проверяем таблицу hoz
            supabase.table('hoz').select('*').limit(1).execute()
        except Exception as e:
            logger.warning(f"Таблица hoz не существует: {e}")
            # Создаем таблицу hoz
            try:
                supabase.rpc('create_hoz_table').execute()
                logger.info("Таблица hoz успешно создана")
            except Exception as e:
                logger.error(f"Ошибка создания таблицы hoz: {e}")
        
        try:
            # Проверяем таблицу fish
            supabase.table('fish').select('*').limit(1).execute()
        except Exception as e:
            logger.warning(f"Таблица fish не существует: {e}")
            # Создаем таблицу fish
            try:
                supabase.rpc('create_fish_table').execute()
                logger.info("Таблица fish успешно создана")
            except Exception as e:
                logger.error(f"Ошибка создания таблицы fish: {e}")
        
        try:
            # Проверяем таблицу chicken
            supabase.table('chicken').select('*').limit(1).execute()
        except Exception as e:
            logger.warning(f"Таблица chicken не существует: {e}")
            # Создаем таблицу chicken
            try:
                supabase.rpc('create_chicken_table').execute()
                logger.info("Таблица chicken успешно создана")
            except Exception as e:
                logger.error(f"Ошибка создания таблицы chicken: {e}")
        
        try:
            # Проверяем таблицу passwords
            supabase.table('passwords').select('*').limit(1).execute()
        except Exception as e:
            logger.warning(f"Таблица passwords не существует: {e}")
            # Создаем таблицу passwords
            try:
                supabase.rpc('create_passwords_table').execute()
                logger.info("Таблица passwords успешно создана")
            except Exception as e:
                logger.error(f"Ошибка создания таблицы passwords: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return False

def get_password(password_type):
    """Получение пароля из Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, используем пароли по умолчанию")
            return '4444' if password_type == 'user' else '880088'

        response = supabase.table('passwords').select('*').execute()
        if response.data:
            passwords = response.data[0]
            return passwords.get('user_password' if password_type == 'user' else 'admin_password', 
                               '4444' if password_type == 'user' else '880088')
        else:
            # Если записей нет, создаем запись с паролями по умолчанию
            data = {'user_password': '4444', 'admin_password': '880088'}
            supabase.table('passwords').insert(data).execute()
            logger.info("Созданы пароли по умолчанию")
            return '4444' if password_type == 'user' else '880088'
    except Exception as e:
        logger.error(f"Ошибка получения пароля: {e}")
    
    return '4444' if password_type == 'user' else '880088'

def set_password(password_type, new_password):
    """Установка нового пароля в Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, пароль не сохранен")
            return False

        response = supabase.table('passwords').select('*').execute()
        if response.data:
            record_id = response.data[0]['id']
            field_name = 'user_password' if password_type == 'user' else 'admin_password'
            
            supabase.table('passwords').update({field_name: new_password}).eq('id', record_id).execute()
            logger.info(f"Пароль {password_type} успешно изменен")
            return True
        else:
            field_name = 'user_password' if password_type == 'user' else 'admin_password'
            data = {'user_password': '4444', 'admin_password': '880088'}
            data[field_name] = new_password
            supabase.table('passwords').insert(data).execute()
            logger.info(f"Пароль {password_type} успешно создан")
            return True
    except Exception as e:
        logger.error(f"Ошибка установки пароля: {e}")
        return False

def create_default_products():
    """Создание структуры данных по умолчанию"""
    default_data = {
        "Оши": [
            "Угорь жаренный Унаги ТЕХ (в уп 10%)",
            "Соус соевый Стандарт Плюс 20кг",
            "Соус Унаги OSHI 1.8л",
            "Соус Кимчи 1.8л OSHI",
            "Картофель Фри Брусок 9*9 2.5кг*5, Lamb Weston",
            "Рис в/с Россия 25кг",
            "Уксус Рисовый OSHI 20л пр-во Космос"
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
        "Свит Лайф": [
            "Сыр полутвердый Моцарелла Пицца 40% Bonfesio Cooking 2.6кг",
            "Сыр Пармезан 9 Месяцев ЮКМП Цилиндр 45% 6-6.5кг",
            "Сыр \"Hochland\" плавленный ломтевой Бистро Чеддер 1.107кг (90 ломтиков)",
            "Крабовое мясо Снежный краб охл. (имитация из сурими) VICI 500гр",
            "Креветки б/г в панцире с/м Empacadora Bibo SA Эквадор 16/20 1кг",
            "Майонез классический SoPro 67% 9.6кг",
            "Соус Ореховый (кунжутный) Smart Chef 1л",
            "Соус Шрирача 0.815кг Uni-Eagle",
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
        ]
    }
    return default_data

def create_default_hoz():
    """Создание хоз. товаров по умолчанию"""
    default_hoz = [
        "CL 850 Крышка карт.лам. CL 850 мл. 212*108 (1/100/1200), CLARITY",
        "CL 850 Форма алюминиевая 850 мл, L-край, 218*112/181*76 h 62 мм, (1/100/600), CLARITY",
        "FOREST clean Концентрат для мытья пола \"Лайм и мята\" нейтральный запах 5 л н, Forest",
        "GraSS Средство для мытья посуды Velly light (зеленое яблоко) 5кг (арт.125469) н, GraSS",
        "GraSS Средство чистящее дезинфиц. гель густой DOS GEL 5,3л (арт.125240), GraSS",
        "Гель \"Белизна\" ЧИСТОЛЮБ 3 в1 750 мл Домбытхим (1/16), ДомБытХим",
        "Контейнер 1000мл ЧЕРНЫЙ 150*200*55 (50/300) ONECLICK BOTTON 1000/bBLACK, 1ЕА",
        "Контейнер 500мл ЧЕРНЫЙ 120*160*45 (50/400) ONECLICK BOTTON 500/bBLACK, 1ЕА",
        "Контейнер 800мл ЧЕРНЫЙ 120*200*55 (50/300) ONECLICK BOTTON 800/bBLACK, 1ЕА",
        "Крышка 20мм к контейнеру 500мл (50/400) ONECLICK LID 500/20, 1ЕА",
        "Крышка 20мм к контейнеру 800мл (50/300) ONECLICK LID 800/20, 1ЕА",
        "Крышка плоская к контейнеру 1000мл (50/300) ONECLICK LID 1000/0, 1ЕА",
        "Мешок д/мусора ПВД 240л 50мкм 10 шт/рол (1/10 рол), Сфера",
        "Пакет КРАФТ без ручки 320*200*340 80гр (1/20/300), ЭЛВИ Групп",
        "Пакет КРАФТ с крученной ручкой 240*140*280 (1/300)н, Монолит",
        "Пакет КРАФТ с плоской ручкой 280*150*320 (1/250), Монолит",
        "Палочки для суши в индив. полиэт. упаковке 20 см круглые+зубочистка 100шт/уп (1/20уп) ГТД н, Лигапроф",
        "Перчатки винил. неопудр. черные L SAF&TY 100шт/уп (1/10уп) (ндс 10%) ГТД, Сейфити",
        "Перчатки винил. неопудр. черные М SAF&TY 100шт/уп (1/10уп) (ндс 10%) ГТД, Сейфити",
        "Пищевая пленка 450*200 (5,5мк) белая \"ДЕСНОГОР\" 1/10, ASD",
        "Полотенца рулонные с центральной вытяжкой (15гр) 130 м (1/6), ПапирЮг",
        "Полотно вафельное отб. ш-40 125 гр (1/50м.) 1/6, Галтекс",
        "Салфетка Plushe Maxi Professional БЕЛАЯ 500 л (1/4уп), ПапирЮг",
        "Тряпка д/пола светлая 75*100 см (1/20), Борд",
        "Фольга 440*6м 9 мкм (1/24) Стандартная, Лига-пак",
        "Мешок д/мусора 30л 15мкм 30шт/рол ОГО (1/20рол), АРСПАК",
        "Освежитель воздуха First Fresh в ассорт. 300мл. 1/12",
        "Пакет КРАФТ без ручки 260Х150Х340 70гр (1/450), Монолит",
        "Пакет КРАФТ с крученной ручкой 320*200*370 (1/200), Монолит",
        "Пакет КРАФТ с плоской ручкой 280*150*320 (1/250), Монолит",
        "Соусник 30 мл (1234 П) с верхним закрытием прозрачный (1/80/1920) ВЗЛП н, ВЗЛП",
        "Соусник 50 мл (1244 П) с верхним закрытием прозрачный (1/80/1200) ВЗЛП, ВЗЛП",
        "Соусник 80 мл (1254 П) с верхним закрытием прозрачный (1/80/960) ВЗЛП н, ВЗЛП",
        "Стеки д/шашлыка 20см 100шт/уп(1/100уп) ГТД, Лигапроф",
        "Термолента 57*30 D ЭКО (1/8/216), ФОРМУЛА Т",
        "Термолента 80*80 Е1 ЭКО (59м) (1/6/72)",
        "Упаковка OSQ 600мл Meal Box S 118х118х65мм (1/450), OSQ"
    ]
    return default_hoz

def create_default_fish():
    """Создание рыбы по умолчанию"""
    default_fish = ["Филе форели охл."]
    return default_fish

def create_default_chicken():
    """Создание курицы по умолчанию"""
    default_chicken = ["Филе куриное копч."]
    return default_chicken

def load_products_data():
    """Загрузка данных о продуктах из Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, используем данные по умолчанию")
            return create_default_products()

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
            for supplier, items in default_data.items():
                for name in items:
                    try:
                        supabase.table('products').insert({
                            'name': name,
                            'supplier': supplier
                        }).execute()
                    except Exception as e:
                        logger.error(f"Ошибка сохранения продукта {name}: {e}")
            
            return default_data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о продуктах: {e}")
        return create_default_products()

def save_products_data(data):
    """Сохранение данных о продуктах в Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, данные не сохранены")
            return False

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
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о продуктах: {e}")
        return False

def load_hoz_data():
    """Загрузка данных о хоз. товарах из Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, используем данные по умолчанию")
            return create_default_hoz()

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
            for name in default_data:
                try:
                    supabase.table('hoz').insert({
                        'name': name,
                        'supplier': 'Хоз. товары'
                    }).execute()
                except Exception as e:
                    logger.error(f"Ошибка сохранения хоз. товара {name}: {e}")
            
            return default_data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о хоз. товарах: {e}")
        return create_default_hoz()

def save_hoz_data(data):
    """Сохранение данных о хоз. товарах в Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, данные не сохранены")
            return False

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
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о хоз. товарах: {e}")
        return False

def load_fish_data():
    """Загрузка данных о рыбе из Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, используем данные по умолчанию")
            return create_default_fish()

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
            for name in default_data:
                try:
                    supabase.table('fish').insert({
                        'name': name,
                        'supplier': 'Рыба'
                    }).execute()
                except Exception as e:
                    logger.error(f"Ошибка сохранения рыбы {name}: {e}")
            
            return default_data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о рыбе: {e}")
        return create_default_fish()

def save_fish_data(data):
    """Сохранение данных о рыбе в Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, данные не сохранены")
            return False

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
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о рыбе: {e}")
        return False

def load_chicken_data():
    """Загрузка данных о курице из Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, используем данные по умолчанию")
            return create_default_chicken()

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
            for name in default_data:
                try:
                    supabase.table('chicken').insert({
                        'name': name,
                        'supplier': 'Курица'
                    }).execute()
                except Exception as e:
                    logger.error(f"Ошибка сохранения курицы {name}: {e}")
            
            return default_data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о курице: {e}")
        return create_default_chicken()

def save_chicken_data(data):
    """Сохранение данных о курице в Supabase"""
    try:
        if not supabase:
            logger.warning("Supabase клиент не инициализирован, данные не сохранены")
            return False

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
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о курице: {e}")
        return False
