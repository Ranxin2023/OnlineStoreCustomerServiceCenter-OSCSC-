from agent.rag.rag_reply import rag_reply
from models.driver import Driver
from constants.constant_values import  LOADING_TIME, SAFE_USERS
from models.web_scrapy_model import WebScrapyModel
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils.extract_user_info import extract_user_info
# from database.user_order_management import fetch_orders_by_username
driver_model=Driver()

def remove_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

def send_image(driver, image_name):
    try:
        import os

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        image_path = os.path.join(
            BASE_DIR,
            "knowledge_base",
            "images",
            image_name
        )

        print(f"[send_image] path: {image_path}")

        file_input = WebDriverWait(driver, LOADING_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='file']")
            )
        )

        file_input.send_keys(image_path)

        print("[send_image] success")
        return True

    except Exception as e:
        print("[send_image] error:", e)
        return False
    
def send_message(driver, reply):
    try:

        # 输入框
        input_box = WebDriverWait(driver, LOADING_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "textarea.im-message-input-no-auto-height")
            )
        )

        input_box.click()
        input_box.clear()
        input_box.send_keys(reply)

        # 发送按钮
        send_btn = WebDriverWait(driver, LOADING_TIME).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "img.im-message-input-footer-right-send-icon")
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            send_btn
        )

        print("Reply sent")
        return True
    except Exception as e:
        print("Reply error:", e)
        return False
                
# def listen_chat(driver, socketio, channel_id):
#     print("[listen_chat] waiting for messages to load...")

#     WebDriverWait(driver, PAGE_LOADING_TIME).until(
#         EC.presence_of_element_located(
#             (By.CSS_SELECTOR, "div.im-message-item")
#         )
#     )
#     print("[listen_chat]Start chat listener")
#     messages0 = driver.find_elements(
#         By.CSS_SELECTOR,
#         "div.im-message-item"
#     )
#     last_count = 0
#     # print(f"[listen_chat]Type of messages is {type(messages0)}")

#     for i in range(len(messages0) - 1, -1, -1):

#         m = messages0[i]

#         cls = m.get_attribute("class")

#         print(f"[listen_chat] cls is {cls}")

#         if "self" in cls:
#             last_count = i + 1
#             break

#     # print(f"[listen_chat]Last seller is{last_count}")

#     # round robin to fetch messages
#     while True:
#         messages = None
#         try:

#             messages = driver.find_elements(
#                 By.CSS_SELECTOR,
#                 "div.im-message-item"
#             )
#         except Exception as e:
#             print(f"[listener] Driver crashed: {e}")

#             try:
#                 driver.quit()
#             except Exception:
#                 pass

#             # 🔥 重新获取 driver
#             driver = driver_model.get_driver(channel_id, driver_pool)

#             print("[listener] Driver restarted")

#             time.sleep(3)
#             continue
           
#         count = len(messages)

#         if count <= last_count:
#             continue
        
#         new_messages = messages[last_count:]

#         for m in new_messages:

#             cls = m.get_attribute("class")

#             sender = "buyer"

#             if "self" in cls:
#                     sender = "seller"
#             message=None
#             text = m.text.strip()
#             if not text:
#                 try:
#                     img = m.find_element(By.CSS_SELECTOR, "img")
#                     img_url = img.get_attribute("src")

#                     message = {
#                             "type": "image",
#                             "content": img_url
#                         }

#                     print("📷 Image message:", img_url)

#                 except Exception as e:
#                     print(f"[listen_chat]Error in parsing images:{e}")
#                     message = {
#                         "type": "unknown",
#                         "content": ""
#                     }
#             else:
#                 message = {
#                         "type": "text",
#                         "content": text
#                     }

#                 print("💬 Text message:", text)
#                 # print(f"[listen_chat]New message:{text}")
#                 # print(f"[listen_chat]Type of the message is:{type(text)}")

#             socketio.emit(
#                 "chat_message",
#                 {
#                     "channelId": channel_id,
#                     "sender": sender,
#                     "message": text
#                 }
#             )
                
#             if sender != "buyer":
#                 continue

#             if message["type"] == "text":
#                 user_text = message["content"].lower().strip()
#                 print(f"[listen_chat] user text message is {user_text}")
#                 # ===== 图片测试指令 =====
#                 if user_text[0:6] in ['image1', 'image2', 'image3']:

#                     image_name = f"{user_text[0:6]}.jpg"   # image1 -> image1.jpg

#                     print(f"[listen_chat] Send test image: {image_name}")

#                     send_image(driver, image_name)

#                     continue  # ❗不要再走后面的回复逻辑

#                 # ===== 正常回复 =====
            
#                 reply = rag_reply(message["content"])
#                 reply = remove_non_bmp(reply)

#                 success=send_message(driver, reply)
#                 if not success:
#                     print("[listen_chat] Failed to send message, skip...")
#                     continue
#             elif message["type"] == "image":
#                 reply = "Thanks for the image. Could you please describe the issue?"

#             else:
#                 reply = "Let me check this for you."

#             print("[listen_chat] Replying:", reply)

            
                
#             last_count = count

#         time.sleep(SWITCHING_TIME)


def listen_chat(driver, socketio, channel_id):

    print("[listen_chat] Start multi-user listener")

    web_model = WebScrapyModel(driver)

    # 🔥 防止重复回复
    last_message_map = {}

    while True:

        try:
            sessions = driver.find_elements(By.CSS_SELECTOR, "div.im-session-item")

            for s in sessions:

                try:
                    # 👉 滚动到用户
                    driver.execute_script("arguments[0].scrollIntoView()", s)
                    time.sleep(0.3)

                    # 👉 点击用户
                    driver.execute_script("arguments[0].click()", s)
                    time.sleep(1)

                    # 👉 获取用户信息
                    user_name, star, country, remark, orders, order_status, \
                order_status_code ,order_id, order_creation_date = extract_user_info(web_scrapy_model=web_model)

                    if not user_name:
                        continue

                    print(f"\n👤 user: {user_name}")

                    # 👉 获取消息
                    messages = driver.find_elements(By.CSS_SELECTOR, "div.im-message-item")

                    if not messages:
                        continue

                    last = messages[-1]
                    text = last.text.strip()
                    cls = last.get_attribute("class")

                    sender = "seller" if "self" in cls else "buyer"
                    socketio.emit(
                            "chat_message",
                            {
                                "channelId": channel_id,
                                "sender": sender,
                                "message": text
                            }
                        )
                    if sender != "buyer" or not text:
                        continue

                    print(f"💬 {user_name}: {text}")
                    if user_name not in SAFE_USERS:
                        continue
                    # 🔥 去重（关键）
                    if user_name in last_message_map and last_message_map[user_name] == text:
                        continue

                    last_message_map[user_name] = text

                    # 🔥 AI回复
                    result = rag_reply(text, user_name)

                    print(f"🤖 Reply from listening chat:\n {result}")
                    # 1️⃣ 文本
                    send_message(driver, result["answer"])

                    # 2️⃣ 图片
                    for img in result["jpg"]:
                        send_image(driver, img)

                    # 3️⃣ 视频
                    for v in result["mp4"]:
                        send_image(driver, v)

                    # 4️⃣ alert
                    if result["alert"]:
                        socketio.emit("alert_message", {
                            "channelId": channel_id,
                            "alert": result["alert"]
                        })
                    # send_message(driver, reply)

                    time.sleep(0.5)

                except Exception as e:
                    print("[listen_chat] user error:", e)
                    continue

        except Exception as e:
            print("[listen_chat] main error:", e)
            return {
                "answer": "Let me check this for you.",
                "jpg": [],
                "mp4": [],
                "alert": ""
            }
        time.sleep(3)
        
def listen_chat_with_user(driver, socketio, channel_id, user_name):

    print(f"[chat] Start listener for user: {user_name}")

    last_count = 0

    while True:

        try:
            messages = driver.find_elements(By.CSS_SELECTOR, "div.im-message-item")
            count = len(messages)

            if count <= last_count:
                time.sleep(2)
                continue

            new_messages = messages[last_count:]

            for m in new_messages:

                cls = m.get_attribute("class")
                sender = "seller" if "self" in cls else "buyer"

                text = m.text.strip()

                if not text:
                    continue

                print(f"[chat] {sender}: {text}")

                # =========================
                # 🔥 只处理 buyer 消息
                # =========================
                if sender != "buyer":
                    continue

                # =========================
                # 🔥 生成回复（升级版）
                # =========================
                reply = rag_reply(query=messages["content"], user_name=user_name)

                send_message(driver, reply)

            last_count = count

        except Exception as e:
            print("[chat] error:", e)

        time.sleep(2)
