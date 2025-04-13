import os
import logging
import json
import psycopg2
import psycopg2.extras

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Данные для подключения к Supabase PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')

def init_db():
    """Инициализация базы данных"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Создаем таблицу для продуктов
        cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            section TEXT,
            product TEXT
        )
        ''')
        
        # Создаем таблицу для хоз. товаров
        cur.execute('''
        CREATE TABLE IF NOT EXISTS hoz (
            product TEXT
        )
        ''')
        
        # Создаем таблицу для рыбы
        cur.execute('''
        CREATE TABLE IF NOT EXISTS fish (
            product TEXT
        )
        ''')
        
        # Создаем таблицу для паролей
        cur.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            type TEXT PRIMARY KEY,
            password TEXT
        )
        ''')
        
        # Проверяем, есть ли пароли в базе
        cur.execute("SELECT COUNT(*) FROM passwords")
        count = cur.fetchone()[0]
        
        # Если паролей нет, добавляем по умолчанию
        if count == 0:
            cur.execute("INSERT INTO passwords (type, password) VALUES (%s, %s)", ('user', '4444'))
            cur.execute("INSERT INTO passwords (type, password) VALUES (%s, %s)", ('admin', '880088'))
        
        conn.commit()
        conn.close()
        logger.info("База данных успешно инициализирована")
        return True
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return False

def get_password(password_type):
    """Получение пароля из базы данных"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT password FROM passwords WHERE type = %s", (password_type,))
        result = cur.fetchone()
        
        conn.close()
        
        if result:
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Ошибка получения пароля: {e}")
        return None

def set_password(password_type, new_password):
    """Изменение пароля в базе данных"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("UPDATE passwords SET password = %s WHERE type = %s", 
                   (new_password, password_type))
        
        conn.commit()
        conn.close()
        logger.info(f"Пароль типа {password_type} успешно обновлен")
        return True
    except Exception as e:
        logger.error(f"Ошибка обновления пароля: {e}")
        return False

def load_products_data():
    """Загрузка данных о продуктах из базы данных"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Проверяем, есть ли данные в таблице
        cur.execute("SELECT COUNT(*) FROM products")
        count = cur.fetchone()[0]
        
        # Если данных нет, создаем структуру по умолчанию
        if count == 0:
            default_data = create_default_products()
            return default_data
        
        # Получаем все уникальные разделы
        cur.execute("SELECT DISTINCT section FROM products")
        sections = [row[0] for row in cur.fetchall()]
        
        data = {}
        for section in sections:
            # Получаем все продукты для раздела
            cur.execute("SELECT product FROM products WHERE section = %s", (section,))
            products = [row[0] for row in cur.fetchall()]
            data[section] = products
        
        conn.close()
        logger.info("Данные о продуктах успешно загружены из БД")
        return data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных из БД: {e}")
        # В случае ошибки возвращаем данные по умолчанию
        return create_default_products()

def save_products_data(data):
    """Сохранение данных о продуктах в базу данных"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Удаляем все существующие данные
        cur.execute("DELETE FROM products")
        
        # Добавляем новые данные
        for section, products in data.items():
            for product in products:
                cur.execute("INSERT INTO products (section, product) VALUES (%s, %s)", 
                           (section, product))
        
        conn.commit()
        conn.close()
        logger.info("Данные о продуктах успешно сохранены в БД")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения данных в БД: {e}")
        return False

def create_default_products():
    """Создание структуры данных по умолчанию и сохранение в БД"""
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

def load_hoz_data():
    """Загрузка данных о хоз. товарах из базы данных"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Проверяем, есть ли данные
        cur.execute("SELECT COUNT(*) FROM hoz")
        count = cur.fetchone()[0]
        
        if count == 0:
            default_hoz = create_default_hoz()
            return default_hoz
        
        cur.execute("SELECT product FROM hoz")
        products = [row[0] for row in cur.fetchall()]
        
        conn.close()
        logger.info("Данные о хоз. товарах успешно загружены из БД")
        return products
    except Exception as e:
        logger.error(f"Ошибка загрузки хоз. товаров из БД: {e}")
        return create_default_hoz()

def create_default_hoz():
    """Создание хоз. товаров по умолчанию и сохранение в БД"""
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
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Удаляем все существующие данные
        cur.execute("DELETE FROM hoz")
        
        # Добавляем новые данные
        for product in default_hoz:
            cur.execute("INSERT INTO hoz (product) VALUES (%s)", (product,))
        
        conn.commit()
        conn.close()
        logger.info("Данные о хоз. товарах успешно сохранены в БД")
    except Exception as e:
        logger.error(f"Ошибка сохранения хоз. товаров в БД: {e}")
    
    return default_hoz

def load_fish_data():
    """Загрузка данных о рыбе из базы данных"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Проверяем, есть ли данные
        cur.execute("SELECT COUNT(*) FROM fish")
        count = cur.fetchone()[0]
        
        if count == 0:
            default_fish = create_default_fish()
            return default_fish
        
        cur.execute("SELECT product FROM fish")
        products = [row[0] for row in cur.fetchall()]
        
        conn.close()
        logger.info("Данные о рыбе успешно загружены из БД")
        return products
    except Exception as e:
        logger.error(f"Ошибка загрузки рыбы из БД: {e}")
        return create_default_fish()

def create_default_fish():
    """Создание рыбы по умолчанию и сохранение в БД"""
    default_fish = ["Филе форели охл.", "Лосось атлантический охл.", "Тунец филе охл."]
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Удаляем все существующие данные
        cur.execute("DELETE FROM fish")
        
        # Добавляем новые данные
        for product in default_fish:
            cur.execute("INSERT INTO fish (product) VALUES (%s)", (product,))
        
        conn.commit()
        conn.close()
        logger.info("Данные о рыбе успешно сохранены в БД")
    except Exception as e:
        logger.error(f"Ошибка сохранения рыбы в БД: {e}")
    
    return default_fish
