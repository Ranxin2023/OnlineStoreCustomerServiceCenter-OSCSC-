
from database.db_management import get_connection


def save_or_update_user(
    channel_id,
    name,
    star,
    country,
    remark,
     
    last_message,
    last_sender
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (
            channel_id, name, star, country, remark, orders, last_message, last_sender
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(channel_id, name)
        DO UPDATE SET
            star=excluded.star,
            country=excluded.country,
            remark=excluded.remark,
            last_message=excluded.last_message,
            last_sender=excluded.last_sender,
            updated_at=CURRENT_TIMESTAMP
    """, (channel_id, name, star, country, remark, last_message, last_sender))

    conn.commit()
    conn.close()



def fetch_country_from_users(user_name:str):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    SELECT country FROM users
    WHERE user_name = ?
    """

    cursor.execute(sql, (user_name,))
    rows = cursor.fetchall()

    conn.close()

    # 提取 orders 字段
    return [row[0] for row in rows]

def fetch_vip_status_from_users(user_name:str):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    SELECT vip FROM users
    WHERE user_name = ?
    """

    cursor.execute(sql, (user_name,))
    rows = cursor.fetchall()

    conn.close()

    # 提取 vip 字段
    return [row[0] for row in rows]