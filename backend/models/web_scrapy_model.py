from constants.constant_values import LOADING_TIME, ELEMENT_LOADING_TIME
# from datetime import datetime
from dotenv import load_dotenv
# from models.load_latest_files import LatestFetch
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from utils.translator_functions import translate_status
# from utils.contry_functions import get_country_from_order
import time
from typing import Optional
load_dotenv()

class WebScrapyModel:
    def __init__(self, driver:Optional[WebDriver]):
        self.driver=driver
        self.table_tag_id="table.next-table-row"
        self.address_tag_id="div[class*='orderInfo--addressItem']"
        self.tag_list = [
            ("order_id_el","span.header--valueHighLight--wCk3sLF", False), 
            ("time_el","span.header--value--E2HYUZn:not(.header--valueHighLight--wCk3sLF)", True), 
            ("buyer_el","a.buyerInfo--inline--U3y4fIR", False),
            ("product_el","span.productInfo--itemTitle--QshSnPH", False),
            ("sku_el","span.productInfo--skuCodeValue--FJA_1Ru", True),
            ("price_el","span.productInfo--unitFee--mVPKC9G", False),
            ("qty_el","td[data-next-table-col='3'] div", False),
            ("amount_el","div.amount--amount--YdsJokJ", False),
            ("status_el","div.chc-state-label__stateText", False),
            ("tag_el","span.chc-color-tag", True),
            ("btns","button.next-btn span.next-btn-helper", True),
            ("note_el","span.orderBasic--value--lMC4G8D", False)
        ]
        
    def driver_setup(self)->bool:
        return self.driver is not None
    
    def button_click(self, input_btn, value):
        input_btn.click()
        input_btn.send_keys(Keys.CONTROL + "a")
        input_btn.send_keys(value)
        input_btn.send_keys(Keys.ENTER)
        time.sleep(1)

    def wait_element_located(self, crawl_obj, tag:str, time=ELEMENT_LOADING_TIME):
        return WebDriverWait(crawl_obj, time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, tag))
        )

    def wait_elements_located(self, crawl_obj, tag:str, time=ELEMENT_LOADING_TIME):
        return WebDriverWait(crawl_obj, time).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, tag)
            )
        )
    
    def find_element_by_css_selector(self, crawl_obj, tag:str):
        return crawl_obj.find_element(By.CSS_SELECTOR, tag)
    
    def find_elements_by_css_selector(self, crawl_obj, tag:str):
        return crawl_obj.find_elements(By.CSS_SELECTOR, tag)
    
    def find_element_by_x_path(self, crawl_obj, tag, time=ELEMENT_LOADING_TIME):
       
        return WebDriverWait(crawl_obj, time).until(
            EC.presence_of_element_located(
                (By.XPATH, tag)
            )
        )
    
    def find_elements_by_x_path(self, crawl_obj, tag:str):
        return WebDriverWait(crawl_obj, time).until(
            EC.presence_of_elements_located(
                (By.XPATH, tag)
            )
        )
        
    def text_strip(self, text_el):
        return text_el.text.strip()

    def execute_script(self,execute_obj, execute_code:str):
        execute_obj.execute_script(execute_code)

  
    
    
    # def extract_user_info(self):
    #     if not self.driver_setup():
    #         print("[extract_user_info] Driver is not set up")
    #         return None
    #     wait = WebDriverWait(self.driver, LOADING_TIME)

    #     # ───── name ─────
    #     try:
    #         name_el = wait.until(
    #             EC.presence_of_element_located(
    #                 (By.CSS_SELECTOR, ".user-name__3a8affc")
    #             )
    #         )
    #         name = self.text_strip(name_el)
    #     except Exception:
    #         name = ""

    #     # ───── star ─────
    #     try:
    #         star_el=self.find_element_by_css_selector(self.driver, ".star-select__1676f39 .ait-select-selection-item span")
    #         star = star_el.text.strip()
    #     except Exception:
    #         star = "No star tags"

    #     # ───── country ─────
    #     try:
    #         country = ""

    #         els = self.find_elements_by_css_selector(
    #             self.driver,
    #             "span[data-spm-anchor-id]"
    #         )

    #         for el in els:
    #             spm = el.get_attribute("data-spm-anchor-id") or ""
    #             text = el.text.strip()

    #             print(f"[DEBUG] spm={spm}, text={text}")

    #             # ✅ 核心：只选 i4 区域（你说的那个）
    #             if ".i4." in spm:
    #                 country = text
    #                 break


    #     except Exception as e:
    #         print(f"Exception in country part is:{e}")
    #         country = ""

    #     # ───── remark ─────
    #     try:
    #         remark_el=self.find_element_by_css_selector(self.driver, ".remark-text__5bc353e")
    #         remark = remark_el.text.strip()
    #     except Exception:
    #         remark = ""

    #     print(f"[user] name={name}, star={star}, country={country}, remark={remark}")

    #     return name, star, country, remark

    # ---------------------------------- chatgpt refined version ----------------------------------
    # def extract_user_info(self):
    #     if not self.driver_setup():
    #         print("[extract_user_info] Driver is not set up")
    #         return "", "", "", ""

    #     wait = WebDriverWait(self.driver, LOADING_TIME)

    #     # ✅ 等页面核心区域加载（关键）
    #     try:
    #         wait.until(
    #             EC.presence_of_element_located(
    #                 (By.CSS_SELECTOR, "[data-spm-anchor-id]")
    #             )
    #         )
    #     except Exception:
    #         print("[extract_user_info] page not fully loaded")

    #     name = ""
    #     star = ""
    #     country = ""
    #     remark = ""

    #     # ───── name（用 i3）─────
    #     try:
    #         name_els = self.find_elements_by_css_selector(
    #             self.driver,
    #             "[data-spm-anchor-id]"
    #         )

    #         for el in name_els:
    #             spm = el.get_attribute("data-spm-anchor-id") or ""
    #             text = el.text.strip()

    #             # DEBUG
    #             print(f"[DEBUG][name] spm={spm}, text={text}")

    #             if spm.startswith("0.0.0.i3") and text:
    #                 name = text
    #                 break

    #     except Exception as e:
    #         print(f"[extract_user_info] name error: {e}")
    #         name = ""

    #     # ───── star（更安全）─────
    #     try:
    #         star_els = self.find_elements_by_css_selector(
    #             self.driver,
    #             ".star-select__1676f39 .ait-select-selection-item span"
    #         )
    #         star = star_els[0].text.strip() if star_els else "No star tags"
    #     except Exception:
    #         star = "No star tags"

    #     # ───── country（用 i4）─────
    #     try:
    #         country_els = self.find_elements_by_css_selector(
    #             self.driver,
    #             "span[data-spm-anchor-id]"
    #         )

    #         for el in country_els:
    #             spm = el.get_attribute("data-spm-anchor-id") or ""
    #             text = el.text.strip()

    #             print(f"[DEBUG][country] spm={spm}, text={text}")

    #             if spm.startswith("0.0.0.i4") and text:
    #                 country = text
    #                 break

    #     except Exception as e:
    #         print(f"[extract_user_info] country error: {e}")
    #         country = ""

    #     # ───── remark（更安全）─────
    #     try:
    #         remark_els = self.find_elements_by_css_selector(
    #             self.driver,
    #             ".remark-text__5bc353e"
    #         )
    #         remark = remark_els[0].text.strip() if remark_els else ""
    #     except Exception:
    #         remark = ""

    #     print(f"[user] name={name}, star={star}, country={country}, remark={remark}")

    #     return name, star, country, remark

    # ----------------------------------- claude changed version ----------------------------------- 
    def extract_user_info(self):
        if not self.driver_setup():
            print("[extract_user_info] Driver is not set up")
            return "", "", "", ""

        wait = WebDriverWait(self.driver, LOADING_TIME)

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

        # ───── name: 直接用 class 精准定位 ─────
        # tag: <div class="user-name__3a8affc" data-spm-anchor-id="0.0.0.i3.xxx">
        try:
            name_el = self.find_element_by_css_selector(
                self.driver,
                "[class*='user-name__']"
            )
            name = name_el.text.strip()
            print(f"[extract_user_info][DEBUG][name] found via class: {name}")
        except Exception:
            # fallback: spm i3 兜底
            try:
                name_els = self.find_elements_by_css_selector(
                    self.driver, "[data-spm-anchor-id*='.i3.']"
                )
                for el in name_els:
                    text = el.text.strip()
                    if text:
                        name = text
                        print(f"[DEBUG][name] found via spm fallback: {name}")
                        break
            except Exception as e:
                print(f"[extract_user_info] name error: {e}")
                name = ""

        # ───── star（更安全）─────
        try:
            print("[extract_user_info] Star fetching")
            star_els = self.find_elements_by_css_selector(
                self.driver,
                ".star-select__1676f39 .ait-select-selection-item span"
            )
            star = star_els[0].text.strip() if star_els else "No star tags"
        except Exception as e:
            print(f"[extract_user_info]Exception in finding star {e}")
            star = "No star tags"

        # # ───── country: span[data-spm-anchor-id*='.i2.'] ─────
        # # tag: <span data-spm-anchor-id="0.0.0.i2.4eed23f1EC2cgj">France</span>
        # try:
        #     country_el = self.find_element_by_css_selector(
        #         self.driver,
        #         "span[data-spm-anchor-id*='.i2.']"
        #     )
        #     country = country_el.text.strip()
        #     print(f"[DEBUG][country] found: {country}")
        # except Exception as e:
        #     print(f"[extract_user_info] country error: {e}")
        #     country = ""
        # ───── country: span[data-spm-anchor-id*='.i2.'] ─────
        # tag: <span data-spm-anchor-id="0.0.0.i2.4eed23f1EC2cgj">France</span>
        # 注意：部分用户没有填写国家，i2 元素不存在属于正常情况
        # ───── country ─────
        try:
            print("[extract_user_info] Country fetching")
            self.wait_element_located(crawl_obj=self.driver,tag="div[class*='info__'] div[class*='basic_'] div[class*='address__']")
            country_el = self.find_element_by_css_selector(
                self.driver,
                "div[class*='info__'] div[class*='basic_'] div[class*='address__']"
            )
            country = country_el.text.strip()
            print(f"[DEBUG][country] found via class: {country}")
        except Exception as e:
            # fallback: spm i4 兜底
            print(f"[extract_user_info] Country Exception:\n{e}")
            try:
                self.wait_element_located(self.driver, "[data-spm-anchor-id*='.i4.']")
                country_els = self.find_elements_by_css_selector(
                    self.driver, "[data-spm-anchor-id*='.i4.']"
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
            remark_els = self.find_elements_by_css_selector(
                self.driver,
                ".remark-text__5bc353e"
            )
            remark = remark_els[0].text.strip() if remark_els else ""
        except Exception:
            remark = ""
        # ───── orders ─────
        try:
            # 有订单
            order_cards = self.find_elements_by_css_selector(
                self.driver,
                "div[class*='im-order-card']"
            )
            if order_cards:
                card = order_cards[0]  # 取第一个订单
                
                status = ""
                order_id = ""
                creation = ""
                
                try:
                    status = self.find_element_by_css_selector(
                        card, "span.im-order-card-status"
                    ).text.strip()
                except Exception:
                    pass
                
                try:
                    order_id = self.find_element_by_css_selector(
                        card, "span.im-order-card-subtitle"
                    ).text.strip()
                except Exception:
                    pass
                
                try:
                    creation_els = self.find_elements_by_css_selector(
                        card, "span.im-order-card-subtitle"
                    )
                    creation = creation_els[1].text.strip() if len(creation_els) > 1 else ""
                except Exception:
                    pass

                orders = f"{status} | {order_id} | {creation}"
                print(f"[DEBUG][orders] found: {orders}")
            else:
                # 没有订单
                orders = "No Orders"
                print("[DEBUG][orders] No Orders")

        except Exception as e:
            print(f"[extract_user_info] orders error: {e}")
            orders = ""
        print(f"[user] name={name}, star={star}, country={country}, remark={remark}")

        return name, star, country, remark, orders