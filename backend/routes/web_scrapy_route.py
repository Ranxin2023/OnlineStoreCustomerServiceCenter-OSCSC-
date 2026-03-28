"""
web_scrapy_route.py
Flask 路由 — 速卖通订单抓取（完整移植自 aliexpress_scraper.py)

前端 POST /api/web-scrapy/scrape  { "url": "<订单列表URL>", "max_pages": 5 }
返回 xlsx 文件下载

使用方式：
  - 直接调用接口即可，后端会自动检测 Chrome 是否启动
  - 如果 Chrome 未启动，会自动拉起（复用 chrome-selenium profile，保留登录态）
  - 如果是第一次使用，需要先手动在弹出的 Chrome 中登录速卖通，再重试
"""

from constants.constant_values import driver_pool, PROFILE_MAP
from constants.order_headers import ORDER_HEADERS, ORDER_KEYS, COLUMN_WIDTHS
from dotenv import load_dotenv
from database.order_management import save_orders_to_db
from flask import Blueprint, request, jsonify, send_file
from models.web_scrapy_model import WebScrapyModel
from models.driver import Driver
from models.load_latest_files import LatestFetch
from utils.save_excel import  save_orders_to_xlsx
from utils.order_scrapy import crawl_orders
import re

load_dotenv()

web_scrapy_bp = Blueprint("web_scrapy", __name__)



# ──—————— model Definition ─────────────────────────────────


driver_model=Driver()


# ─────────────────────────────────────────────────────
# Flask 路由
# ─────────────────────────────────────────────────────

@web_scrapy_bp.route("/api/web-scrapy/scrape", methods=["POST", "OPTIONS"])
def scrape_web_page():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data      = request.get_json()
    url       = data.get("url")

    # No URL is given 
    if not url:
        return jsonify({"error": "URL is required"}), 400
    channel_id = None
    
    # parse the channel id
    m = re.search(r"channelId=(\d+)", url)
    if m:
        channel_id = m.group(1)
    max_pages = data.get("max_pages", None)  # 可选，不传则抓全部

    print(f"Start scraping: {url}, max_pages: {max_pages or 'ALL'}")

    driver = driver_model.get_driver(channel_id, driver_pool=driver_pool)
    web_scrapy_model=WebScrapyModel(driver=driver)
    all_orders=None
    try:
        # 1️. 爬订单
        all_orders = crawl_orders(
            web_scrapy_model=web_scrapy_model,
            order_list_url=url,
            max_pages=max_pages,
            channel_id=channel_id
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503
    
    print(f"[scrape_web_page]The length of all_orders is {len(all_orders)}")
    # for order in all_orders:
    #     print(f"{order}")
    
    if not all_orders:
        return jsonify({"error": "No orders scraped"}), 400
    store = PROFILE_MAP.get(channel_id, "unknown")
    
    # 2️. 保存数据库
    new_orders =save_orders_to_db(all_orders, store)

    # 3. 更新最新时间
    latest_fetch = LatestFetch()
    latest_fetch.update_latest_fetch(store)
    
    # 4.  保存Excel
    filename = f"order_list_{store}.xlsx"
    
    xlsx_path, xlsx_name = save_orders_to_xlsx(data=new_orders, filename=filename,data_keys=ORDER_KEYS,excel_headers=ORDER_HEADERS, col_widths=COLUMN_WIDTHS, mode='a')
    print(f"File saved to the path: {xlsx_path}")

    return send_file(
        xlsx_path,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=xlsx_name
    )

@web_scrapy_bp.route("/api/web-scrapy/setup-driver", methods=["POST"])
def setup_driver_route():

    data = request.get_json()
    channel_id = data.get("channelId")
    # print(f"chanel id is{channel_id}")
    try:
        driver_model.get_driver(channel_id, driver_pool)

        return jsonify({
            "message": f"Driver for channel {channel_id} initialized"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

