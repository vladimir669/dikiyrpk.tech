from supabase import create_client
import os
import logging

logger = logging.getLogger('app')

# Получаем URL и ключ Supabase из переменных окружения или используем значения по умолчанию
url = os.environ.get("SUPABASE_URL", "https://wxlrektensoxrnwipsbs.supabase.co")
key = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")  # укорочен для читаемости

try:
    supabase = create_client(url, key)
    logger.info("Supabase клиент успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка при инициализации Supabase: {e}")
    raise

# Получение всех поставщиков
def get_suppliers():
    try:
        response = supabase.table("suppliers").select("*").order("name").execute()
        return response.data
    except Exception as e:
        logger.error(f"Ошибка получения поставщиков: {e}")
        return []

# Получение всех продуктов поставщика
def get_products_by_supplier(supplier_id):
    try:
        response = supabase.table("products").select("*").eq("supplier_id", supplier_id).order("name").execute()
        return response.data
    except Exception as e:
        logger.error(f"Ошибка получения продуктов для поставщика {supplier_id}: {e}")
        return []

# Получение всех продуктов с названием поставщика
def get_all_products():
    try:
        response = supabase.table("products").select("*, suppliers(name)").order("name").execute()
        return response.data
    except Exception as e:
        logger.error(f"Ошибка получения всех продуктов: {e}")
        return []

# Получение одной заявки с товарами
def get_request_with_items(request_id):
    try:
        request = supabase.table("requests").select("*, suppliers(name), branches(name)").eq("id", request_id).single().execute()
        items = supabase.table("request_items").select("*, products(*)").eq("request_id", request_id).execute()
        return {
            "request": request.data,
            "items": items.data
        }
    except Exception as e:
        logger.error(f"Ошибка получения заявки {request_id}: {e}")
        return {
            "request": None,
            "items": []
        }
