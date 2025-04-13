import os
import json
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
HOZ_FILE = os.path.join(DATA_DIR, 'hoz.json')
FISH_FILE = os.path.join(DATA_DIR, 'fish.json')
CHICKEN_FILE = os.path.join(DATA_DIR, 'chicken.json')

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(PRODUCTS_FILE):
        save_products_data(create_default_products())
    if not os.path.exists(HOZ_FILE):
        save_hoz_data(create_default_hoz())
    if not os.path.exists(FISH_FILE):
        save_fish_data(create_default_fish())
    if not os.path.exists(CHICKEN_FILE):
        save_chicken_data(create_default_chicken())

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
        "Пищевая пленка 450*200  (5,5мк) белая \"ДЕСНОГОР\" 1/10, ASD",
        "Термолента  57*30 D ЭКО (1/8/216), ФОРМУЛА Т",
        "Упаковка OSQ 600мл Meal Box S 118х118х65мм (1/450), OSQ"
    ]

def create_default_fish():
    return ["Филе форели охл."]

def create_default_chicken():
    return ["Филе куриное копч."]

# Функции для загрузки и сохранения данных
def save_products_data(data): _save(PRODUCTS_FILE, data)
def load_products_data(): return _load(PRODUCTS_FILE)
def save_hoz_data(data): _save(HOZ_FILE, data)
def load_hoz_data(): return _load(HOZ_FILE)
def save_fish_data(data): _save(FISH_FILE, data)
def load_fish_data(): return _load(FISH_FILE)
def save_chicken_data(data): _save(CHICKEN_FILE, data)
def load_chicken_data(): return _load(CHICKEN_FILE)

def _save(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"Данные успешно сохранены в {filepath}")

def _load(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
