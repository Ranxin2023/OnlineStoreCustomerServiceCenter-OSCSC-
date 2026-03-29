from constants.constant_values import LOADING_TIME
from utils.translator_functions import translate_text, find_status_code
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from models.web_scrapy_model import WebScrapyModel
from typing import Optional, Tuple

def extract_user_info(web_scrapy_model:Optional[WebScrapyModel])->Tuple[str]:
    if not web_scrapy_model.driver_setup():
            print("[extract_user_info] Driver is not set up")
            return "", "", "", "", "", "", "", "", ""

    wait = WebDriverWait(web_scrapy_model.driver, LOADING_TIME)

    # ✅ 等页面核心区域加载（关键）
    try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-spm-anchor-id]")
                )
            )
    except Exception:
            print("[extract_user_info] page not fully loaded")

    name = ""
    star = ""
    country = ""
    remark = ""
    orders=""
    order_status=""
    order_status_en=""
    order_status_code=0
    order_id=""
    order_creation_date=""
    # ───── name: 直接用 class 精准定位 ─────
    # tag: <div class="user-name__3a8affc" data-spm-anchor-id="0.0.0.i3.xxx">
    try:
            name_el = web_scrapy_model.find_element_by_css_selector(
                web_scrapy_model.driver,
                "[class*='user-name__']"
            )
            name = name_el.text.strip()
            print(f"[extract_user_info][DEBUG][name] found via class: {name}")
    except Exception:
            # fallback: spm i3 兜底
            try:
                name_els = web_scrapy_model.find_elements_by_css_selector(
                    web_scrapy_model.driver, "[data-spm-anchor-id*='.i3.']"
                )
                for el in name_els:
                    text = el.text.strip()
                    if text:
                        name = text
                        print(f"[extract_user_info][DEBUG][name] found via spm fallback: {name}")
                        break
            except Exception as e:
                print(f"[extract_user_info] name error: {e}")
                name = ""

    # ───── star（更安全）─────
    try:
            print("[extract_user_info] Star fetching")
            star_els = web_scrapy_model.find_elements_by_css_selector(
                web_scrapy_model.driver,
                ".star-select__1676f39 .ait-select-selection-item span"
            )
            star = star_els[0].text.strip() if star_els else "No star tags"
    except Exception as e:
            print(f"[extract_user_info]Exception in finding star {e}")
            star = "No star tags"

       
    # ───── country ─────
    try:
            print("[extract_user_info] Country fetching")
            web_scrapy_model.wait_element_located(crawl_obj=web_scrapy_model.driver,tag="div[class*='info__'] div[class*='basic_'] div[class*='address__']")
            country_el = web_scrapy_model.find_element_by_css_selector(
                web_scrapy_model.driver,
                "div[class*='info__'] div[class*='basic_'] div[class*='address__']"
            )
            country = country_el.text.strip()
            print(f"[DEBUG][country] found via class: {country}")
    except Exception as e:
            # fallback: spm i4 兜底
            print(f"[extract_user_info] Country Exception:\n{e}")
            try:
                web_scrapy_model.wait_element_located(web_scrapy_model.driver, "[data-spm-anchor-id*='.i4.']")
                country_els = web_scrapy_model.find_elements_by_css_selector(
                    web_scrapy_model.driver, "[data-spm-anchor-id*='.i4.']"
                )
                country = ""
                for el in country_els:
                    text = el.text.strip()
                    if text:
                        country = text
                        print(f"[DEBUG][country] found via spm fallback: {country}")
                        break
            except Exception as e:
                print(f"[extract_user_info] country error: {e}")
                country = ""
    # ───── remark（更安全）─────
    try:
            remark_els = web_scrapy_model.find_elements_by_css_selector(
                web_scrapy_model.driver,
                ".remark-text__5bc353e"
            )
            remark = remark_els[0].text.strip() if remark_els else ""
    except Exception:
            remark = ""
    # ───── orders ─────
    try:
            # 有订单
            order_cards = web_scrapy_model.find_elements_by_css_selector(
                web_scrapy_model.driver,
                "div[class*='im-order-card']"
            )
            if order_cards:
                card = order_cards[0]  # 取第一个订单
                
                try:
                    order_status = web_scrapy_model.find_element_by_css_selector(
                        card, "span.im-order-card-status"
                    ).text.strip()
                except Exception:
                    pass
                
                try:
                    order_id = web_scrapy_model.find_element_by_css_selector(
                        card, "span.im-order-card-subtitle"
                    ).text.strip()
                except Exception:
                    pass
                
                try:
                    creation_els = web_scrapy_model.find_elements_by_css_selector(
                        card, "span.im-order-card-subtitle"
                    )
                    order_creation_date = creation_els[1].text.strip() if len(creation_els) > 1 else ""
                except Exception:
                    pass

                orders = f"{order_status} | {order_id} | {order_creation_date}"
                order_status_en=translate_text(orders)
                order_status_code=find_status_code(order_status_en)
                print(f"[DEBUG][orders] found: {orders}")
            else:
                # 没有订单
                orders = "No Orders"
                order_status_code=0
                print("[DEBUG][orders] No Orders")

    except Exception as e:
            print(f"[extract_user_info] orders error: {e}")
            orders = ""
    print(f"[user] name={name}, star={star}, country={country}, remark={remark} orders ={orders} ")

    return name, star, country, remark, orders, order_status, order_status_code,order_id, order_creation_date

