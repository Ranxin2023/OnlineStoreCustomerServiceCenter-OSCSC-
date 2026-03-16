from constants.constant_values import PAGE_LOADING_TIME, LOADING_TIME,SWITCHING_TIME
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from agent.handle_intent import generate_reply
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
def remove_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

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
    # print(f"[listen_chat] messages length = {len(messages0)}")

    for i in range(len(messages0) - 1, -1, -1):

        m = messages0[i]

        cls = m.get_attribute("class")

        print(f"[listen_chat] cls is {cls}")

        if "self" in cls:
            last_count = i + 1
            break

    # print(f"[listen_chat]Last seller is{last_count}")

    # round robin
    while True:

        try:

            messages = driver.find_elements(
                By.CSS_SELECTOR,
                "div.im-message-item"
            )

            print(f"[listen_chat] messages length in while True = {len(messages)}")
            count = len(messages)

            if count <= last_count:
                continue
            
            new_messages = messages[last_count:]

            for m in new_messages:

                text = m.text.strip()
                cls = m.get_attribute("class")

                sender = "buyer"

                if "self" in cls:
                    sender = "seller"

                print("New message:", text)


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

                reply = generate_reply(text)
                # print(f"[listen_chat]Intent is: {reply}")
                reply = remove_non_bmp(reply)
                print("[listen_chat] Replying:", reply)

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

                except Exception as e:
                            print("Reply error:", e)
                
                last_count = count

        except Exception as e:
            print("Listener error:", e)

        time.sleep(SWITCHING_TIME)