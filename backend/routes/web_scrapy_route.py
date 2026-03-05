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

from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, send_file
from models.web_scrapy_model import WebScrapyModel
from utils.scrape_order_helper import  save_orders_to_xlsx, get_driver
from utils.web_scrape_constant_values import profile_map
import os
import re

load_dotenv()

web_scrapy_bp = Blueprint("web_scrapy", __name__)

# ── constant variables ──────────────────────────────────────────────

PAGE_DELAY       = 3    # 翻页等待秒数
CHROME_PATH      = os.getenv("CHROME_PATH")
DEBUG_PORT       = os.getenv("DEBUG_PORT")
LOADING_TIME = 15

# ── setup driver ──────────────────────────────────────────────

web_scrapy_model=WebScrapyModel()

driver_pool = {}

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
    m = re.search(r"channelId=(\d+)", url)
    if m:
        channel_id = m.group(1)
    max_pages = data.get("max_pages", None)  # 可选，不传则抓全部

    print(f"Start scraping: {url}, max_pages: {max_pages or 'ALL'}")

    driver = get_driver(channel_id, driver_pool=driver_pool)
    web_scrapy_model.driver=driver
    try:

        all_orders = web_scrapy_model.crawl_orders(
            url,
            max_pages=max_pages,
            channel_id=channel_id
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

    if not all_orders:
        return jsonify({"error": "No orders scraped"}), 400
    store=profile_map.get(channel_id, "unknown")
    xlsx_path, xlsx_name = save_orders_to_xlsx(all_orders, store=store)
    print(f"File saved: {xlsx_path}")

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
    print(f"chanel id is{channel_id}")
    try:
        get_driver(channel_id, driver_pool)

        return jsonify({
            "message": f"Driver for channel {channel_id} initialized"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @web_scrapy_bp.route("/api/web-scrapy/scrape-detail", methods=["POST", "OPTIONS"])
# def scrape_order_detail():
#     """
#     单条订单详情调试接口
#     POST { "url": "https://csp.aliexpress.com/m_apps/order-manage/orderDetail?orderId=xxx&channelId=xxx" }
#     返回 JSON，包含收货信息 + 调试用的页面元素列表
#     """
#     if request.method == "OPTIONS":
#         return jsonify({"ok": True}), 200

#     data = request.get_json()
#     url  = data.get("url")
#     # handle not get url error
#     if not url:
#         return jsonify({"error": "URL is required"}), 400
    
#     m = re.search(r"channelId=(\d+)", url)
#     channel_id = m.group(1) if m else None

#     if not channel_id:
#         return jsonify({"error": "channelId not found"}), 400
    

#     print(f"[detail] 开始抓单条详情: {url}")

#     if web_scrapy_model.driver is None: 
#         return jsonify({"error": "Cannot setup driver"}), 503

#     try:
#         driver.get(url)

#         # 等待地址区域加载
#         try:
#             WebDriverWait(driver, 15).until(
#                 EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, "div[class*='orderInfo--addressItem']")
#                 )
#             )
#         except Exception:
#             return jsonify({"error": "页面加载超时，地址区域未出现，请确认已登录速卖通"}), 504

#         # ── 收集地址区域所有元素，返回给前端用于定位按钮 ──
#         debug_elements = []
#         try:
#             container = driver.find_element(
#                 By.XPATH, "//*[contains(@class,'orderInfo--address')]"
#             )
#             for el in container.find_elements(By.XPATH, ".//*")[:50]:
#                 tag = el.tag_name
#                 cls = el.get_attribute("class") or ""
#                 txt = (el.text or "").strip()[:40]
#                 onclick = el.get_attribute("onclick") or ""
#                 if cls or txt:
#                     debug_elements.append({
#                         "tag": tag, "class": cls, "text": txt, "onclick": onclick
#                     })
#         except Exception as e:
#             debug_elements.append({"error": str(e)})

#         # ── 点击收货地址眼睛（用 data-spm i3 定位，避免误点买家名字旁的眼睛）──
#         clicked_by = None
#         try:
#             eye_els = driver.find_elements(By.CSS_SELECTOR, "i[class*='orderEye--eye']")
#             target = None
#             for el in eye_els:
#                 spm = el.get_attribute("data-spm-anchor-id") or ""
#                 if ".i3." in spm:
#                     target = el
#                     break
#             if target is None and eye_els:
#                 target = eye_els[-1]
#             if target:
#                 driver.execute_script("arguments[0].click();", target)
#                 clicked_by = "orderEye--eye[data-spm=i3]"
#                 print("    OK 点击收货地址眼睛")
#                 time.sleep(1)
#             else:
#                 print("    WARN 未找到眼睛按钮")
#         except Exception as e:
#             print(f"    WARN 点击眼睛失败: {e}")

#         # ── 等收件人脱敏 ──
#         unmasked = False
#         def recipient_unmasked(d):
#             items = d.find_elements(By.CSS_SELECTOR, "div[class*='orderInfo--addressItem']")
#             for item in items:
#                 try:
#                     label = item.find_element(By.CSS_SELECTOR, "span[class*='addressLabel']").text.strip()
#                     if "收件人名称" in label:
#                         value = item.find_element(By.CSS_SELECTOR, "span[class*='addressValue']").text.strip()
#                         return "*" not in value and value != ""
#                 except Exception:
#                     pass
#             return False

#         try:
#             WebDriverWait(driver, 30).until(recipient_unmasked)
#             print("    OK 收件人已脱敏")
#         except Exception:
#             # 等待超时就兜底等 2 秒再读，避免空结果
#             print("    WARN 等待收件人脱敏超时，延迟2秒后继续")
#             time.sleep(3)


#         # ── 读取地址字段 ──
#         result = {
#             'recipient': '', 'address': '', 'postal_code': '',
#             'email': '', 'phone': '', 'tax_number': ''
#         }
#         address_items = driver.find_elements(By.CSS_SELECTOR, "div[class*='orderInfo--addressItem']")
#         for item in address_items:
#             try:
#                 label = item.find_element(By.CSS_SELECTOR, "span[class*='addressLabel']").text.strip()
#                 value = item.find_element(By.CSS_SELECTOR, "span[class*='addressValue']").text.strip()
#                 if "收件人名称" in label:
#                     result['recipient'] = value
#                 elif "详细地址" in label:
#                     result['address'] = value
#                 elif "邮编" in label:
#                     result['postal_code'] = value
#                 elif "联系邮件" in label:
#                     result['email'] = value
#                 elif "联系电话" in label:
#                     result['phone'] = value
#                 elif "Tax" in label:
#                     result['tax_number'] = value
#             except Exception:
#                 continue
#         print(f"recipient: {result['recipient']}")
#         print(f"address: {result['address']}")
#         print(f"postal_code: {result['postal_code']}")
#         print(f"email: {result['email']}")
#         print(f"phone: {result['phone']}")
#         print(f"tax_number: {result['tax_number']}")
        
#         return jsonify({
#             "data":           result,
#             "unmasked":       unmasked,
#             "clicked_by":     clicked_by,
#             "debug_elements": debug_elements,   # 用这个找正确的按钮 selector
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
