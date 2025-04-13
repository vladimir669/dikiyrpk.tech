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
    save_products_data(default_data)
    return default_data

def create_default_hoz():
    """Создание хоз. товаров по умолчанию"""
    default_hoz = [
        "Мешки для мусора",
        "Салфетки",
        "Перчатки",
        "Моющее средство",
        "Губки",
        "GraSS Средство моющее CLEO 5,2кг (арт. 125415)",
        "Пакет КРАФТ без ручки 320200340 80гр (1/20/300)",
        "Пакет КРАФТ без ручки 260Х150Х340 70гр (1/450)",
        "Пакет КРАФТ с крученной ручкой 240140280 (1/300)",
        "Пакет КРАФТ с крученной ручкой 320200370 (1/200)",
        "Пакет КРАФТ с плоской ручкой 280150320 (1/250)",
        "Контейнер 500мл ЧЕРНЫЙ 12016045 (50/400) — ONECLICK BOTTON 500/bBLACK",
        "Крышка 20мм к контейнеру 500мл (50/400) — ONECLICK LID 500/20",
        "Салатник ECO OpSalad 220х160х55 дно чёрное 1000мл + крышка (1/300)",
        "Контейнер 1000мл ЧЕРНЫЙ 15020055 (50/300) — ONECLICK BOTTON 1000/bBLACK"
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
