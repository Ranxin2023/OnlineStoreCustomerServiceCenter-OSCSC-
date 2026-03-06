import os
from helper_functions.constant_values import profile_map
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
def setup_driver(channel_id):
    profile_name = profile_map.get(channel_id)

    if not profile_name:
        raise RuntimeError(f"Unknown channel id {channel_id}")

    profile_root = os.path.join(os.getcwd(), "chrome_profiles")
    os.makedirs(profile_root, exist_ok=True)

    profile_dir = os.path.join(profile_root, profile_name)
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()

    # options.add_argument(f"--user-data-dir={profile_dir}")
    # options.add_argument("--disable-blink-features=AutomationControlled")
    options.binary_location = "/usr/bin/chromium"

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # driver = webdriver.Chrome(options=options)
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    return driver

def get_driver(channel_id, driver_pool):

    if channel_id not in driver_pool:
        print(f"Initializing driver for channel {channel_id}")
        driver_pool[channel_id] = setup_driver(channel_id)

    return driver_pool[channel_id]