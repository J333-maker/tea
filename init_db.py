import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = 'tea_platform.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            region TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_date TEXT NOT NULL,
            total_amount REAL,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price_at_time REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    conn.commit()
    print("Database initialized.")
    return conn

def populate_data(conn):
    cursor = conn.cursor()

    # Products: Anding Cloud Tea varieties
    products = [
        ('安顶云雾茶-明前特级', 'Green Tea', 1200.0, 50),
        ('安顶云雾茶-雨前一级', 'Green Tea', 800.0, 100),
        ('安顶云雾茶-春茶二级', 'Green Tea', 500.0, 200),
        ('安顶红茶-特级', 'Black Tea', 900.0, 80),
        ('安顶白茶-精品', 'White Tea', 1500.0, 30),
        ('安顶云雾茶-大众款', 'Green Tea', 300.0, 500)
    ]
    cursor.executemany('INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)', products)

    # Customers
    regions = ['Hangzhou', 'Shanghai', 'Beijing', 'Guangzhou', 'Shenzhen', 'Chengdu']
    first_names = ['Li', 'Wang', 'Zhang', 'Liu', 'Chen', 'Yang', 'Zhao', 'Huang', 'Zhou', 'Wu']
    last_names = ['Wei', 'Fang', 'Ming', 'Jie', 'Hui', 'Lei', 'Na', 'Ying', 'Qiang', 'Tao']
    
    customers = []
    for _ in range(50):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{name.lower().replace(' ', '.')}@example.com"
        region = random.choice(regions)
        customers.append((name, email, region))
    
    cursor.executemany('INSERT INTO customers (name, email, region) VALUES (?, ?, ?)', customers)
    
    # Commit to get IDs
    conn.commit()

    # Orders
    # Generate orders for the past 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    orders = []
    order_items = []
    
    # Get customer and product IDs
    cursor.execute('SELECT id FROM customers')
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT id, price FROM products')
    product_dict = {row[0]: row[1] for row in cursor.fetchall()}
    product_ids = list(product_dict.keys())

    for _ in range(200): # 200 orders
        cust_id = random.choice(customer_ids)
        # Random date
        days_offset = random.randint(0, 365)
        order_date = (start_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
        status = random.choice(['Completed', 'Shipped', 'Processing', 'Cancelled'])
        
        # Order items
        num_items = random.randint(1, 5)
        current_order_items = []
        total_amount = 0
        
        for _ in range(num_items):
            prod_id = random.choice(product_ids)
            qty = random.randint(1, 3)
            price = product_dict[prod_id]
            current_order_items.append((prod_id, qty, price))
            total_amount += price * qty
            
        orders.append((cust_id, order_date, total_amount, status))
        # We need the order ID for items, so we insert order first
        cursor.execute('INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, ?)', 
                       (cust_id, order_date, total_amount, status))
        order_id = cursor.lastrowid
        
        for item in current_order_items:
            cursor.execute('INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (?, ?, ?, ?)',
                           (order_id, item[0], item[1], item[2]))

    conn.commit()
    print("Mock data populated.")

if __name__ == '__main__':
    conn = init_db()
    populate_data(conn)
    conn.close()
