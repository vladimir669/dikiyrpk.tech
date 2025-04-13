import os
import json
import logging
from supabase import create_client, Client

# Настройка логирования
logger = logging.getLogger(__name__)

# Настройки Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://postgresql://postgres:[vovik46304]@db.wxlrektensoxrnwipsbs.supabase.co:5432/postgres")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "DATABASE_URL")

# Инициализация клиента Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase клиент успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации Supabase клиента: {e}")
    supabase = None

def init_db():
    """Инициализация базы данных"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return False

        # Проверяем, существуют ли данные
        products_response = supabase.table('products').select('*').execute()
        if not products_response.data:
            # Создаем значения по умолчанию
            products_data = create_default_products()
            # Сохраняем в Supabase
            supabase.table('products').insert({'data': products_data}).execute()
            logger.info("Созданы данные о продуктах по умолчанию")
        
        hoz_response = supabase.table('hoz').select('*').execute()
        if not hoz_response.data:
            hoz_data = create_default_hoz()
            supabase.table('hoz').insert({'data': hoz_data}).execute()
            logger.info("Созданы данные о хоз. товарах по умолчанию")
        
        fish_response = supabase.table('fish').select('*').execute()
        if not fish_response.data:
            fish_data = create_default_fish()
            supabase.table('fish').insert({'data': fish_data}).execute()
            logger.info("Созданы данные о рыбе по умолчанию")
        
        chicken_response = supabase.table('chicken').select('*').execute()
        if not chicken_response.data:
            chicken_data = create_default_chicken()
            supabase.table('chicken').insert({'data': chicken_data}).execute()
            logger.info("Созданы данные о курице по умолчанию")
        
        password_response = supabase.table('passwords').select('*').execute()
        if not password_response.data:
            passwords = {'user': '4444', 'admin': '880088'}
            supabase.table('passwords').insert({'data': passwords}).execute()
            logger.info("Созданы пароли по умолчанию")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return False

def get_password(password_type):
    """Получение пароля из Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return '4444' if password_type == 'user' else '880088'

        response = supabase.table('passwords').select('*').execute()
        if response.data:
            passwords = response.data[0]['data']
            return passwords.get(password_type, '4444' if password_type == 'user' else '880088')
    except Exception as e:
        logger.error(f"Ошибка получения пароля: {e}")
    
    return '4444' if password_type == 'user' else '880088'

def set_password(password_type, new_password):
    """Установка нового пароля в Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return False

        response = supabase.table('passwords').select('*').execute()
        if response.data:
            record_id = response.data[0]['id']
            passwords = response.data[0]['data']
            passwords[password_type] = new_password
            
            supabase.table('passwords').update({'data': passwords}).eq('id', record_id).execute()
            logger.info(f"Пароль {password_type} успешно изменен")
            return True
        else:
            passwords = {'user': '4444', 'admin': '880088'}
            passwords[password_type] = new_password
            supabase.table('passwords').insert({'data': passwords}).execute()
            logger.info(f"Пароль {password_type} успешно создан")
            return True
    except Exception as e:
        logger.error(f"Ошибка установки пароля: {e}")
        return False

def create_default_products():
    """Создание структуры данных по умолчанию"""
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
            "Соус соевый Стандарт Плюс 20кг",
            "Соус Унаги OSHI 1.8л",
            "Соус Кимчи 1.8л OSHI",
            "Картофель Фри Брусок 9*9 2.5кг*5, Lamb Weston",
            "Рис в/с Россия 25кг",
            "Уксус Рисовый OSHI 20л пр-во Космос"
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
            logger.error("Supabase клиент не инициализирован")
            return create_default_products()

        response = supabase.table('products').select('*').execute()
        if response.data:
            data = response.data[0]['data']
            logger.info("Данные о продуктах успешно загружены из Supabase")
            return data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о продуктах: {e}")
    
    logger.info("Создание структуры данных по умолчанию")
    data = create_default_products()
    save_products_data(data)
    return data

def save_products_data(data):
    """Сохранение данных о продуктах в Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return False

        response = supabase.table('products').select('*').execute()
        if response.data:
            record_id = response.data[0]['id']
            supabase.table('products').update({'data': data}).eq('id', record_id).execute()
        else:
            supabase.table('products').insert({'data': data}).execute()
        
        logger.info("Данные о продуктах успешно сохранены в Supabase")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о продуктах: {e}")
        return False

def load_hoz_data():
    """Загрузка данных о хоз. товарах из Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return create_default_hoz()

        response = supabase.table('hoz').select('*').execute()
        if response.data:
            data = response.data[0]['data']
            logger.info("Данные о хоз. товарах успешно загружены из Supabase")
            return data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о хоз. товарах: {e}")
    
    logger.info("Создание хоз. товаров по умолчанию")
    data = create_default_hoz()
    save_hoz_data(data)
    return data

def save_hoz_data(data):
    """Сохранение данных о хоз. товарах в Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return False

        response = supabase.table('hoz').select('*').execute()
        if response.data:
            record_id = response.data[0]['id']
            supabase.table('hoz').update({'data': data}).eq('id', record_id).execute()
        else:
            supabase.table('hoz').insert({'data': data}).execute()
        
        logger.info("Данные о хоз. товарах успешно сохранены в Supabase")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о хоз. товарах: {e}")
        return False

def load_fish_data():
    """Загрузка данных о рыбе из Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return create_default_fish()

        response = supabase.table('fish').select('*').execute()
        if response.data:
            data = response.data[0]['data']
            logger.info("Данные о рыбе успешно загружены из Supabase")
            return data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о рыбе: {e}")
    
    logger.info("Создание рыбы по умолчанию")
    data = create_default_fish()
    save_fish_data(data)
    return data

def save_fish_data(data):
    """Сохранение данных о рыбе в Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return False

        response = supabase.table('fish').select('*').execute()
        if response.data:
            record_id = response.data[0]['id']
            supabase.table('fish').update({'data': data}).eq('id', record_id).execute()
        else:
            supabase.table('fish').insert({'data': data}).execute()
        
        logger.info("Данные о рыбе успешно сохранены в Supabase")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о рыбе: {e}")
        return False

def load_chicken_data():
    """Загрузка данных о курице из Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return create_default_chicken()

        response = supabase.table('chicken').select('*').execute()
        if response.data:
            data = response.data[0]['data']
            logger.info("Данные о курице успешно загружены из Supabase")
            return data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных о курице: {e}")
    
    logger.info("Создание курицы по умолчанию")
    data = create_default_chicken()
    save_chicken_data(data)
    return data

def save_chicken_data(data):
    """Сохранение данных о курице в Supabase"""
    try:
        if not supabase:
            logger.error("Supabase клиент не инициализирован")
            return False

        response = supabase.table('chicken').select('*').execute()
        if response.data:
            record_id = response.data[0]['id']
            supabase.table('chicken').update({'data': data}).eq('id', record_id).execute()
        else:
            supabase.table('chicken').insert({'data': data}).execute()
        
        logger.info("Данные о курице успешно сохранены в Supabase")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных о курице: {e}")
        return False
