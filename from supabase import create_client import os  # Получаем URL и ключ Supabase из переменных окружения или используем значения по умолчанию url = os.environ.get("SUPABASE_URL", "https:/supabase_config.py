from supabase import create_client
import os

# Получаем URL и ключ Supabase из переменных окружения или используем значения по умолчанию
url = os.environ.get("SUPABASE_URL", "https://wxlrektensoxrnwipsbs.supabase.co")
key = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4bHJla3RlbnNveHJud2lwc2JzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDU1NDk3NCwiZXhwIjoyMDYwMTMwOTc0fQ.45X6uk_ZfNvwLjmBOum2s3JZnm6KehUvImzzec0iWMc")

supabase = create_client(url, key)

def get_suppliers():
    """Получить всех поставщиков"""
    response = supabase.table("suppliers").select("*").order("name").execute()
    return response.data

def get_products_by_supplier(supplier_id):
    """Получить все продукты по поставщику"""
    response = supabase.table("products").select("*").eq("supplier_id", supplier_id).order("name").execute()
    return response.data

def get_all_products():
    """Получить все продукты"""
    response = supabase.table("products").select("*, suppliers(name)").order("name").execute()
    return response.data

def get_request_with_items(request_id):
    """Получить заявку с товарами"""
    request = supabase.table("requests").select("*, suppliers(name), branches(name)").eq("id", request_id).single().execute()
    items = supabase.table("request_items").select("*, products(*)").eq("request_id", request_id).execute()
    
    return {
        "request": request.data,
        "items": items.data
    }
