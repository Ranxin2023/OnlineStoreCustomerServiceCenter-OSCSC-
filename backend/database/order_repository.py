import os
import sqlite3
from datetime import datetime
DB_PATH = os.path.join(os.path.dirname(__file__), "orders.db")


def save_orders_to_db(orders, store):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_orders = []

    for order in orders:

        order_id = order.get("order_id")

        # 关键：判断数据库是否已经存在
        cursor.execute(
            "SELECT 1 FROM orders WHERE order_id=? LIMIT 1",
            (order_id,)
        )
        exists = cursor.fetchone()

        if exists:
            continue

        new_orders.append(order)

        cursor.execute("""
        INSERT INTO orders VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )
        """, (
            order.get("order_id"),
            store,
            order.get("order_link"),
            order.get("date"),
            order.get("buyer"),
            order.get("product"),
            order.get("specs"),
            order.get("sku"),
            order.get("price"),
            order.get("qty"),
            order.get("amount"),
            order.get("status"),
            order.get("status_en"),
            order.get("ae_ioss"),
            order.get("semi_managed"),
            order.get("action"),
            order.get("recipient"),
            order.get("address"),
            order.get("country"),
            order.get("postal_code"),
            order.get("email"),
            order.get("phone"),
            order.get("tax_number"),
            order.get("remark")
        ))

    conn.commit()
    conn.close()

    return new_orders

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
