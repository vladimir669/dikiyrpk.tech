# В начале app.py добавьте:
import os
import shutil

# Создаем директорию для шаблонов, если она не существует
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir, exist_ok=True)

# Функция для создания шаблона, если он не существует
def create_template_if_not_exists(template_name, content):
    template_path = os.path.join(templates_dir, template_name)
    if not os.path.exists(template_path):
        with open(template_path, 'w') as f:
            f.write(content)

# Создаем все необходимые шаблоны
# Здесь нужно добавить вызовы функции create_template_if_not_exists для каждого шаблона
# Например:
create_template_if_not_exists('base.html', """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Система заказов{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <script>
        // Предотвращаем масштабирование на мобильных устройствах
        document.addEventListener('touchstart', function(event) {
            if (event.touches.length > 1) {
                event.preventDefault();
            }
        }, { passive: false });
        
        var lastTouchEnd = 0;
        document.addEventListener('touchend', function(event) {
            var now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    </script>
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        <div class="container">
            <h1>{% block header %}Система заказов{% endblock %}</h1>
        </div>
    </header>
    
    <nav>
        <div class="container">
            <a href="{{ url_for('index') }}">Главная</a>
            {% if session.get('logged_in') %}
                <a href="{{ url_for('menu') }}">Меню</a>
                <a href="{{ url_for('hoz') }}">Хоз. товары</a>
                <a href="{{ url_for('fish') }}">Рыба</a>
                <a href="{{ url_for('chicken') }}">Курица</a>
                <a href="{{ url_for('logout') }}">Выход</a>
            {% elif session.get('admin_logged_in') %}
                <a href="{{ url_for('admin_panel') }}">Админ-панель</a>
                <a href="{{ url_for('admin_logout') }}">Выход</a>
            {% else %}
                <a href="{{ url_for('login') }}">Вход</a>
                <a href="{{ url_for('admin_login') }}">Админ</a>
            {% endif %}
        </div>
    </nav>
    
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    
    <script>
        {% block script %}{% endblock %}
    </script>
</body>
</html>
""")

create_template_if_not_exists('index.html', """{% extends 'base.html' %}

{% block title %}Главная | Система заказов{% endblock %}

{% block header %}Система заказов{% endblock %}

{% block content %}
<div style="text-align: center; margin-top: 50px;">
    <h2>Добро пожаловать в систему заказов</h2>
    <p>Пожалуйста, выберите нужный раздел в меню выше.</p>
</div>
{% endblock %}
""")

create_template_if_not_exists('login.html', """{% extends 'base.html' %}

{% block title %}Вход | Система заказов{% endblock %}

{% block header %}Вход в систему{% endblock %}

{% block content %}
<div class="login-form">
    <h2>Вход</h2>
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    <form id="loginForm" method="post">
        <div class="form-group">
            <label for="password">Пароль:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <button type="submit" class="btn">Войти</button>
    </form>
</div>
{% endblock %}

{% block script %}
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    var password = document.getElementById('password').value;
    var formData = new FormData();
    formData.append('password', password);
    
    fetch('/check_password', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            alert('Неверный пароль');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при входе');
    });
});
{% endblock %}
""")

create_template_if_not_exists('admin_login.html', """{% extends 'base.html' %}

{% block title %}Админ | Система заказов{% endblock %}

{% block header %}Вход в админ-панель{% endblock %}

{% block content %}
<div class="login-form">
    <h2>Вход в админ-панель</h2>
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    <form id="adminLoginForm" method="post">
        <div class="form-group">
            <label for="password">Пароль:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <button type="submit" class="btn">Войти</button>
    </form>
</div>
{% endblock %}

{% block script %}
document.getElementById('adminLoginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    var password = document.getElementById('password').value;
    var formData = new FormData();
    formData.append('password', password);
    
    fetch('/admin_login', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            alert('Неверный пароль');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при входе');
    });
});
{% endblock %}
""")

create_template_if_not_exists('menu.html', """{% extends 'base.html' %}

{% block title %}Меню | Система заказов{% endblock %}

{% block header %}Меню{% endblock %}

{% block content %}
<div class="product-list">
    {% for supplier, items in products.items() %}
    <div class="product-category">
        <h3>{{ supplier }}</h3>
        {% for item in items %}
        <div class="product-item">
            <input type="checkbox" id="product-{{ loop.index }}-{{ supplier|replace(' ', '-') }}" data-name="{{ item }}">
            <label for="product-{{ loop.index }}-{{ supplier|replace(' ', '-') }}">{{ item }}</label>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
</div>

<button id="orderBtn" class="order-btn">Отправить заказ</button>
{% endblock %}

{% block script %}
document.getElementById('orderBtn').addEventListener('click', function() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    var selectedItems = [];
    
    checkboxes.forEach(function(checkbox) {
        selectedItems.push(checkbox.dataset.name);
    });
    
    if (selectedItems.length === 0) {
        alert('Выберите хотя бы один товар');
        return;
    }
    
    fetch('/order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            items: selectedItems
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Заказ успешно отправлен');
            // Снимаем выделение со всех чекбоксов
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = false;
            });
        } else {
            alert('Ошибка: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке заказа');
    });
});
{% endblock %}
""")

create_template_if_not_exists('hoz.html', """{% extends 'base.html' %}

{% block title %}Хоз. товары | Система заказов{% endblock %}

{% block header %}Хоз. товары{% endblock %}

{% block content %}
<div class="product-list">
    <div class="product-category">
        <h3>Хоз. товары</h3>
        {% for item in hoz_items %}
        <div class="product-item">
            <input type="checkbox" id="hoz-{{ loop.index }}" data-name="{{ item }}">
            <label for="hoz-{{ loop.index }}">{{ item }}</label>
        </div>
        {% endfor %}
    </div>
</div>

<button id="orderBtn" class="order-btn">Отправить заказ</button>
{% endblock %}

{% block script %}
document.getElementById('orderBtn').addEventListener('click', function() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    var selectedItems = [];
    
    checkboxes.forEach(function(checkbox) {
        selectedItems.push(checkbox.dataset.name);
    });
    
    if (selectedItems.length === 0) {
        alert('Выберите хотя бы один товар');
        return;
    }
    
    fetch('/order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            items: selectedItems
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Заказ успешно отправлен');
            // Снимаем выделение со всех чекбоксов
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = false;
            });
        } else {
            alert('Ошибка: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке заказа');
    });
});
{% endblock %}
""")

create_template_if_not_exists('fish.html', """{% extends 'base.html' %}

{% block title %}Рыба | Система заказов{% endblock %}

{% block header %}Рыба{% endblock %}

{% block content %}
<div class="product-list">
    <div class="product-category">
        <h3>Рыба</h3>
        {% for item in fish_items %}
        <div class="product-item">
            <input type="checkbox" id="fish-{{ loop.index }}" data-name="{{ item }}">
            <label for="fish-{{ loop.index }}">{{ item }}</label>
        </div>
        {% endfor %}
    </div>
</div>

<button id="orderBtn" class="order-btn">Отправить заказ</button>
{% endblock %}

{% block script %}
document.getElementById('orderBtn').addEventListener('click', function() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    var selectedItems = [];
    
    checkboxes.forEach(function(checkbox) {
        selectedItems.push(checkbox.dataset.name);
    });
    
    if (selectedItems.length === 0) {
        alert('Выберите хотя бы один товар');
        return;
    }
    
    fetch('/order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            items: selectedItems
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Заказ успешно отправлен');
            // Снимаем выделение со всех чекбоксов
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = false;
            });
        } else {
            alert('Ошибка: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке заказа');
    });
});
{% endblock %}
""")

create_template_if_not_exists('chicken.html', """{% extends 'base.html' %}

{% block title %}Курица | Система заказов{% endblock %}

{% block header %}Курица{% endblock %}

{% block content %}
<div class="product-list">
    <div class="product-category">
        <h3>Курица</h3>
        {% for item in chicken_items %}
        <div class="product-item">
            <input type="checkbox" id="chicken-{{ loop.index }}" data-name="{{ item }}">
            <label for="chicken-{{ loop.index }}">{{ item }}</label>
        </div>
        {% endfor %}
    </div>
</div>

<button id="orderBtn" class="order-btn">Отправить заказ</button>
{% endblock %}

{% block script %}
document.getElementById('orderBtn').addEventListener('click', function() {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    var selectedItems = [];
    
    checkboxes.forEach(function(checkbox) {
        selectedItems.push(checkbox.dataset.name);
    });
    
    if (selectedItems.length === 0) {
        alert('Выберите хотя бы один товар');
        return;
    }
    
    fetch('/order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            items: selectedItems
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Заказ успешно отправлен');
            // Снимаем выделение со всех чекбоксов
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = false;
            });
        } else {
            alert('Ошибка: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке заказа');
    });
});
{% endblock %}
""")

create_template_if_not_exists('admin.html', """{% extends 'base.html' %}

{% block title %}Админ-панель | Система заказов{% endblock %}

{% block header %}Админ-панель{% endblock %}

{% block content %}
<div class="admin-panel">
    <div class="admin-section">
        <h3>Продукты</h3>
        <div class="admin-form">
            <textarea id="productsData">{{ products|tojson }}</textarea>
            <button id="saveProducts">Сохранить</button>
        </div>
    </div>
    
    <div class="admin-section">
        <h3>Хоз. товары</h3>
        <div class="admin-form">
            <textarea id="hozData">{{ hoz_items|tojson }}</textarea>
            <button id="saveHoz">Сохранить</button>
        </div>
    </div>
    
    <div class="admin-section">
        <h3>Рыба</h3>
        <div class="admin-form">
            <textarea id="fishData">{{ fish_items|tojson }}</textarea>
            <button id="saveFish">Сохранить</button>
        </div>
    </div>
    
    <div class="admin-section">
        <h3>Курица</h3>
        <div class="admin-form">
            <textarea id="chickenData">{{ chicken_items|tojson }}</textarea>
            <button id="saveChicken">Сохранить</button>
        </div>
    </div>
    
    <div class="admin-section">
        <h3>Пароли</h3>
        <div class="admin-form">
            <div class="form-group">
                <label for="userPassword">Пароль пользователя:</label>
                <input type="text" id="userPassword" value="4444">
            </div>
            <div class="form-group">
                <label for="adminPassword">Пароль администратора:</label>
                <input type="text" id="adminPassword" value="880088">
            </div>
            <button id="savePasswords">Сохранить</button>
        </div>
    </div>
</div>
{% endblock %}

{% block script %}
// Сохранение продуктов
document.getElementById('saveProducts').addEventListener('click', function() {
    try {
        var productsData = JSON.parse(document.getElementById('productsData').value);
        
        fetch('/api/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                products: productsData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Продукты успешно обновлены');
            } else {
                alert('Ошибка: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при обновлении продуктов');
        });
    } catch (e) {
        alert('Ошибка в формате данных: ' + e.message);
    }
});

// Сохранение хоз. товаров
document.getElementById('saveHoz').addEventListener('click', function() {
    try {
        var hozData = JSON.parse(document.getElementById('hozData').value);
        
        fetch('/api/hoz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hoz_items: hozData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Хоз. товары успешно обновлены');
            } else {
                alert('Ошибка: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при обновлении хоз. товаров');
        });
    } catch (e) {
        alert('Ошибка в формате данных: ' + e.message);
    }
});

// Сохранение рыбы
document.getElementById('saveFish').addEventListener('click', function() {
    try {
        var fishData = JSON.parse(document.getElementById('fishData').value);
        
        fetch('/api/fish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fish_items: fishData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Рыба успешно обновлена');
            } else {
                alert('Ошибка: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при обновлении рыбы');
        });
    } catch (e) {
        alert('Ошибка в формате данных: ' + e.message);
    }
});

// Сохранение курицы
document.getElementById('saveChicken').addEventListener('click', function() {
    try {
        var chickenData = JSON.parse(document.getElementById('chickenData').value);
        
        fetch('/api/chicken', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chicken_items: chickenData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Курица успешно обновлена');
            } else {
                alert('Ошибка: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при обновлении курицы');
        });
    } catch (e) {
        alert('Ошибка в формате данных: ' + e.message);
    }
});

// Сохранение паролей
document.getElementById('savePasswords').addEventListener('click', function() {
    var userPassword = document.getElementById('userPassword').value;
    var adminPassword = document.getElementById('adminPassword').value;
    
    // Сохраняем пароль пользователя
    fetch('/api/password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type: 'user',
            password: userPassword
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Сохраняем пароль администратора
            return fetch('/api/password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'admin',
                    password: adminPassword
                })
            });
        } else {
            throw new Error(data.message);
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Пароли успешно обновлены');
        } else {
            alert('Ошибка: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обновлении паролей');
    });
});
{% endblock %}
""")

# Создаем директорию для статических файлов, если она не существует
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
css_dir = os.path.join(static_dir, 'css')
if not os.path.exists(css_dir):
    os.makedirs(css_dir, exist_ok=True)

# Создаем файл style.css, если он не существует
css_file = os.path.join(css_dir, 'style.css')
if not os.path.exists(css_file):
    with open(css_file, 'w') as f:
        f.write("""
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: #333;
    color: white;
    padding: 10px 0;
    text-align: center;
}

nav {
    display: flex;
    justify-content: center;
    background-color: #444;
    padding: 10px 0;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 0 15px;
    padding: 5px 10px;
    border-radius: 5px;
}

nav a:hover {
    background-color: #555;
}

.login-form {
    max-width: 400px;
    margin: 50px auto;
    padding: 20px;
    background-color: white;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.login-form h2 {
    text-align: center;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
}

.form-group input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.btn {
    display: inline-block;
    padding: 10px 15px;
    background-color: #333;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.btn:hover {
    background-color: #555;
}

.error {
    color: red;
    margin-bottom: 15px;
}

.product-list {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}

.product-category {
    flex: 1;
    min-width: 300px;
    background-color: white;
    border-radius: 5px;
    padding: 15px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.product-category h3 {
    margin-top: 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #ddd;
}

.product-item {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.product-item input[type="checkbox"] {
    margin-right: 10px;
}

.order-btn {
    display: block;
    width: 100%;
    padding: 15px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 20px;
}

.order-btn:hover {
    background-color: #45a049;
}

.admin-panel {
    background-color: white;
    border-radius: 5px;
    padding: 20px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.admin-section {
    margin-bottom: 30px;
}

.admin-section h3 {
    margin-top: 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #ddd;
}

.admin-form {
    margin-top: 20px;
}

.admin-form textarea {
    width: 100%;
    height: 200px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: monospace;
}

.admin-form input[type="text"] {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-bottom: 10px;
}

.admin-form button {
    padding: 10px 15px;
    background-color: #333;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.admin-form button:hover {
    background-color: #555;
}

.message {
    padding: 10px;
    margin-bottom: 15px;
    border-radius: 4px;
}

.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

@media (max-width: 768px) {
    .product-category {
        min-width: 100%;
    }
    
    nav {
        flex-direction: column;
        align-items: center;
    }
    
    nav a {
        margin: 5px 0;
    }
}
        """)
