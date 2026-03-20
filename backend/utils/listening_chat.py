from agent.handle_intent import generate_reply
from models.driver import Driver
from constants.constant_values import PAGE_LOADING_TIME, LOADING_TIME,SWITCHING_TIME, driver_pool
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
# def listen_chat(driver, socketio, channel_id):

#     last_message = None

#     print("Start chat listener...")

#     while True:

#         try:

#             messages = driver.find_elements(
#                 By.CSS_SELECTOR,
#                 "div.im-message-item"
#             )

#             if not messages:
#                 time.sleep(2)
#                 continue

#             latest = messages[-1]

#             text = latest.text.strip()
#             cls = latest.get_attribute("class")

#             sender = "buyer"
#             if "self" in cls:
#                 sender = "seller"

#             # 防止重复推送
#             if text and text != last_message:

#                 print(f"New {sender} message: {text}")

#                 socketio.emit(
#                     "chat_message",
#                     {
#                         "channelId": channel_id,
#                         "sender": sender,
#                         "message": text
#                     }
#                 )

#                 last_message = text

#         except Exception as e:
#             print("Listener error:", e)

#         time.sleep(2)
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
                
def listen_chat(driver, socketio, channel_id):
    print("[listen_chat] waiting for messages to load...")

    WebDriverWait(driver, PAGE_LOADING_TIME).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.im-message-item")
        )
    )
    print("[listen_chat]Start chat listener")
    messages0 = driver.find_elements(
        By.CSS_SELECTOR,
        "div.im-message-item"
    )
    last_count = 0
    # print(f"[listen_chat]Type of messages is {type(messages0)}")

    for i in range(len(messages0) - 1, -1, -1):

        m = messages0[i]

        cls = m.get_attribute("class")

        print(f"[listen_chat] cls is {cls}")

        if "self" in cls:
            last_count = i + 1
            break

    # print(f"[listen_chat]Last seller is{last_count}")

    # round robin to fetch messages
    while True:
        messages = None
        try:

            messages = driver.find_elements(
                By.CSS_SELECTOR,
                "div.im-message-item"
            )
        except Exception as e:
            print(f"[listener] Driver crashed: {e}")

            try:
                driver.quit()
            except Exception:
                pass

            # 🔥 重新获取 driver
            driver = driver_model.get_driver(channel_id, driver_pool)

            print("[listener] Driver restarted")

            time.sleep(3)
            continue
           
        count = len(messages)

        if count <= last_count:
            continue
        
        new_messages = messages[last_count:]

        for m in new_messages:

            cls = m.get_attribute("class")

            sender = "buyer"

            if "self" in cls:
                    sender = "seller"
            message=None
            text = m.text.strip()
            if not text:
                try:
                    img = m.find_element(By.CSS_SELECTOR, "img")
                    img_url = img.get_attribute("src")

                    message = {
                            "type": "image",
                            "content": img_url
                        }

                    print("📷 Image message:", img_url)

                except Exception as e:
                    print(f"[listen_chat]Error in parsing images:{e}")
                    message = {
                        "type": "unknown",
                        "content": ""
                    }
            else:
                message = {
                        "type": "text",
                        "content": text
                    }

                print("💬 Text message:", text)
                # print(f"[listen_chat]New message:{text}")
                # print(f"[listen_chat]Type of the message is:{type(text)}")

            socketio.emit(
                "chat_message",
                {
                    "channelId": channel_id,
                    "sender": sender,
                    "message": text
                }
            )
                
            if sender != "buyer":
                continue

            if message["type"] == "text":
                user_text = message["content"].lower().strip()
                print(f"[listen_chat] user text message is {user_text}")
                # ===== 图片测试指令 =====
                if user_text[0:6] in ['image1', 'image2', 'image3']:

                    image_name = f"{user_text[0:6]}.jpg"   # image1 -> image1.jpg

                    print(f"[listen_chat] Send test image: {image_name}")

                    send_image(driver, image_name)

                    continue  # ❗不要再走后面的回复逻辑

                # ===== 正常回复 =====
                reply = generate_reply(message["content"])
                reply = remove_non_bmp(reply)

                success=send_message(driver, reply)
                if not success:
                    print("[listen_chat] Failed to send message, skip...")
                    continue
            elif message["type"] == "image":
                reply = "Thanks for the image. Could you please describe the issue?"

            else:
                reply = "Let me check this for you."

            print("[listen_chat] Replying:", reply)

            
                
            last_count = count

        

        time.sleep(SWITCHING_TIME)