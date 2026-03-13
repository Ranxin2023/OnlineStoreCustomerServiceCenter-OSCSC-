
from flask import Blueprint, jsonify, request
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helper_functions.constant_values import SAFE_USERS, driver_pool
from helper_functions.driver import get_driver
import time
# driver = setup_driver()
chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat/open", methods=["POST", "OPTIONS"])
def open_chat():

    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.json

    channel_id = data.get("channelId")
    url = data.get("url")
    message = data.get("message")

    if not message:
        return jsonify({"error": "message is required"}), 400

    driver = get_driver(channel_id, driver_pool=driver_pool)

    try:

        # 1 打开聊天页面
        driver.get(url)

        # 2 等聊天列表加载
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

        # 3 点击聊天
        driver.execute_script(
            "arguments[0].click();",
            target_session
        )

        print(f"Opened chat with {target_name}")

        # 4 等输入框
        input_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "textarea.im-message-input-no-auto-height")
            )
        )

        # 5 输入 message
        print(f"Typing message: {message}")

        input_box.click()  # 先确保输入框获得焦点
        input_box.clear()
        input_box.send_keys(message)

        print("Message typed successfully")

        # 等待10秒（你提示的倒计时）
        print("10秒后将发送...")
        time.sleep(10)

        # 6 点击发送按钮
        print("Trying to find send button...")

        send_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "img.im-message-input-footer-right-send-icon")
            )
        )

        print("Send button found, clicking...")

        driver.execute_script("arguments[0].click();", send_btn)

        print("Message sent successfully")

        driver.execute_script("arguments[0].click();", send_btn)
        return jsonify({
            "status": "message typed",
            "user": target_name,
            "message": message
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500