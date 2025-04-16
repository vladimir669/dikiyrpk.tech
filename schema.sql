-- Создание таблицы поставщиков
CREATE TABLE suppliers (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

-- Создание таблицы продуктов
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  supplier_id INTEGER REFERENCES suppliers(id) ON DELETE CASCADE
);

-- Создание таблицы филиалов
CREATE TABLE branches (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

-- Создание таблицы заявок
CREATE TABLE requests (
  id SERIAL PRIMARY KEY,
  cook_name TEXT NOT NULL,
  fill_date DATE NOT NULL,
  request_date DATE NOT NULL,
  branch_id INTEGER REFERENCES branches(id) ON DELETE SET NULL,
  supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Создание таблицы элементов заявки
CREATE TABLE request_items (
  id SERIAL PRIMARY KEY,
  request_id INTEGER REFERENCES requests(id) ON DELETE CASCADE,
  product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
  quantity INTEGER NOT NULL
);

-- Вставка поставщиков из списка
INSERT INTO suppliers (name) VALUES 
('Свит Лайф'),
('Рафт'),
('Оши'),
('Хоз. товары'),
('Рыба');

-- Вставка филиалов
INSERT INTO branches (name) VALUES 
('Центральный'),
('Северный'),
('Южный'),
('Западный'),
('Восточный');
