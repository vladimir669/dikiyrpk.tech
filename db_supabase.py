import os
import logging
from supabase import create_client, Client

# Логирование
logger = logging.getLogger(__name__)

# Настройки Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wxlrektensoxrnwipsbs.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

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

        # Продукты
        if not supabase.table('products').select('*').execute().data:
            supabase.table('products').insert({'data': create_default_products()}).execute()
            logger.info("Созданы продукты по умолчанию")

        # Хозтовары
        if not supabase.table('hoz').select('*').execute().data:
            supabase.table('hoz').insert({'data': create_default_hoz()}).execute()
            logger.info("Созданы хозтовары по умолчанию")

        # Рыба
        if not supabase.table('fish').select('*').execute().data:
            supabase.table('fish').insert({'data': create_default_fish()}).execute()
            logger.info("Созданы данные о рыбе по умолчанию")

        # Курица
        if not supabase.table('chicken').select('*').execute().data:
            supabase.table('chicken').insert({'data': create_default_chicken()}).execute()
            logger.info("Созданы данные о курице по умолчанию")

        # Пароли
        if not supabase.table('passwords').select('*').execute().data:
            supabase.table('passwords').insert({'data': {'user': '4444', 'admin': '880088'}}).execute()
            logger.info("Созданы пароли по умолчанию")

        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return False

def get_password(password_type):
    """Получить пароль (user/admin)"""
    try:
        if not supabase:
            return '4444' if password_type == 'user' else '880088'

        response = supabase.table('passwords').select('*').execute()
        if response.data:
            return response.data[0]['data'].get(password_type, '4444' if password_type == 'user' else '880088')
    except Exception as e:
        logger.error(f"Ошибка получения пароля: {e}")

    return '4444' if password_type == 'user' else '880088'

def set_password(password_type, new_password):
    """Установить пароль"""
    try:
        if not supabase:
            return False

        response = supabase.table('passwords').select('*').execute()
        if response.data:
            record_id = response.data[0]['id']
            passwords = response.data[0]['data']
            passwords[password_type] = new_password
            supabase.table('passwords').update({'data': passwords}).eq('id', record_id).execute()
            return True
        else:
            supabase.table('passwords').insert({'data': {password_type: new_password}}).execute()
            return True
    except Exception as e:
        logger.error(f"Ошибка установки пароля: {e}")
        return False

# === ТВОИ СПИСКИ ===

def create_default_products():
    return {
        "Свит Лайф": [
            "Сыр полутвердый Моцарелла Пицца 40% Bonfesio Cooking 2.6кг",
            "Сыр Пармезан 9 Месяцев ЮКМП Цилиндр 45% 6-6.5кг",
            "Сыр 'Hochland' плавленный ломтевой Бистро Чеддер 1.107кг (90 ломтиков)",
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
            "Имбирь Маринованный белый Premium Fujin Китай 1.4кг",
            "Масло Подсолнечное Smart Chef для фритюра 5л",
            "Порошок Васаби Tamaki 2кг",
            "Сахарный песок сумка Россия 5кг",
            "Мука пшеничная Царица Кубанская Высший Сорт 5кг",
        ],
        "Рафт": [
            "Масаго красная Санта-бремор",
            "Масаго черная Санта-бремор",
            "Масаго оранжевая Санта-бремор",
            "Водоросли Нори 100 листов, 240 г/уп, 72шт/кор, 17,28 кг/кор, Россия",
            "Соус Чили-манго 'Food Service', 1кг, 6 шт/кор, 10415806, Гурмикс, Россия",
            "Картофельные дольки в кожуре со специями, уп. 0,9кг, замороженный, 9кг/кор, Tayyebat, Ливан",
            "Кунжутное семя обжаренное белое 1 кг, 15 шт/кор, СКМ, Россия",
            "Лук жареный 1 кг, 10 шт/кор, Нидерланды",
            "Тунец филе Tellowfin, сім, 500-800гр, Saku (сяку), Аками, ААА, кор. -10хг., Babdian Food (Fujian) Co, Ltd, 3500/02248, Китай",
            "Луковые кольца в панировке (формованые) зам.уп 0,908 кг, 8шт/кор., 7,264 кг/кор, Baby Star, Китай",
            "Нагетсы серволюкс",
        ],
        "Оши": [
            "Угорь жаренный Унаги ТЕХ (в уп 10%)",
            "Соус соевый Стандарт Плюс 20кг",
            "Соус Унаги OSHI 1.8л",
            "Соус Кимчи 1.8л OSHI",
            "Картофель Фри Брусок 9*9 2.5кг*5, Lamb Weston",
            "Рис в/с Россия 25кг",
            "Уксус Рисовый OSHI 20л пр-во Космос",
        ]
    }

def create_default_hoz():
    return [
        "перчатки нитриловые M",
        "перчатки нитриловые L",
        "пакеты фасовочные 24x37",
        "пакеты мусорные 60л",
        "фольга 30см 100м",
        "пленка пищевая 30см 200м",
        "Контейнер 1000мл ЧЕРНЫЙ 150*200*55 (50/300) ONECLICK BOTTON 1000/bBLACK",
        "Контейнер 500мл ЧЕРНЫЙ 120*160*45 (50/400) ONECLICK BOTTON 500/bBLACK",
        "Контейнер 800мл ЧЕРНЫЙ 120*200*55 (50/300) ONECLICK BOTTON 800/bBLACK",
        "Крышка 20мм к контейнеру 500мл (50/400) ONECLICK LID 500/20",
        "Крышка 20мм к контейнеру 800мл (50/300) ONECLICK LID 800/20",
        "Крышка плоская к контейнеру 1000мл (50/300) ONECLICK LID 1000/0",
        "Мешок д/мусора ПВД 240л 50мкм 10 шт/рол (1/10 рол), Сфера",
        "Пакет КРАФТ без ручки 320*200*340 80гр (1/20/300), ЭЛВИ Групп",
        "Пакет КРАФТ с крученной ручкой 240*140*280 (1/300), Монолит",
        "Пакет КРАФТ с плоской ручкой 280*150*320 (1/250), Монолит",
        "Палочки для суши в индив. полиэт. упаковке 20 см круглые+зубочистка 100шт/уп (1/20уп) ГТД, Лигапроф",
        "Перчатки винил. неопудр. черные L SAF&TY 100шт/уп (1/10уп) (ндс 10%) ГТД, Сейфити",
        "Перчатки винил. неопудр. черные М SAF&TY 100шт/уп (1/10уп) (ндс 10%) ГТД, Сейфити",
        "Пищевая пленка 450*200 (5,5мк) белая 'ДЕСНОГОР' 1/10, ASD",
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
        "Соусник 30 мл (1234 П) с верхним закрытием прозрачный (1/80/1920) ВЗЛП",
        "Соусник 50 мл (1244 П) с верхним закрытием прозрачный (1/80/1200) ВЗЛП",
        "Соусник 80 мл (1254 П) с верхним закрытием прозрачный (1/80/960) ВЗЛП",
        "Стеки д/шашлыка 20см 100шт/уп(1/100уп) ГТД, Лигапроф",
        "Термолента 57*30 D ЭКО (1/8/216), ФОРМУЛА Т",
        "Термолента 80*80 Е1 ЭКО (59м) (1/6/72)",
        "Упаковка OSQ 600мл Meal Box S 118х118х65мм (1/450), OSQ",
    ]

def create_default_fish():
    return [
        "филе форели",
        "Тунец филе Tellowfin, сім, 500-800гр, Saku (сяку), Аками, ААА, кор. -10хг., Babdian Food (Fujian) Co, Ltd"
    ]

def create_default_chicken():
    return [
        "филе куриное копч."
    ]
