import os
import time
import csv
import uuid
from urllib.parse import urljoin, urlparse, parse_qs

from flask import Blueprint, request, jsonify, send_file
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


web_scrapy_bp = Blueprint("web_scrapy", __name__)

WAITING_TIME = 30
BASE_URL = "https://csp.aliexpress.com"


# -----------------------------
# Utils
# -----------------------------

def save_orders_to_csv(orders):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(base_dir, "..", "downloads")
    os.makedirs(download_dir, exist_ok=True)

    filename = f"orders_{uuid.uuid4().hex}.csv"
    filepath = os.path.join(download_dir, filename)

    fieldnames = [
        "order_id",
        "order_date",
        "order_status",
        "buyer",
        "shipping_no",
        "amount_paid",
        "payment_time",
        "detail_url",
    ]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for o in orders:
            writer.writerow(o)

    return filepath, filename


def setup_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )


def wait_for_order_list_page(driver):
    WebDriverWait(driver, WAITING_TIME).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a[href*='orderDetail']")
        )
    )
    print("✅ Order list loaded")


def open_detail_in_new_tab(driver, link_element):
    original_window = driver.current_window_handle
    existing_windows = driver.window_handles

    link_element.click()

    WebDriverWait(driver, WAITING_TIME).until(
        lambda d: len(d.window_handles) > len(existing_windows)
    )

    new_window = [w for w in driver.window_handles if w not in existing_windows][0]
    driver.switch_to.window(new_window)

    return original_window


# -----------------------------
# Scrape detail page (SECOND PAGE)
# -----------------------------

def scrape_order_detail_page(driver):
    WebDriverWait(driver, WAITING_TIME).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'订单详情')]")
        )
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")

    def v(label):
        el = soup.find("span", string=lambda x: x and label in x)
        if not el:
            return ""
        return el.find_next("span").get_text(strip=True)

    return {
        "order_id": "'" + v("订单号"),
        "order_status": v("订单状态"),
        "shipping_no": v("实际发货单号"),
        "detail_url": driver.current_url,
    }


# -----------------------------
# Main crawler
# -----------------------------

def crawl_orders_page(order_list_url):
    driver = setup_driver()

    print("🌐 Opening order list page")
    driver.get(order_list_url)

    print("🔐 Please login manually...")
    time.sleep(30)

    print("🔁 Re-opening order list page after login")
    driver.get(order_list_url)

    wait_for_order_list_page(driver)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    detail_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "orderDetail" not in href:
            continue

        full_url = urljoin(BASE_URL, href)
        parsed = urlparse(full_url)
        params = parse_qs(parsed.query)

        if "orderId" not in params:
            continue

        # 强制 desktop
        full_url = full_url.replace("/m_apps/", "/")
        detail_links.append(full_url)

    detail_links = list(dict.fromkeys(detail_links))

    print(f"🔗 Found {len(detail_links)} order detail links")
    for link in detail_links:
        print("   ", link)

    orders = []

    link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='orderDetail']")

    for idx, link_el in enumerate(link_elements, start=1):
        print(f"\n➡️ [{idx}/{len(link_elements)}] Opening order detail: {link_el}")

        original_window = open_detail_in_new_tab(driver, link_el)

        try:
            order_data = scrape_order_detail_page(driver)
            orders.append(order_data)
            print(f"   ✅ Scraped order {order_data['order_id']}")

        except Exception as e:
            print("   ❌ Failed to scrape detail:", e)

        finally:
            driver.close()
            driver.switch_to.window(original_window)

    driver.quit()
    return orders


# -----------------------------
# Flask route
# -----------------------------

@web_scrapy_bp.route("/api/web-scrapy/scrape", methods=["POST", "OPTIONS"])
def scrape_web_page():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    print(f"🚀 Start scraping: {url}")

    orders = crawl_orders_page(url)

    if not orders:
        return jsonify({"error": "No orders scraped"}), 400

    csv_path, csv_name = save_orders_to_csv(orders)

    print(f"📁 CSV saved: {csv_path}")

    return send_file(
        csv_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=csv_name
    )
