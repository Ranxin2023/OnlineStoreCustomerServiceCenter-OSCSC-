import os
import socket
from utils.constant_values import PROFILE_MAP, DEBUG_PORT
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# ─────────────────────────────────────────────────────
# Driver — 自动检测并启动 Chrome
# ─────────────────────────────────────────────────────

def is_chrome_reachable():
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
    
    def setup_chrome_driver(self, channel_id):
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

    def get_driver(self, channel_id, driver_pool):

        if channel_id not in driver_pool:
            print(f"Initializing driver for channel {channel_id}")
            driver_pool[channel_id] = self.setup_chrome_driver(channel_id)

        return driver_pool[channel_id]