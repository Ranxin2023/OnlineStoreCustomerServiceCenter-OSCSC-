
from constants.constant_values import SAFE_USERS, LOADING_TIME, driver_pool
from models.web_scrapy_model import WebScrapyModel
from database.user_management import save_or_update_user
from flask import Blueprint, jsonify, request
from models.driver import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sockets.socket_bp import socketio
import threading
from utils.listening_chat import listen_chat

chat_bp = Blueprint("chat", __name__)

# ----------------model definition------------------

driver_model=Driver()

@chat_bp.route("/api/chat/open", methods=["POST", "OPTIONS"])
def open_chat():
    # option method return 
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.json

    channel_id = data.get("channelId")
    url = data.get("url")
    message = data.get("message")

    if not message:
        return jsonify({"error": "message is required"}), 400

    # 0 加载driver
    driver=None
    try:
        driver = driver_model.get_driver(channel_id, driver_pool=driver_pool)
    except Exception as e:
        print(f"[open_chat]Cannot open driver ...{e}")
        return jsonify({"error": str(e)}), 500

    # 1 打开聊天页面
    try:
        driver.get(url)
    except Exception as e:
        print("Cannot open URL...")
        return jsonify({"error": str(e)}), 500
        
    # 2 等聊天列表加载
    try:
        WebDriverWait(driver, LOADING_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.im-session-item")
            )
        )

        sessions = driver.find_elements(
            By.CSS_SELECTOR,
            "div.im-session-item"
        )

        target_session = None
        target_name = None
        for s in sessions:

            try:
                name = s.find_element(
                    By.CSS_SELECTOR,
                    "div.im-session-item-name-content b"
                ).text.strip()

                print("Found chat:", name)

                for safe_user in SAFE_USERS:
                    if safe_user in name:
                        target_session = s
                        target_name = name
                        break

                if target_session:
                    break

            except Exception:
                continue

        if target_session is None:
            return jsonify({"error": "No safe user session found"}), 404
    except Exception as e:
        print("Error in loading the chat box")
        return jsonify({"error": str(e)}), 500
    
    # 3 点击聊天
    try:
        driver.execute_script(
            "arguments[0].click();",
            target_session
        )

        print(f"Opened chat with {target_name}")
    except Exception as e:
        print(f"Error in clicking the chat {e}")
        return jsonify({"error": str(e)}), 500

    # 4. 获取所有消息
    # ✅ 等聊天内容加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.im-message-item")
        )
    )

    messages = driver.find_elements(By.CSS_SELECTOR, "div.im-message-item")

    latest_message_text = ""
    latest_sender = ""

    if messages:
        last = messages[-1]

        latest_message_text = last.text.strip()
        cls = last.get_attribute("class")

        if "self" in cls:
            latest_sender = "seller"
        else:
            latest_sender = "buyer"

    print(f"[chat] latest_message: {latest_message_text}")
    print(f"[chat] sender: {latest_sender}")

    # 5. 存储用户信息
    web_scrapy_model=WebScrapyModel()
    web_scrapy_model.driver=driver
    user_name, star, country, remark = web_scrapy_model.extract_user_info()
    print(f"[open_chat]user info are: {user_name}, {star}, {country}, {remark}")
    save_or_update_user(
        channel_id,
        user_name,
        star,
        country,
        remark,
        latest_message_text,
        latest_sender
    )
    return jsonify({
        "status": "message typed",
        "user": target_name,
        "message": message
    })


@chat_bp.route("/api/chat/start-listener", methods=["POST"])
def start_listener():

    data = request.json
    channel_id = data.get("channelId")

    driver = driver_model.get_driver(channel_id, driver_pool)

    thread = threading.Thread(
        target=listen_chat,
        args=(driver, socketio, channel_id),
        daemon=True
    )

    thread.start()

    return jsonify({"status": "listener started"})