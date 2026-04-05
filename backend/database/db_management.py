import sqlite3
import os
from typing import List
DB_PATH = os.path.join(os.path.dirname(__file__), "orders.db")

ALLOWED_TABLES = {"yanwen_orders", "users", "orders", "user_orders", "sqlite_sequence"}
ALLOWED_COLUMNS = {"yanwen_orders":["tracking_number", "last_status", "buyer_id"],
                   "users":["id", "channel_id", "name", "star", "country", "remark", "last_message", "last_sender", "updated_at", "vip"],
                   "user_orders":["id", "channel_id","status", "created_at", "channel_id", "order_creation_date", "status_code", "orders", "user_name"]}
def get_connection():
    return sqlite3.connect(DB_PATH)

def fetch_by_key(
    table_name: str,
    schema_names: List[str],
    key: str,
    value: str,
    order_by: str = None,   # 🔥 新增
    desc: bool = False,     # 🔥 新增
    limit: int = None       # 🔥 新增
):
    if table_name not in ALLOWED_TABLES:
        raise ValueError("Invalid table")

    for col in schema_names:
        if col not in ALLOWED_COLUMNS[table_name]:
            raise ValueError(f"Invalid column: {col}")

    if key not in ALLOWED_COLUMNS[table_name]:
        raise ValueError("Invalid key column")

    conn = get_connection()
    cursor = conn.cursor()

    columns_str = ", ".join(schema_names)

    sql = f"""
    SELECT {columns_str}
    FROM {table_name}
    WHERE {key} = ?
    """

    # 👉 ORDER BY
    if order_by:
        if order_by not in ALLOWED_COLUMNS[table_name]:
            raise ValueError("Invalid order_by column")

        sql += f" ORDER BY {order_by}"
        if desc:
            sql += " DESC"

    # 👉 LIMIT
    if limit:
        sql += f" LIMIT {limit}"

    cursor.execute(sql, (value,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return dict(zip(schema_names, row))