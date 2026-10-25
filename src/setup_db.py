import sqlite3
import os

os.makedirs("data", exist_ok=True)
db_path = os.path.join("data", "ecommerce.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Populating Enterprise Kaggle Sales Schema...")

# Drop old tables to start fresh
cursor.execute("DROP TABLE IF EXISTS orders;")
cursor.execute("DROP TABLE IF EXISTS customers;")
cursor.execute("DROP TABLE IF EXISTS products;")
cursor.execute("DROP TABLE IF EXISTS agent_schema_metadata;")

# 1. Complex Business Tables
cursor.execute("""
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_city TEXT,
    customer_state TEXT
);
""")

cursor.execute("""
CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_price REAL,
    product_weight_g INTEGER
);
""")

cursor.execute("""
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    order_purchase_timestamp TEXT,
    order_status TEXT,
    payment_value REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

# 2. Agent Metadata Table
cursor.execute("""
CREATE TABLE agent_schema_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT UNIQUE,
    column_details TEXT,
    business_description TEXT
);
""")

# Insert real-world style Kaggle rows
cursor.executemany("INSERT INTO customers VALUES (?, ?, ?);", [
    ('c_001', 'Sao Paulo', 'SP'), ('c_002', 'Rio de Janeiro', 'RJ'), ('c_003', 'Sao Paulo', 'SP')
])
cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?);", [
    ('p_101', 'electronics', 1200.50, 450), ('p_102', 'office_furniture', 340.00, 8500), ('p_103', 'electronics', 15.00, 50)
])
cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?);", [
    ('o_901', 'c_001', 'p_101', '2026-01-10 14:32:00', 'delivered', 1200.50),
    ('o_902', 'c_002', 'p_102', '2026-02-15 09:15:00', 'delivered', 340.00),
    ('o_903', 'c_003', 'p_103', '2026-02-20 18:22:00', 'shipped', 15.00)
])

# Insert clean production metadata descriptions
cursor.executemany("INSERT INTO agent_schema_metadata (table_name, column_details, business_description) VALUES (?, ?, ?);", [
    ('customers', 'customer_id (text), customer_city (text), customer_state (text)', 'Contains customer geographic profiles, including cities and state abbreviations.'),
    ('products', 'product_id (text), product_category_name (text), product_price (real), product_weight_g (int)', 'Inventory lookup table mapping products to categories, listing unit prices, and weights in grams.'),
    ('orders', 'order_id (text), customer_id (text), product_id (text), order_purchase_timestamp (text), order_status (text), payment_value (real)', 'Transactional ledger tracking sales, order processing statuses, timestamps, and actual payment amounts collected.')
])

conn.commit()
conn.close()
print("Success! Complex Kaggle Data Layer Created.")
