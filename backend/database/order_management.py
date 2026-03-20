
from database.db_management import get_connection


def save_orders_to_db(orders, store):
    conn = get_connection()
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
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
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
            order.get("remark"),
            order.get("short_address")
        ))

    conn.commit()
    conn.close()

    return new_orders

