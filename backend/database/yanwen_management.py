
from db_management import get_connection, fetch_by_key
def save_yanwen_order(order: dict):
    """
    插入或更新 yanwen_orders
    order 示例：
    {
        "order_id": "123",
        "tracking_number": "YT123456789",
        "last_status": "Delivered",
        "last_status_code": "DELIVERED",
        "last_update_time": "2026-04-05 10:00:00",
        "buyer_id": "user123"
    }
    """

    sql = """
    INSERT INTO yanwen_orders (
        order_id,
        tracking_number,
        last_status,
        last_status_code,
        last_update_time,
        buyer_id,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)

    ON CONFLICT(tracking_number) DO UPDATE SET
        last_status = excluded.last_status,
        last_status_code = excluded.last_status_code,
        last_update_time = excluded.last_update_time,
        updated_at = CURRENT_TIMESTAMP;
    """
    conn=get_connection()
    cursor = conn.cursor()
    values = (
        order.get("order_id"),
        order.get("tracking_number"),
        order.get("last_status"),
        order.get("last_status_code"),
        order.get("last_update_time"),
        order.get("buyer_id"),
    )

    try:
        cursor.execute(sql, values)
        conn.commit()
        print(f"[DB] Saved tracking: {order.get('tracking_number')}")
    except Exception as e:
        print(f"[DB ERROR] {e}")
        conn.rollback()

def fetch_order_from_yanwen(user_name: str):
    return fetch_by_key(
        table_name="yanwen_orders",
        schema_names=["order_id", "tracking_number"],
        key="user_name",
        value=user_name,
        order_by="id",  
        desc=True,
        limit=1
    )


def fetch_tracking_from_yanwen(tracking_number:str):
    return fetch_by_key(
        table_name="yanwen_orders",
        schema_names=["last_status", "last_update_time"],
        key="tracking_number",
        value=tracking_number,
        order_by=None,  
        desc=None,
        limit=None
    )
     