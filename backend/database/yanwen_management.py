
from database.db_management import get_connection, fetch_by_key
import json

def save_yanwen_order(tracking_number, data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO logistics_orders (
        tracking_number,
        carrier,
        raw_data,
        updated_at
    )
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(tracking_number)
    DO UPDATE SET
        raw_data = excluded.raw_data,
        updated_at = CURRENT_TIMESTAMP
    """, (
        tracking_number,
        "yanwen",
        json.dumps(data)   # 🔥直接存完整 data
    ))

    conn.commit()
    conn.close()

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
     