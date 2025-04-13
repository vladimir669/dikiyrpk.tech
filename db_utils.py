import os
import json
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Определение путей для данных
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')  # Храним данные в подкаталоге приложения
PASSWORD_FILE = os.path.join(DATA_DIR, 'password.txt')
ADMIN_PASSWORD_FILE = os.path.join(DATA_DIR, 'admin_password.txt')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
HOZ_FILE = os.path.join(DATA_DIR, 'hoz.json')
FISH_FILE = os.path.join(DATA_DIR, 'fish.json')

def init_db():
    """Инициализация базы данных (файловой структуры)"""
    try:
        # Создаем директорию для данных, если она не существует
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logger.info(f"Директория {DATA_DIR} успешно создана")
        
        # Инициализация файлов с паролями
        if not os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write('4444')
            logger.info(f"Создан файл с паролем пользователя: {PASSWORD_FILE}")

        if not os.path.exists(ADMIN_PASSWORD_FILE):
            with open(ADMIN_PASSWORD_FILE, 'w', encoding='utf-8') as f:
                f.write('880088')
            logger.info(f"Создан файл с паролем администратора: {ADMIN_PASSWORD_FILE}")
        
        # Инициализация файлов с данными
        if not os.path.exists(PRODUCTS_FILE):
            create_default_products()
        
        if not os.path.exists(HOZ_FILE):
            create_default_hoz()
        else:
            # Обновляем хоз. товары даже если файл существует
            create_default_hoz()
            logger.info(f"Обновлены данные о хоз. товарах в {HOZ_FILE}")
        
        if not os.path.exists(FISH_FILE):
            create_default_fish()
            
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return False

def get_password(password_type):
    """Получение пароля из файла"""
    try:
        file_path = ADMIN_PASSWORD_FILE if password_type == 'admin' else PASSWORD_FILE
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            logger.warning(f"Файл с паролем не найден: {file_path}")
            # Пробуем пересоздать файл с паролем
            init_db()
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
    except Exception as e:
        logger.error(f"Ошибка получения пароля: {e}")
    return None

def set_password(password_type, new_password):
    """Установка нового пароля"""
    try:
        file_path = ADMIN_PASSWORD_FILE if password_type == 'admin' else PASSWORD_FILE
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_password)
        logger.info(f"Пароль {password_type} успешно изменен")
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
            "Порошок Васаби Tamaki 2кг",
            "Имбирь белый маринованный Premium Fujin Китай 1.4кг",
            "Сыр Кремчиз Cooking 11кг"
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
            "Нагетсы серволюкс",
            "Луковые кольца в панировке (формованые) зам.уп 0,908 кг, 8шт/кор., 7,264 кг/кор, Baby Star, Китай"
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
        ],
        "Рыба": [
            "Филе форели охл.",
            "Лосось атлантический охл.",
            "Тунец филе охл."
        ]
    }
    
    # Проверяем, существует ли файл с данными
    if os.path.exists(PRODUCTS_FILE):
        try:
            # Если файл существует, загружаем данные из него
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                logger.info(f"Загружены существующие данные из {PRODUCTS_FILE}")
                
                # Используем существующие данные вместо значений по умолчанию
                default_data = existing_data
        except Exception as e:
            logger.error(f"Ошибка загрузки существующих данных: {e}")
    
    save_products_data(default_data)
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
    try:
        with open(HOZ_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_hoz, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные о хоз. товарах успешно сохранены в {HOZ_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения hoz.json: {e}")
    return default_hoz

def create_default_fish():
    """Создание рыбы по умолчанию"""
    default_fish = ["Филе форели охл.", "Лосось атлантический охл.", "Тунец филе охл."]
    
    # Проверяем, существует ли файл с данными
    if os.path.exists(FISH_FILE):
        try:
            # Если файл существует, загружаем данные из него
            with open(FISH_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Загружены существующие данные из {FISH_FILE}")
                
                # Извлекаем список рыбы из существующих данных
                if isinstance(data, dict) and "Рыба" in data:
                    default_fish = data["Рыба"]
                elif isinstance(data, list):
                    default_fish = data
                else:
                    default_fish = list(data.values())[0] if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f"Ошибка загрузки существующих данных о рыбе: {e}")
    
    try:
        with open(FISH_FILE, 'w', encoding='utf-8') as f:
            json.dump({"Рыба": default_fish}, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные о рыбе успешно сохранены в {FISH_FILE}")
    except Exception as e:
        logger.error(f"Ошибка сохранения fish.json: {e}")
    return default_fish

def load_products_data():
    """Загрузка данных о продуктах"""
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Данные о продуктах успешно загружены из {PRODUCTS_FILE}")
                return data
    except Exception as e:
        logger.error(f"Ошибка загрузки products.json: {e}")
    
    logger.info("Создание структуры данных по умолчанию")
    return create_default_products()

def save_products_data(data):
    """Сохранение данных о продуктах"""
    try:
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные о продуктах успешно сохранены в {PRODUCTS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения products.json: {e}")
        return False

def load_hoz_data():
    """Загрузка данных о хоз. товарах"""
    try:
        if os.path.exists(HOZ_FILE):
            with open(HOZ_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Данные о хоз. товарах успешно загружены из {HOZ_FILE}")
                return data
    except Exception as e:
        logger.error(f"Ошибка загрузки hoz.json: {e}")
    
    logger.info("Создание хоз. товаров по умолчанию")
    return create_default_hoz()

def load_fish_data():
    """Загрузка данных о рыбе"""
    try:
        if os.path.exists(FISH_FILE):
            with open(FISH_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Данные о рыбе успешно загружены из {FISH_FILE}")
                if isinstance(data, dict) and "Рыба" in data:
                    return data["Рыба"]
                return list(data.values())[0] if isinstance(data, dict) else data
    except Exception as e:
        logger.error(f"Ошибка загрузки fish.json: {e}")
    
    logger.info("Создание рыбы по умолчанию")
    return create_default_fish()
