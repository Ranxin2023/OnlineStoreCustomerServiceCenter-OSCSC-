
from database.db_management import get_connection


def save_or_update_user(
    channel_id,
    name,
    star,
    country,
    remark,
    orders, 
    last_message,
    last_sender
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (
            channel_id, name, star, country, remark, orders, last_message, last_sender
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(channel_id, name)
        DO UPDATE SET
            star=excluded.star,
            country=excluded.country,
            remark=excluded.remark,
            orders=excluded.orders, 
            last_message=excluded.last_message,
            last_sender=excluded.last_sender,
            updated_at=CURRENT_TIMESTAMP
    """, (channel_id, name, star, country, remark, orders, last_message, last_sender))

    conn.commit()
    conn.close()