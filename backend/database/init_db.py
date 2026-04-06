from db_management import get_connection
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
            star TEXT,           -- 星标（无星标 / ⭐1 / ⭐2...)
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yanwen_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id TEXT,                 -- 你的订单号（可选）
            tracking_number TEXT NOT NULL, -- 运单号（核心）

            last_status TEXT,              -- 最新物流描述(message)
            last_status_code TEXT,         -- 状态码(LM40等)
            last_update_time TEXT,         -- 最新更新时间

            buyer_id TEXT,                 -- 买家（用于发消息）

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logistics_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id TEXT,
            tracking_number TEXT,
            buyer_id TEXT,

            carrier TEXT,         
            raw_data TEXT,        

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );""")
    conn.commit()
    conn.close()

if __name__=="__main__":
    init_db()