import sqlite3
import os
from datetime import datetime
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
            tax_number TEXT, 
            short_address TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,

            name TEXT,           -- 用户名
            star TEXT,           -- 星标（无星标 / ⭐1 / ⭐2...）
            country TEXT,        -- 国家
            remark TEXT,         -- 备注

            last_message TEXT,
            last_sender TEXT,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(channel_id, name)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id VARCHAR(50) UNIQUE,
            status VARCHAR(50),
            created_at DATETIME,
            channel_id VARCHAR(20),
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status_code INT DEFAULT -1
        );
    """)
    conn.commit()
    conn.close()



def get_last_commit_time(store):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT last_commit_time FROM sync_state WHERE store=?",
        (store,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]

    return None

def update_commit_time(store):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT OR REPLACE INTO sync_state (store, last_commit_time)
        VALUES (?,?)
    """, (store, now))

    conn.commit()
    conn.close()

    return now
