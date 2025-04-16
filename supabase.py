from supabase import create_client

url = "https://wxlrektensoxrnwipsbs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4bHJla3RlbnNveHJud2lwc2JzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDU1NDk3NCwiZXhwIjoyMDYwMTMwOTc0fQ.45X6uk_ZfNvwLjmBOum2s3JZnm6KehUvImzzec0iWMc"

supabase = create_client(url, key)

def get_categories():
    return supabase.table("categories").select("*").execute().data

def get_products_by_category(cat_id):
    return supabase.table("products").select("*").eq("category_id", cat_id).execute().data
