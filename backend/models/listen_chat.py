from constants.constant_values import LOADING_TIME
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Optional
class ListenChat:
    def __init__(self, driver:Optional[WebDriver]):
        self.driver=driver

    def send_image(self, driver:Optional[WebDriver], image_name):
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