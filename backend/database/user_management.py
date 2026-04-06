
from database.db_management import get_connection,fetch_by_key

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
            channel_id, name, star, country, remark, last_message, last_sender
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
    return fetch_by_key(schema_name=["country"], table_name="users",key="name", value=user_name)

def fetch_vip_status_from_users(user_name:str):
    return fetch_by_key(schema_name=["vip"], table_name="users",key="name", value=user_name)