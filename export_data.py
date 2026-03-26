import sqlite3
import json
from datetime import datetime

DB_NAME = 'tea_platform.db'
OUTPUT_FILE = 'static/data.json'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def export_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    data = {}
    
    # 1. Total Sales & Order Count
    cursor.execute('SELECT COUNT(*), SUM(total_amount) FROM orders')
    row = cursor.fetchone()
    count = row[0]
    total = row[1] if row[1] is not None else 0
    
    data['order_count'] = count
    data['total_sales'] = round(total, 2)
    data['avg_order_value'] = round(total / count, 2) if count > 0 else 0

    
    # Customer Count
    cursor.execute('SELECT COUNT(*) FROM customers')
    data['customer_count'] = cursor.fetchone()[0]

    # Recent Orders
    cursor.execute('''
        SELECT o.id, c.name, o.total_amount, o.status, o.order_date
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.order_date DESC
        LIMIT 10
    ''')
    # Convert Row objects to dicts
    recent_orders = []
    for row in cursor.fetchall():
        recent_orders.append({
            'id': row['id'],
            'customer': row['name'],
            'amount': round(row['total_amount'], 2),
            'status': row['status'],
            'date': row['order_date']
        })
    data['recent_orders'] = recent_orders
    
    # 2. Sales by Product Category (requires join)
    cursor.execute('''
        SELECT p.category, SUM(oi.quantity * oi.price_at_time) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        GROUP BY p.category
    ''')
    category_sales = {row['category']: round(row['revenue'], 2) for row in cursor.fetchall()}
    data['category_sales'] = category_sales
    
    # 3. Sales Over Time (Monthly)
    cursor.execute('''
        SELECT strftime('%Y-%m', order_date) as month, SUM(total_amount) as revenue
        FROM orders
        GROUP BY month
        ORDER BY month
    ''')
    monthly_sales = {row['month']: round(row['revenue'], 2) for row in cursor.fetchall()}
    data['monthly_sales'] = monthly_sales
    
    # 4. Top Products
    cursor.execute('''
        SELECT p.name, SUM(oi.quantity) as sold_count
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        GROUP BY p.name
        ORDER BY sold_count DESC
        LIMIT 5
    ''')
    top_products = {row['name']: row['sold_count'] for row in cursor.fetchall()}
    data['top_products'] = top_products

    # 5. All Products (for e-commerce frontend)
    cursor.execute('SELECT id, name, category, price, stock FROM products')
    products = []
    for row in cursor.fetchall():
        products.append({
            'id': row['id'],
            'name': row['name'],
            'category': row['category'],
            'price': row['price'],
            'stock': row['stock']
        })
    data['products'] = products

    conn.close()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Data exported to {OUTPUT_FILE}")

if __name__ == '__main__':
    export_data()
