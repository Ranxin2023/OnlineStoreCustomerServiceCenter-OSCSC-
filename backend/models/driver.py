import os
import socket
from constants.constant_values import PROFILE_MAP, DEBUG_PORT
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict, Optional 
# ─────────────────────────────────────────────────────
# Driver — 自动检测并启动 Chrome
# ─────────────────────────────────────────────────────

def is_chrome_reachable()->bool:
    """检查 Chrome 调试端口是否可连接"""
    try:
        s = socket.create_connection(("127.0.0.1", DEBUG_PORT), timeout=2)
        s.close()
        return True
    except OSError:
        return False

class Driver:
    def __init__(self):
        self.chrome_profile_dir = os.path.join(os.getcwd(), "chrome_profiles")
        os.makedirs(self.chrome_profile_dir, exist_ok=True)
        
    def is_driver_alive(self, driver)->bool:
        try:
            driver.current_url
            return True
        except Exception as e:
            print(f"[is_driver_alive]Driver is not alive:{e}")
            return False
            
    def get_driver(self, channel_id, driver_pool: Dict[str, Optional[WebDriver]])->WebDriver:

        if channel_id in driver_pool:

            driver = driver_pool[channel_id]

            if self.is_driver_alive(driver):
                return driver
            else:
                print(f"[driver] Driver dead, recreating for {channel_id}")
                try:
                    driver.quit()
                except Exception as e:
                    print(f"[get_driver]Exception in get driver is {e}")
                del driver_pool[channel_id]

        # 🔥 重新创建
        new_driver = self.setup_chrome_driver(channel_id=channel_id)

        driver_pool[channel_id] = new_driver

        return new_driver

    def setup_chrome_driver(self, channel_id:str)->WebDriver:
        profile_name = PROFILE_MAP.get(channel_id)

        if not profile_name:
            raise RuntimeError(f"Unknown channel id {channel_id}")

    
        profile_dir = os.path.join(self.chrome_profile_dir, profile_name)
        os.makedirs(profile_dir, exist_ok=True)

        options = Options()

        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # setup chrome driver
        driver = webdriver.Chrome(options=options)

        return driver

   