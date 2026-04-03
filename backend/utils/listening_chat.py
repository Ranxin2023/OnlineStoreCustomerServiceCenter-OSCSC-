# from agent.rag.rag_reply import rag_reply
# from models.driver import Driver
# from constants.constant_values import  ELEMENT_LOADING_TIME, LOADING_TIME, SAFE_USERS
# from models.web_scrapy_model import WebScrapyModel
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# from typing import Dict
# from utils.extract_user_info import extract_user_info
# driver_model=Driver()

# def remove_non_bmp(text):
#     return ''.join(c for c in text if ord(c) <= 0xFFFF)

# def send_video(driver, video_name):
#     try:
#         import os
 
#         BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 
#         video_path = os.path.join(
#             BASE_DIR,
#             "knowledge_base",
#             "mp4",
#             video_name
#         )
 
#         print(f"[send_video] path: {video_path}")
 
#         # 🔥 每次都重新找 input（关键）
#         file_input = WebDriverWait(driver, ELEMENT_LOADING_TIME).until(
#             EC.presence_of_element_located(
#                 (By.CSS_SELECTOR, "input[type='file']")
#             )
#         )
 
#         # 记录发送前消息数量
#         before_count = len(driver.find_elements(By.CSS_SELECTOR, "div.im-message-item"))
 
#         file_input.send_keys(video_path)
 
#         # ✅ 等待视频消息真正出现在聊天里（最多 30 秒，视频上传较慢）
#         try:
#             WebDriverWait(driver, 30).until(
#                 lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.im-message-item")) > before_count
#             )
#         except Exception:
#             print("[send_video] warning: timeout waiting for message, sleeping 5s")
#             time.sleep(5)
 
#         print("[send_video] success")
#         return True
 
#     except Exception as e:
#         print("[send_video] error:", e)
#         return False
 
# def send_image(driver, image_name):
#     try:
#         import os
 
#         BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 
#         image_path = os.path.join(
#             BASE_DIR,
#             "knowledge_base",
#             "images",
#             image_name
#         )
 
#         print(f"[send_image] path: {image_path}")
 
#         file_input = WebDriverWait(driver, LOADING_TIME).until(
#             EC.presence_of_element_located(
#                 (By.CSS_SELECTOR, "input[type='file']")
#             )
#         )
 
#         # 记录发送前消息数量
#         before_count = len(driver.find_elements(By.CSS_SELECTOR, "div.im-message-item"))
 
#         file_input.send_keys(image_path)
 
#         # ✅ 等待图片消息真正出现在聊天里（最多 15 秒）
#         try:
#             WebDriverWait(driver, 15).until(
#                 lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.im-message-item")) > before_count
#             )
#         except Exception:
#             print("[send_image] warning: timeout waiting for message, sleeping 3s")
#             time.sleep(3)
 
#         print("[send_image] success")
#         return True
 
#     except Exception as e:
#         print("[send_image] error:", e)
#         return False
    
# def send_message(driver, reply):
#     try:

#         # 输入框
#         input_box = WebDriverWait(driver, LOADING_TIME).until(
#             EC.presence_of_element_located(
#                 (By.CSS_SELECTOR, "textarea.im-message-input-no-auto-height")
#             )
#         )

#         input_box.click()
#         input_box.clear()
#         input_box.send_keys(reply)

#         # 发送按钮
#         send_btn = WebDriverWait(driver, LOADING_TIME).until(
#             EC.element_to_be_clickable(
#                 (By.CSS_SELECTOR, "img.im-message-input-footer-right-send-icon")
#             )
#         )

#         driver.execute_script(
#             "arguments[0].click();",
#             send_btn
#         )

#         print("Reply sent")
#         return True
#     except Exception as e:
#         print("Reply error:", e)
#         return False
                
# def clean_message(text: str) -> str:
#     if not text:
#         return ""

#     # 常见翻译标识
#     remove_phrases = [
#         "by Alibaba Auto Translation",
#         "由阿里AI翻译",
#         "Translated by Alibaba",
#         "Auto Translation"
#     ]

#     for phrase in remove_phrases:
#         text = text.replace(phrase, "")

#     return text.strip()

# def listen_chat(driver, socketio, channel_id):

#     print("[listen_chat] Start multi-user listener")

#     web_model = WebScrapyModel(driver)

#     last_count_map = {}
#     current_user = None  

#     while True:
#         try:

#             # ✅🔥 放在这里（第一行）
#             if not driver.session_id:
#                 print("❌ driver 已断开，停止监听")
#                 break
#             sessions = driver.find_elements(By.CSS_SELECTOR, "div.im-session-item")
#             if not sessions:
#                 time.sleep(1)
#                 print("No sessions found")
#                 continue
#             current_user=traverse_sessions(sessions=sessions, driver=driver, last_count_map=last_count_map, 
#                               socketio=socketio, channel_id=channel_id,current_user=current_user, web_model=web_model)
            

#         except Exception as e:
#             print("[listen_chat] main error:", e)
#             time.sleep(1)
#         finally: 

#             time.sleep(1)
        
# def traverse_sessions(sessions, driver, last_count_map:Dict[str, int], 
#                       socketio, channel_id:str, current_user, web_model:WebScrapyModel)->str:
#     processed_users = set() 
#     for s in sessions:
#         try:
#             # 👉 滚动
#             driver.execute_script("arguments[0].scrollIntoView()", s)
#             time.sleep(0.2)

#                     # 👉 先拿名字
#             try:
#                 name = s.find_element(
#                     By.CSS_SELECTOR,
#                     "div.im-session-item-name-content b"
#                 ).text.strip()
#             except Exception as e:
#                 print(f"Error in fetching user's name:{e}")
#                 continue

#             print(f"[fetch users] name:{name}")
#             # 👉 防重复点击
#             if current_user != name:
#                 driver.execute_script("arguments[0].click()", s)
#                 time.sleep(0.5)
#                 current_user = name

#                     # 👉 获取用户信息
#             user_name, star, country, remark, orders, order_status, \
#                     order_status_code, order_id, order_creation_date = extract_user_info(web_scrapy_model=web_model)

#             if not user_name:
#                 print("No users found")
#                 continue
#             if user_name in processed_users:
#                 print("⛔ already processed this round")
#                 continue
#             print(f"\n👤 user: {user_name}")
#             if user_name not in SAFE_USERS:
#                 print("Not safe Users")
#                 continue

#             # 👉 获取消息
#             messages = driver.find_elements(By.CSS_SELECTOR, "div.im-message-item")
#             count = len(messages)
#             print(f"[listen_chat] length of new message is {count}")
#             if not messages:
#                 continue

#             # ✅ 新用户 → 跳过历史消息
#             if user_name not in last_count_map:

#                 last_seller_index = 0

#                 for i in range(len(messages) - 1, -1, -1):
#                     cls = messages[i].get_attribute("class")

#                     if "self" in cls:   # seller
#                         last_seller_index = i + 1
#                         break

#                 last_count_map[user_name] = last_seller_index

#                 print(f"[INIT] Start from last seller index: {last_seller_index}")
#                 continue

#             # ✅ 没新消息 → 跳过
#             if count <= last_count_map[user_name]:
#                 print("Skip for no new message")
#                 continue

#             # ✅ 获取新消息
#             new_messages = messages[last_count_map[user_name]:]

#             buyer_texts = []

#             for m in new_messages:
#                 text = clean_message(m.text.strip())
#                 cls = m.get_attribute("class")
#                 sender = "seller" if "self" in cls else "buyer"

#                 socketio.emit(
#                     "chat_message",
#                         {
#                             "channelId": channel_id,
#                             "sender": sender,
#                             "message": text
#                         }
#                     )

#                 if sender == "buyer" and text:
#                     buyer_texts.append(text)

#             # ✅ 更新计数
#             last_count_map[user_name] = count

#             # ✅ 合并消息回复
#             if buyer_texts:
#                 combined_text = " ".join(buyer_texts)

#                 print(f"🧠 Combined: {combined_text}")

#                 result = rag_reply(combined_text, user_name)

#                 processed_users.add(user_name)
#                 print(f"[traverse_sessions] jpg={result['jpg']}, mp4={result['mp4']}")
#                 send_message(driver, result["answer"])
#                 for img in result["jpg"]:
#                     send_image(driver, img)

#                 for v in result["mp4"]:
#                     send_video(driver, v)

#                 # ✅ 所有媒体发完后，等待 2 秒再切换到下一个用户
#                 time.sleep(2)
#                 print(f"[traverse_sessions] all media sent for {user_name}, moving to next")
#                 if result["alert"]:
#                     socketio.emit("alert_message", {
#                         "channelId": channel_id,
#                         "alert": result["alert"]
#                     })


#             time.sleep(0.3)
#         except Exception as e:
#             print("[listen_chat] user error:", e)
#             raise
#     return current_user



# -------------------------- claude revised -----------------------------------------------

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
 
        # 每次重新找 input，防止 stale element
        file_input = WebDriverWait(driver, ELEMENT_LOADING_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='file']")
            )
        )
 
        file_input.send_keys(video_path)
        file_input = None  # 立即释放，防止后续 stale reference
 
        # ✅ 视频上传期间用 keep-alive 防止 ChromeDriver session 超时断开
        # 每 3 秒发一次轻量命令（获取当前 URL），最多等 60 秒
        print("[send_video] waiting for upload, sending keep-alive to driver...")
        for i in range(20):  # 20 * 3s = 60s max
            time.sleep(3)
            try:
                _ = driver.current_url  # 轻量 keep-alive，不操作 DOM
                print(f"[send_video] keep-alive {i+1}/20")
            except Exception as ka_err:
                print(f"[send_video] keep-alive failed: {ka_err}")
                break
 
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

        # 每次重新找 input，防止 stale element
        file_input = WebDriverWait(driver, LOADING_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='file']")
            )
        )

        # 记录发送前消息数（不持有 DOM 引用）
        before_count = len(driver.find_elements(By.CSS_SELECTOR, "div.im-message-item"))

        file_input.send_keys(image_path)
        file_input = None  # 立即释放，防止后续 stale reference

        # 等待图片消息真正出现（最多 15 秒）
        try:
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.im-message-item")) > before_count
            )
            time.sleep(0.5)  # 等 UI 渲染稳定
        except Exception:
            print("[send_image] warning: timeout waiting for message, sleeping 3s")
            time.sleep(3)

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
    # ✅ Fix: processed_users 在 while 外创建，跨轮持久化
    # 用户有新消息时会自动从中移除，允许重新回复
    processed_users = set()

    while True:
        try:
            if not driver.session_id:
                print("❌ driver 已断开，停止监听")
                break
            sessions = driver.find_elements(By.CSS_SELECTOR, "div.im-session-item")
            if not sessions:
                time.sleep(1)
                print("No sessions found")
                continue
            current_user = traverse_sessions(
                sessions=sessions,
                driver=driver,
                last_count_map=last_count_map,
                socketio=socketio,
                channel_id=channel_id,
                current_user=current_user,
                web_model=web_model,
                processed_users=processed_users,
            )

        except Exception as e:
            print("[listen_chat] main error:", e)
            time.sleep(1)
        finally:
            time.sleep(1)

def traverse_sessions(sessions, driver, last_count_map: Dict[str, int],
                      socketio, channel_id: str, current_user, web_model: WebScrapyModel,
                      processed_users: set) -> str:
    """
    processed_users 由外层 listen_chat 传入持久保存。
    用户被回复后加入；检测到新消息时移除，允许再次回复。
    """
    for s in sessions:
        try:
            driver.execute_script("arguments[0].scrollIntoView()", s)
            time.sleep(0.2)

            try:
                name = s.find_element(
                    By.CSS_SELECTOR,
                    "div.im-session-item-name-content b"
                ).text.strip()
            except Exception as e:
                print(f"Error in fetching user's name:{e}")
                continue

            print(f"[fetch users] name:{name}")

            # 只有切换用户时才点击
            if current_user != name:
                driver.execute_script("arguments[0].click()", s)
                time.sleep(0.5)
                current_user = name

            user_name, star, country, remark, orders, order_status, \
                    order_status_code, order_id, order_creation_date = extract_user_info(web_scrapy_model=web_model)

            if not user_name:
                print("No users found")
                continue

            print(f"\n👤 user: {user_name}")

            if user_name not in SAFE_USERS:
                print("Not safe Users")
                continue

            messages = driver.find_elements(By.CSS_SELECTOR, "div.im-message-item")
            count = len(messages)
            print(f"[listen_chat] length of new message is {count}")
            if not messages:
                continue

            # 新用户 → 初始化基准，跳过本轮
            if user_name not in last_count_map:
                last_seller_index = 0
                for i in range(len(messages) - 1, -1, -1):
                    cls = messages[i].get_attribute("class")
                    if "self" in cls:
                        last_seller_index = i + 1
                        break
                last_count_map[user_name] = last_seller_index
                print(f"[INIT] Start from last seller index: {last_seller_index}, skip this round")
                continue

            # 没有新消息 → 跳过
            if count <= last_count_map[user_name]:
                print("Skip for no new message")
                continue

            # ✅ 有新消息 → 从 processed_users 移除，允许重新回复
            if user_name in processed_users:
                print(f"[traverse_sessions] new message from {user_name}, re-enabling reply")
                processed_users.discard(user_name)

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

            # 更新计数
            last_count_map[user_name] = count

            if buyer_texts:
                # ✅ Fix: 先标记再发送，防止同轮或下一轮重复触发
                processed_users.add(user_name)

                combined_text = " ".join(buyer_texts)
                print(f"🧠 Combined: {combined_text}")

                result = rag_reply(combined_text, user_name)

                send_message(driver, result["answer"])
                print(f"[traverse_sessions] jpg={result['jpg']}, mp4={result['mp4']}")

                for img in result["jpg"]:
                    send_image(driver, img)

                for v in result["mp4"]:
                    send_video(driver, v)

                # ✅ 所有媒体发完后等 2 秒再切换用户
                time.sleep(2)
                print(f"[traverse_sessions] all media sent for {user_name}, moving to next")

                if result["alert"]:
                    socketio.emit("alert_message", {
                        "channelId": channel_id,
                        "alert": result["alert"]
                    })

            time.sleep(0.3)

        except Exception as e:
            print("[listen_chat] user error:", e)
            raise

    return current_user