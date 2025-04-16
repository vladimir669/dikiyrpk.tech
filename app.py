from flask import Flask, render_template, request, redirect, session, url_for
from supabase import supabase, get_products_by_category, get_categories
from config import ADMIN_PASSWORD
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return redirect(url_for('form'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        return render_template('login.html', error='Неверный пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/form', methods=['GET', 'POST'])
def form():
    categories = get_categories()
    products = {cat['name']: get_products_by_category(cat['id']) for cat in categories}
    return render_template('form.html', categories=categories, products=products)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    categories = get_categories()
    products = {cat['name']: get_products_by_category(cat['id']) for cat in categories}
    return render_template('admin.html', categories=categories, products=products)

@app.route('/admin/add_category', methods=['POST'])
def add_category():
    if not session.get('admin'):
        return redirect(url_for('login'))
    name = request.form.get('name')
    supabase.table("categories").insert({"name": name}).execute()
    return redirect(url_for('admin'))

@app.route('/admin/delete_category/<int:cat_id>', methods=['POST'])
def delete_category(cat_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    supabase.table("categories").delete().eq("id", cat_id).execute()
    return redirect(url_for('admin'))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if not session.get('admin'):
        return redirect(url_for('login'))
    name = request.form.get('name')
    cat_id = request.form.get('category_id')
    supabase.table("products").insert({"name": name, "category_id": cat_id}).execute()
    return redirect(url_for('admin'))

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    supabase.table("products").delete().eq("id", product_id).execute()
    return redirect(url_for('admin'))
