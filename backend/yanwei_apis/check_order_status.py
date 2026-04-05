from database.yanwen_management import fetch_order_from_yanwen

def check_order_status(user_name):
    """
    根据 user_name 查询订单物流状态
    """
    try:

        order=fetch_order_from_yanwen(user_name=user_name)

        if not order:
            return "I couldn't find any order under your account."

        order_id, tracking_number = order
        tracking=fetch_order_from_yanwen(tracking_number=tracking_number)
        if not tracking:
            return f"I found your order {order_id}, but no tracking info yet."

        last_status, last_update_time = tracking

        # 👉 3️⃣ 返回自然语言（给chatbot）
        return (
            f"📦 Order {order_id}\n"
            f"Tracking Number: {tracking_number}\n"
            f"Status: {last_status}\n"
            f"Last Update: {last_update_time}"
        )

    except Exception as e:
        print(f"[check_order_status ERROR] {e}")
        return "Sorry, I couldn't retrieve your order status right now."