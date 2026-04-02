from agent.rag.rag_reply import rag_reply
from models.driver import Driver
from constants.constant_values import  ELEMENT_LOADING_TIME, LOADING_TIME, SAFE_USERS
from models.web_scrapy_model import WebScrapyModel
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Dict
from utils.extract_user_info import extract_user_info
driver_model=Driver()

def remove_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)
def send_video(driver, video_name):
    try:
        import os

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        video_path = os.path.join(
            BASE_DIR,
            "knowledge_base",
            "mp4",
            video_name
        )

        print(f"[send_video] path: {video_path}")

        # 🔥 每次都重新找 input（关键）
        file_input = WebDriverWait(driver, ELEMENT_LOADING_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='file']")
            )
        )

        file_input.send_keys(video_path)

        print("[send_video] success")
        return True

    except Exception as e:
        print("[send_video] error:", e)
        return False

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
                
def clean_message(text: str) -> str:
    if not text:
        return ""

    # 常见翻译标识
    remove_phrases = [
        "by Alibaba Auto Translation",
        "由阿里AI翻译",
        "Translated by Alibaba",
        "Auto Translation"
    ]

    for phrase in remove_phrases:
        text = text.replace(phrase, "")

    return text.strip()

def listen_chat(driver, socketio, channel_id):

    print("[listen_chat] Start multi-user listener")

    web_model = WebScrapyModel(driver)

    last_count_map = {}
    current_user = None  

    while True:
        try:

            # ✅🔥 放在这里（第一行）
            if not driver.session_id:
                print("❌ driver 已断开，停止监听")
                break
            sessions = driver.find_elements(By.CSS_SELECTOR, "div.im-session-item")
            if not sessions:
                time.sleep(1)
                print("No sessions found")
                continue
            current_user=traverse_sessions(sessions=sessions, driver=driver, last_count_map=last_count_map, 
                              socketio=socketio, channel_id=channel_id,current_user=current_user, web_model=web_model)
            

        except Exception as e:
            print("[listen_chat] main error:", e)
            time.sleep(1)
        finally: 

            time.sleep(1)
        
def traverse_sessions(sessions, driver, last_count_map:Dict[str, int], 
                      socketio, channel_id:str, current_user, web_model:WebScrapyModel)->str:
    for s in sessions:
        try:
            # 👉 滚动
            driver.execute_script("arguments[0].scrollIntoView()", s)
            time.sleep(0.2)

                    # 👉 先拿名字
            try:
                name = s.find_element(
                    By.CSS_SELECTOR,
                    "div.im-session-item-name-content b"
                ).text.strip()
            except Exception as e:
                print(f"Error in fetching user's name:{e}")
                continue

            print(f"[fetch users] name:{name}")
            # 👉 防重复点击
            if current_user != name:
                driver.execute_script("arguments[0].click()", s)
                time.sleep(0.5)
                current_user = name

                    # 👉 获取用户信息
            user_name, star, country, remark, orders, order_status, \
                    order_status_code, order_id, order_creation_date = extract_user_info(web_scrapy_model=web_model)

            if not user_name:
                        continue

            print(f"\n👤 user: {user_name}")
            if user_name not in SAFE_USERS:
                print("Not safe Users")
                continue

            # 👉 获取消息
            messages = driver.find_elements(By.CSS_SELECTOR, "div.im-message-item")
            count = len(messages)
            print(f"[listen_chat] length of new message is {count}")
            if not messages:
                continue

            # ✅ 新用户 → 跳过历史消息
            if user_name not in last_count_map:

                last_seller_index = 0

                for i in range(len(messages) - 1, -1, -1):
                    cls = messages[i].get_attribute("class")

                    if "self" in cls:   # seller
                        last_seller_index = i + 1
                        break

                last_count_map[user_name] = last_seller_index

                print(f"[INIT] Start from last seller index: {last_seller_index}")
                continue

            # ✅ 没新消息 → 跳过
            if count <= last_count_map[user_name]:
                print("Skip for no new message")
                continue

            # ✅ 获取新消息
            new_messages = messages[last_count_map[user_name]:]

            buyer_texts = []

            for m in new_messages:
                text = clean_message(m.text.strip())
                cls = m.get_attribute("class")
                sender = "seller" if "self" in cls else "buyer"

                socketio.emit(
                    "chat_message",
                        {
                            "channelId": channel_id,
                            "sender": sender,
                            "message": text
                        }
                    )

                if sender == "buyer" and text:
                    buyer_texts.append(text)

            # ✅ 合并消息回复
            if buyer_texts:
                combined_text = " ".join(buyer_texts)

                print(f"🧠 Combined: {combined_text}")

                result = rag_reply(combined_text, user_name)

                send_message(driver, result["answer"])

                for img in result["jpg"]:
                    send_image(driver, img)

                for v in result["mp4"]:
                    send_video(driver, v)

                if result["alert"]:
                    socketio.emit("alert_message", {
                        "channelId": channel_id,
                        "alert": result["alert"]
                    })

            # ✅ 更新计数（必须在最后）
            last_count_map[user_name] = count

            time.sleep(0.3)
        except Exception as e:
            print("[listen_chat] user error:", e)
            raise
        return current_user