
from constants.constant_values import SAFE_USERS, LOADING_TIME, driver_pool
from database.user_management import save_or_update_user
from flask import Blueprint, jsonify, request
from models.driver import Driver
from models.web_scrapy_model import WebScrapyModel
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sockets.socket_bp import socketio
from utils.listening_chat import listen_chat
import threading
import time

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

# # fetch all user's info
# ----------------------------------first version of chat users-----------------------------------
# @chat_bp.route("/api/chat/users", methods=["POST", "OPTIONS"])
# def fetch_users():

#     if request.method == "OPTIONS":
#         return jsonify({"ok": True}), 200

#     data = request.json
#     channel_id = data.get("channelId")
#     url = data.get("url")

#     if not url:
#         return jsonify({"error": "url is required"}), 400

#     # 1️⃣ driver
#     driver=None
#     try:
#         driver = driver_model.get_driver(channel_id, driver_pool=driver_pool)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     driver.get(url)

#     # 2️⃣ 等 session
#     WebDriverWait(driver, LOADING_TIME).until(
#         EC.presence_of_element_located(
#             (By.CSS_SELECTOR, "div.im-session-item")
#         )
#     )

#     sessions = driver.find_elements(
#         By.CSS_SELECTOR,
#         "div.im-session-item"
#     )

#     users = []

#     web_scrapy_model = WebScrapyModel()
#     web_scrapy_model.driver=driver
#     print(f"[fetch_users] total sessions: {len(sessions)}")

#     # 3️⃣ 遍历所有用户（核心）
#     for i, s in enumerate(sessions):

#         try:
#             print(f"[fetch_users] processing user {i+1}")

#             # 点击用户
#             driver.execute_script("arguments[0].click();", s)

#             # 等聊天加载
#             # WebDriverWait(driver, LOADING_TIME).until(
#             #     EC.presence_of_element_located(
#             #         (By.CSS_SELECTOR, "div.im-message-item")
#             #     )
#             # )
#             WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, "[data-spm-anchor-id*='.i3.']")
#                 )
#             )
#             time.sleep(1)  # 防止 UI 未刷新完成

#             # ⭐ 用你已有函数
#             user_name, star, country, remark = web_scrapy_model.extract_user_info()
#             print(f"[fetch_users] user_name: {user_name}, star: {star}, country: {country}, remark: {remark}")
#             users.append({
#                 "name": user_name,
#                 "star": star,
#                 "country": country,
#                 "remark": remark
#             })
#             messages = driver.find_elements(By.CSS_SELECTOR, "div.im-message-item")

#             latest_message_text = ""
#             latest_sender = ""

#             if messages:
#                 last = messages[-1]

#                 latest_message_text = last.text.strip()
#                 cls = last.get_attribute("class")

#                 if "self" in cls:
#                     latest_sender = "seller"
#                 else:
#                     latest_sender = "buyer"
#             save_or_update_user(
#                 channel_id,
#                 user_name,
#                 star,
#                 country,
#                 remark,
#                 latest_message_text,
#                 latest_sender
#             )
#             print(f"[fetch_users] got: {user_name}")

#         except Exception as e:
#             print(f"[fetch_users] skip error: {e}")
#             continue

#     return jsonify({
#         "users": users
#     })

# ----------------------------------gpt refined version of chat users-----------------------------------
# @chat_bp.route("/api/chat/users", methods=["POST", "OPTIONS"])
# def fetch_users():

#     if request.method == "OPTIONS":
#         return jsonify({"ok": True}), 200

#     data = request.json
#     channel_id = data.get("channelId")
#     url = data.get("url")

#     if not url:
#         return jsonify({"error": "url is required"}), 400

#     # ───── 1. 获取 driver ─────
#     try:
#         driver = driver_model.get_driver(channel_id, driver_pool=driver_pool)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     driver.get(url)

#     # ───── 2. 等 session 列表加载 ─────
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located(
#             (By.CSS_SELECTOR, "div.im-session-item")
#         )
#     )

#     users = []
#     processed_users = set()

#     web_scrapy_model = WebScrapyModel()
#     web_scrapy_model.driver = driver

   
#     print("[fetch_users] start...")

#     # ───── 3. 核心循环（稳定版）─────
#     while True:

#         sessions = driver.find_elements(By.CSS_SELECTOR, "div.im-session-item")

#         new_found = False

#         for s in sessions:
#             try:
#                 # 👉 获取左侧用户名字（用于去重）
#                 name = s.text.strip()

#                 if not name or name in processed_users:
#                     continue

#                 print(f"[fetch_users] processing: {name}")

#                 processed_users.add(name)

#                 # ───── 滚动到可见 ─────
#                 driver.execute_script(
#                     "arguments[0].scrollIntoView({block: 'center'});",
#                     s
#                 )
#                 time.sleep(0.4)
#             except Exception as e:
#                 print(f"[fetch_users] skip error: {e}")
#                 continue

#             # ───── 获取当前右侧用户（用于判断切换）─────
#             old_name = ""
#             try:
#                 old_name = driver.find_element(
#                         By.CSS_SELECTOR,
#                         "[data-spm-anchor-id*='.i3.']"
#                     ).text.strip()
#             except Exception as e:
#                 print(f"[fetch_users] Error in fetching old name:{e}")
#                 continue

#                 # ───── 点击（真实点击）─────
#             try:
#                 ActionChains(driver).move_to_element(s).pause(0.2).click().perform()

#                 # ───── 等待用户切换（关键）─────
#                 WebDriverWait(driver, 5).until(
#                     lambda d: d.find_element(
#                         By.CSS_SELECTOR,
#                         "[data-spm-anchor-id*='.i3.']"
#                     ).text.strip() != old_name
#                 )

#                 time.sleep(0.5)
#             except Exception as e:
            
#                 print(f"[fetch_users] Error in clicking users: {e}")
#                 continue

#             # ───── 获取用户信息 ─────
#             user_name, star, country, remark = web_scrapy_model.extract_user_info()

#             print(f"[fetch_users] got: {user_name}, {country}")

#             users.append({
#                     "name": user_name,
#                     "star": star,
#                     "country": country,
#                     "remark": remark
#                 })

#             new_found = True

#         # ───── 没新用户 → 结束 ─────
#         if not new_found:
#             break

#     print(f"[fetch_users] finished, total users: {len(users)}")

#     return jsonify({
#         "users": users
#     })

# ----------------------------------claude refined version of chat users-----------------------------------
@chat_bp.route("/api/chat/users", methods=["POST", "OPTIONS"])
def fetch_users():

    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.json
    channel_id = data.get("channelId")
    url = data.get("url")

    if not url:
        return jsonify({"error": "url is required"}), 400

    # ───── 1. 获取 driver ─────
    try:
        driver = driver_model.get_driver(channel_id, driver_pool=driver_pool)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    driver.get(url)

    # ───── 2. 等 session 列表加载 ─────
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.im-session-item")
        )
    )

    users = []
    processed_users = set()

    web_scrapy_model = WebScrapyModel()
    web_scrapy_model.driver = driver

   
    print("[fetch_users] start...")

    # ───── 3. 核心循环（稳定版）─────
    while True:

        sessions = driver.find_elements(By.CSS_SELECTOR, "div.im-session-item")

        new_found = False

        for s in sessions:
            try:
                # 左侧列表项用户名: <b data-spm-anchor-id="0.0.0.i8.xxx">sean potts</b>
                name_el = s.find_element(By.CSS_SELECTOR, ".im-session-item-name-content b")
                name = name_el.text.strip()

                if not name or name in processed_users:
                    continue

                print(f"[fetch_users] processing: {name}")
                processed_users.add(name)

                # ───── 滚动到可见 ─────
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    s
                )
                time.sleep(0.4)
            except Exception as e:
                print(f"[fetch_users] skip error: {e}")
                continue

            # ───── 获取当前右侧面板用户名快照（判断切换用）─────
            # 右侧面板 selector: [class*='user-name__']
            # 左侧列表 selector: .im-session-item-name-content b  ← 完全不同！
            old_name = ""
            try:
                old_name = driver.find_element(
                    By.CSS_SELECTOR,
                    "[class*='user-name__']"
                ).text.strip()
                print(f"[fetch_users] old_name (right panel): '{old_name}'")
            except Exception:
                print("[fetch_users] old_name not found, likely first user")

            # ───── 点击 + 等右侧面板切换（带重试）─────
            click_ok = False
            for attempt in range(2):
                try:
                    driver.execute_script("arguments[0].click();", s)
                    time.sleep(0.5)

                    _captured = old_name
                    if _captured:
                        # 等右侧面板 user-name 变成不同的值
                        WebDriverWait(driver, 8).until(
                            lambda d, _o=_captured: d.find_element(
                                By.CSS_SELECTOR,
                                "[class*='user-name__']"
                            ).text.strip() != _o
                        )
                    else:
                        # 第一个用户：右侧面板首次出现 user-name
                        WebDriverWait(driver, 8).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "[class*='user-name__']")
                            )
                        )

                    time.sleep(0.5)
                    click_ok = True
                    print(f"[fetch_users] panel switched OK (attempt {attempt+1})")
                    break

                except Exception as e:
                    print(f"[fetch_users] click attempt {attempt+1} failed: {e}")
                    time.sleep(1)

            if not click_ok:
                print("[fetch_users] both click attempts failed, reading panel anyway...")

            # ───── 等右侧面板 user-name 稳定后读取 ─────
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[class*='user-name__']")
                    )
                )
            except Exception:
                pass
            user_name, star, country, remark = web_scrapy_model.extract_user_info()

            print(f"[fetch_users] got: {user_name}, {country}")
            users.append({
                    "name": user_name,
                    "star": star,
                    "country": country,
                    "remark": remark
                })

            new_found = True
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
            save_or_update_user(
                channel_id,
                user_name,
                star,
                country,
                remark,
                latest_message_text,
                latest_sender
            )

        # ───── 没新用户 → 结束 ─────
        if not new_found:
            break

    print(f"[fetch_users] finished, total users: {len(users)}")

    return jsonify({
        "users": users
    })