import os
import json
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
HOZ_FILE = os.path.join(DATA_DIR, 'hoz.json')
FISH_FILE = os.path.join(DATA_DIR, 'fish.json')

def save_products_data(data):
    try:
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные о продуктах успешно сохранены в {PRODUCTS_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения products.json: {e}")
        return False

def save_hoz_data(data):
    try:
        with open(HOZ_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные о хоз. товарах успешно сохранены в {HOZ_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения hoz.json: {e}")
        return False

def save_fish_data(data):
    try:
        with open(FISH_FILE, 'w', encoding='utf-8') as f:
            json.dump({"Рыба": data}, f, ensure_ascii=False, indent=4)
        logger.info(f"Данные о рыбе успешно сохранены в {FISH_FILE}")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения fish.json: {e}")
        return False
