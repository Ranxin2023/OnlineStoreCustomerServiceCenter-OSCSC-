from database.db_management import get_connection, fetch_by_key

def save_user_orders(user_name, orders, order_id, status, status_code, order_time):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO user_orders (user_name, orders, order_id, status, status_code, order_creation_date)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(order_id) DO UPDATE SET
        status = excluded.status,
        status_code = excluded.status_code,
        order_creation_date = excluded.order_creation_date
    """

    cursor.execute(sql, (user_name, orders, order_id, status, status_code, order_time))
    conn.commit()


def fetch_orders_by_username(user_name:str):
    return fetch_by_key(schema_name=["orders"], table_name="user_orders", key="user_name", value=user_name)