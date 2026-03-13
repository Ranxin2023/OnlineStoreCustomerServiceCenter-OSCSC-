import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "orders.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        store TEXT,
        order_link TEXT,
        date TEXT,
        buyer TEXT,
        product TEXT,
        specs TEXT,
        sku TEXT,
        price TEXT,
        qty INTEGER,
        amount TEXT,
        status TEXT,
        status_en TEXT,
        ae_ioss TEXT,
        semi_managed TEXT,
        action TEXT,
        recipient TEXT,
        address TEXT,
        country TEXT, 
        postal_code TEXT,
        email TEXT,
        phone TEXT,
        tax_number TEXT
        short_address TEXT
    )
    """)

    conn.commit()
    conn.close()

