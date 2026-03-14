
from flask import Blueprint, jsonify, request
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sockets.socket_bp import socketio
from utils.constant_values import SAFE_USERS, driver_pool
from utils.listening_chat import listen_chat
from models.driver import Driver
import threading
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
    try:
        driver = driver_model.get_driver(channel_id, driver_pool=driver_pool)
    except Exception as e:
        print("Cannot open driver ...")
        return jsonify({"error": str(e)}), 500

    # 1 打开聊天页面
    try:
        driver.get(url)
    except Exception as e:
        print("Cannot open URL...")
        return jsonify({"error": str(e)}), 500
        
    # 2 等聊天列表加载
    try:
        WebDriverWait(driver, 20).until(
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
    
    # # 4 读取最新消息
    # try:
    #     print("Reading latest message...")

    #     WebDriverWait(driver, 20).until(
    #         EC.presence_of_element_located(
    #             (By.CSS_SELECTOR, "div.im-message-item")
    #         )
    #     )

    #     messages = driver.find_elements(
    #         By.CSS_SELECTOR,
    #         "div.im-message-item"
    #     )

    #     if not messages:
    #         print("No messages found")
    #         latest_message_text = ""
    #         latest_sender = "unknown"
    #     else:
    #         latest = messages[-1]

    #         latest_message_text = latest.text.strip()
    #         cls = latest.get_attribute("class")

    #         # 判断发送者
    #         if "self" in cls:
    #             latest_sender = "seller"
    #         else:
    #             latest_sender = "buyer"

    #         print("Latest message:", latest_message_text)
    #         print("Sender:", latest_sender)

    #     # 如果最后一条是自己发的，不再发送
    #     if latest_sender == "seller":
    #         print("Last message was sent by seller, skip sending")
    #         return jsonify({
    #             "status": "skip",
    #             "reason": "last message from seller",
    #             "last_message": latest_message_text
    #         })

    # except Exception as e:
    #     print(f"Error reading latest message: {e}")
    #     return jsonify({"error": str(e)}), 500 
    # # 5  输入 message
    # try:
    #     input_box = WebDriverWait(driver, 20).until(
    #         EC.presence_of_element_located(
    #             (By.CSS_SELECTOR, "textarea.im-message-input-no-auto-height")
    #         )
    #     )

    #     print(f"Typing message: {message}")

    #     input_box.click()  # 先确保输入框获得焦点
    #     input_box.clear()
    #     input_box.send_keys(message)

    #     print("Message typed successfully")

    #     # 等待10秒（你提示的倒计时）
    #     print("10秒后将发送...")
    #     time.sleep(10)
    # except Exception as e:
    #     print(f"Error in inputing messages {e}")
    #     return jsonify({"error": str(e)}), 500

    # # 6 点击发送按钮
    # try:
    #     print("Trying to find send button...")

    #     send_btn = WebDriverWait(driver, 20).until(
    #         EC.element_to_be_clickable(
    #             (By.CSS_SELECTOR, "img.im-message-input-footer-right-send-icon")
    #         )
    #     )

    #     print("Send button found, clicking...")

    #     driver.execute_script("arguments[0].click();", send_btn)

    #     print("Message sent successfully")

    #     driver.execute_script("arguments[0].click();", send_btn)
    # except Exception as e:
    #     print(f"Error in sending messages {e}")
    #     return jsonify({"error": str(e)}), 500
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