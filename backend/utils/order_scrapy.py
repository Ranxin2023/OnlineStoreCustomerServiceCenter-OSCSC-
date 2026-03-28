from constants.constant_values import PAGE_LOADING_TIME, LOADING_TIME, BASE_URL, SWITCHING_TIME, PROFILE_MAP, CHANNEL_ID
from datetime import datetime
from models.web_scrapy_model import WebScrapyModel
from models.load_latest_files import LatestFetch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.translator_functions import translate_status
from utils.contry_functions import get_country_from_order
from typing import Optional
import time

# ─────────────────────────────────────────────────────
# 翻页
# ─────────────────────────────────────────────────────
def go_next_page(web_scrapy_model:Optional[WebScrapyModel], current_page):
        """点击下一页，返回 True 表示成功翻页，False 表示已是最后一页"""
        try:
            total = get_total_pages(web_scrapy_model=web_scrapy_model)
            if total is not None and current_page >= total:
                print(f"  [翻页] 已是最后一页 ({current_page}/{total})")
                return False
            next_btn=web_scrapy_model.find_element_by_css_selector(web_scrapy_model.driver, "button.next-pagination-item.next-next")
            disabled = next_btn.get_attribute("disabled")
            aria_label = next_btn.get_attribute("aria-label") or ""
            print(f"  [翻页] 找到下一页按钮: aria-label='{aria_label}', disabled='{disabled}'")
            if disabled is not None:
                print("  [翻页] 按钮已禁用，已是最后一页")
                return False
            web_scrapy_model.driver.execute_script("arguments[0].click();", next_btn)
            print("  [翻页] 点击下一页成功")
            time.sleep(SWITCHING_TIME)
            return True
        except Exception as e:
            print(f"  [翻页] 未找到下一页按钮，停止: {e}")
            return False

def get_total_pages(web_scrapy_model:Optional[WebScrapyModel]):
        """从分页显示元素读取总页数，例如 '1/30' 返回 30"""
        try:
                display=web_scrapy_model.find_element_by_css_selector(web_scrapy_model.driver, "span.next-pagination-display")
                text = web_scrapy_model.text_strip(display) # 例如 "1/30"
                total = int(text.split("/")[-1])
                print(f"  [分页] 当前: {text}，共 {total} 页")
                return total
        except Exception as e:
                print(f"  [分页] 读取总页数失败: {e}")
                return None
    

# ──———————— 抓所有详情页（不再需要回列表页）──────
def extract_order_detail(web_scrapy_model: Optional[WebScrapyModel], order_link: str):
        """进入详情页，点击完整收货地址眼睛，提取收货信息"""
        result = {
            'recipient':   '',
            'address':     '',
            'postal_code': '',
            'email':       '',
            'phone':       '',
            'tax_number':  ''
        }

        try:
            web_scrapy_model.driver.get(order_link)
        except Exception as e:
            print(f"[extract_order_detail] Error to get the driver{e}")

        # 等待地址区域加载
        try:
            web_scrapy_model.wait_element_located(web_scrapy_model.driver, web_scrapy_model.address_tag_id)
        except Exception:
            print("  [详情页] 地址区域加载超时，跳过此订单")
            return result  # 返回空的 result 字典即可

        # ── 收集地址区域所有元素，返回给前端用于定位按钮 ──
        debug_elements = []
        try:
            container=web_scrapy_model.find_element_by_x_path(web_scrapy_model.driver, "//*[contains(@class,'orderInfo--address')]")
            for el in container.find_elements(By.XPATH, ".//*")[:50]:
                tag = el.tag_name
                cls = el.get_attribute("class") or ""
                txt = (el.text or "").strip()[:40]
                onclick = el.get_attribute("onclick") or ""
                if cls or txt:
                    debug_elements.append({
                        "tag": tag, "class": cls, "text": txt, "onclick": onclick
                    })
        except Exception as e:
                debug_elements.append({"error": str(e)})

        # ── 尝试多种方式点击展开按钮 ──
        # clicked_by = None
        # 页面有两个眼睛图标：左边是买家名字旁，右边是完整收货地址
        # 右边收货地址的眼睛 data-spm-anchor-id 包含 "i3"
        # clicked_by = None
        try:
            eye_els=web_scrapy_model.find_elements_by_css_selector(web_scrapy_model.driver, "i[class*='orderEye--eye']")
                
            target = None
            for el in eye_els:
                    spm = el.get_attribute("data-spm-anchor-id") or ""
                    if ".i3." in spm:
                        target = el
                        break
            # 如果没找到 i3，fallback 取最后一个（通常右边）
            if target is None and eye_els:
                    target = eye_els[-1]
            if target:
                web_scrapy_model.driver.execute_script("arguments[0].click();", target)
                print("     OK 点击收货地址眼睛")
                time.sleep(1)
            else:
                    print("    WARN 未找到眼睛按钮")
        except Exception as e:
            print(f"    WARN 点击眼睛失败: {e}")

        # ──———————— 等收件人脱敏 ──————————
        # unmasked = False
        def recipient_unmasked(d):
            items = d.find_elements(By.CSS_SELECTOR, web_scrapy_model.address_tag_id)
            for item in items:
                    try:
                        label_element=web_scrapy_model.find_element_by_css_selector(item, "span[class*='addressLabel']")
                        label=web_scrapy_model.text_strip(label_element)
                        if "收件人名称" in label:
                            value_element=web_scrapy_model.find_element_by_css_selector(item, "span[class*='addressValue']")
                            value=value_element.text.strip()
                            return "*" not in value and value != ""
                    except Exception:
                        pass
            return False

        try:
                WebDriverWait(web_scrapy_model.driver, 5).until(recipient_unmasked)
                print("    OK 收件人已脱敏")
        except Exception:
                # 等待超时就兜底等 2 秒再读，避免空结果
                print("    WARN 等待收件人脱敏超时，延迟2秒后继续")
                time.sleep(SWITCHING_TIME)


        # ── 读取地址字段 ──
        result = {
                'recipient': '', 'address': '', 'postal_code': '',
                'email': '', 'phone': '', 'tax_number': ''
            }
        address_items=web_scrapy_model.find_elements_by_css_selector(web_scrapy_model.driver, web_scrapy_model.address_tag_id)
        for item in address_items:
            try:
                label_element=web_scrapy_model.find_element_by_css_selector(item, "span[class*='addressLabel']")
                label=web_scrapy_model.text_strip(label_element)
                value_element=web_scrapy_model.find_element_by_css_selector(item, "span[class*='addressValue']")
                value=web_scrapy_model.text_strip(value_element)
                if "收件人名称" in label:
                    result['recipient'] = value
                elif "详细地址" in label:
                    result['address'] = value
                elif "邮编" in label:
                    result['postal_code'] = value
                elif "联系邮件" in label:
                    result['email'] = value
                elif "联系电话" in label:
                    result['phone'] = value
                elif "Tax" in label:
                    result['tax_number'] = value
                elif "National address（仅沙特使用）" in label:
                    print(f"National address is {value}")
                    result['short_address'] = value

            except Exception:
                print("[extract_order_detail]无法找到详情页地址信息。。。。。。")

        # except Exception as e:
        #     print(f"  [extract_order_detail] 详情页错误信息：{e}")

        return result


# ─────────────────────────────────────────────────────
# 列表页解析（第一阶段）+ 详情页抓取（第二阶段）
# ─────────────────────────────────────────────────────

def parse_orders_from_page(web_scrape_model:Optional[WebScrapyModel],store):
    if not web_scrape_model.driver_setup():
        print("[parse_orders_from_page]Driver is not set up, please setup the driver")
        return None
    """
        first stage — 只解析列表数据，不进详情页
    """
    all_orders = []

        # wait for the table to be loaded
    try:
        web_scrape_model.wait_element_located(web_scrape_model.driver, web_scrape_model.table_tag_id)
            
    except Exception:
        print("  [警告] 订单表格未加载")
        return all_orders
        
    tables =web_scrape_model.find_elements_by_css_selector(web_scrape_model.driver, web_scrape_model.table_tag_id)
    print(f"  找到 {len(tables)} 个订单")
        
    for table in tables:
        order_el={}
        order = {}
        order['store']=store
        # find all the tags
        exception_flag = False
        exception_msg = None
        for tag, tag_id, is_multi in web_scrape_model.tag_list:
                try:
                    order_el[tag]=web_scrape_model.find_elements_by_css_selector(crawl_obj=table, tag=tag_id) \
                        if is_multi else web_scrape_model.find_element_by_css_selector(crawl_obj=table, tag=tag_id)
                        
                except Exception as e:
                    order_el[tag] = [] if is_multi else None
                    exception_flag=True
                    exception_msg=e
        if exception_flag:
                print(f"  [跳过] 解析订单出错: {exception_msg}")
                continue
            
                    
            
        # 订单号 + 构造详情链接
        try:
                order_id_el=order_el["order_id_el"]
                order_id = web_scrape_model.text_strip(order_id_el)
                order['order_id'] = order_id
                cid=web_scrape_model.channel_id if web_scrape_model.channel_id else CHANNEL_ID
                order['order_link'] = (
                    f"{BASE_URL}/m_apps/order-manage/"
                    f"orderDetail?orderId={order_id}&channelId={cid}"
                )
                # print(f"[Parse Orders From Page]Order Link is {order['order_link']}")
        except Exception as e:
                print(f"  [订单号解析失败] {e}")
                order['order_id']   = ""
                order['order_link'] = ""

        # 下单时间
        try:
                time_els=order_el["time_el"]
                order['date'] = time_els[0].text.strip() if time_els else ""
                # print(f"[parse_orders_from_page] Order Date is {order['date']}")
        except Exception:
                order['date'] = ""

        # 买家
        try:
                buyer_el=order_el["buyer_el"]
                order['buyer'] = web_scrape_model.text_strip(buyer_el)
        except Exception:
                order['buyer'] = ""

        # 商品名称
        try:
                product_el=order_el["product_el"]
                order['product'] = product_el.text.strip()[:80]
        except Exception:
                order['product'] = ""

        # 规格 / SKU
        try:
                sku_els=order_el["sku_el"]
                order['specs'] = sku_els[0].text.strip() if len(sku_els) > 0 else ""
                order['sku']   = sku_els[1].text.strip() if len(sku_els) > 1 else ""
        except Exception:
                order['specs'] = ""
                order['sku']   = ""

        # 单价
        try:
                price_el = order_el["price_el"]
                order['price'] = web_scrape_model.text_strip(price_el)
        except Exception:
                order['price'] = ""

        # 数量
        try:
                qty_el=order_el["qty_el"]
                order['qty'] = qty_el.text.strip()
        except Exception:
                order['qty'] = ""

        # 总金额
        try:
                amount_el=order_el["amount_el"]
                order['amount'] = web_scrape_model.text_strip(amount_el)
        except Exception:
                order['amount'] = ""

        # 订单状态
        try:
                status_el=order_el["status_el"]
                order['status']    = web_scrape_model.text_strip(status_el)
                order['status_en'] = translate_status(order['status'])
        except Exception:
                order['status']    = ""
                order['status_en'] = ""

        # AE/IOSS
        try:
                tag_els   = order_el["tag_el"]
                tag_texts = [el.text for el in tag_els]
                order['ae_ioss'] = "yes" if "AE/IOSS" in tag_texts else "no"
        except Exception:
                order['ae_ioss'] = "no"

        # 半托管
        try:
                tag_els   = order_el["tag_el"]
                tag_texts  = [el.text for el in tag_els]
                order['semi_managed'] = "yes" if any("半托管" in t for t in tag_texts) else "no"
        except Exception:
                order['semi_managed'] = "no"

        # 操作按钮
        try:
                btns=order_el["btns"]
                btn_texts    = [b.text.strip() for b in btns if b.text.strip()]
                order['action'] = ", ".join(btn_texts)
        except Exception:
                order['action'] = ""

        # 备注
        try:
                note_el = ["note_el"]
                order["remark"] = note_el.text.strip()
        except Exception:
                order["remark"] = ""

        # 详情字段先占位
        order['recipient']   = ""
        order['address']     = ""
        order['postal_code'] = ""
        order['email']       = ""
        order['phone']       = ""
        order['tax_number']  = ""
        order['short_address']  = ""

        all_orders.append(order)

        # except Exception as e:
        #     print(f"  [跳过] 解析订单出错: {e}")
        #     continue

    return all_orders


# ─────────────────────────────────────────────────────
# 主抓取流程
# ─────────────────────────────────────────────────────

def crawl_orders(web_scrapy_model:Optional[WebScrapyModel], order_list_url, max_pages=None, channel_id=None):
        if not web_scrapy_model.driver_setup():
            print("[crawl_orders] Driver is not setup ")
            return None
        web_scrapy_model.channel_id=channel_id
        # 连接已有 Chrome，绝对不能调 driver.quit()，否则会关掉用户的浏览器
        
        print(f"Opening order list: {order_list_url} and Channel id: {channel_id}")
        web_scrapy_model.driver.get(order_list_url)
        time.sleep(SWITCHING_TIME)

        channel_id_ = channel_id if channel_id is not None else CHANNEL_ID
        store = PROFILE_MAP[channel_id_]
        # 等页面真正加载完（等到有订单表格出现，最多 30 秒）
        try:
                web_scrapy_model.wait_element_located(web_scrapy_model.driver, web_scrapy_model.table_tag_id, time=PAGE_LOADING_TIME)
                print("OK 订单列表页已加载")
        except Exception:
                print("WARN 等待订单列表超时，尝试继续...")

        try:
                latest_fetch = LatestFetch()
                last_time = latest_fetch.get_latest_fetch(store)

                if last_time:
                        start_date = datetime.strptime(
                        last_time, "%Y-%m-%d %H:%M:%S"
                        ).strftime("%Y-%m-%d")
                else:
                        start_date = datetime.now().strftime("%Y-%m-%d")

                end_date = datetime.now().strftime("%Y-%m-%d")

                print(f"[AUTO TIME] {start_date} -> {end_date}")

                # 找到两个日期输入框
                date_input_tag="input[placeholder*='开始'], input[placeholder*='结束']"
                date_inputs=web_scrapy_model.wait_elements_located(web_scrapy_model.driver, date_input_tag, time=LOADING_TIME)
                start_input = date_inputs[0]
                end_input = date_inputs[1]
                
                # ---------- 填写开始时间 ----------
                web_scrapy_model.button_click(start_input, start_date)

                # ---------- 填写结束时间 ----------
                web_scrapy_model.button_click(end_input, end_date)

                # 验证是否成功
                start_val = start_input.get_attribute("value")
                end_val = end_input.get_attribute("value")

                print(f"[DEBUG] start value: {start_val}")
                print(f"[DEBUG] end value: {end_val}")

        except Exception as e:
                print(f"WARN 自动填写时间失败: {e}")

        # 等待用户在浏览器里点击查询按钮
        try:
                print("⌛ 请在浏览器中点击【查询】按钮...")

                query_btn=web_scrapy_model.find_element_by_x_path(crawl_obj=web_scrapy_model.driver, tag="//button[.//span[text()='查询']]")
                
                # 获取旧表格第一行（用于检测刷新）
                old_first_row=web_scrapy_model.find_element_by_css_selector(web_scrapy_model.driver, f"{web_scrapy_model.table_tag_id} tbody tr")

                # 重置点击状态
                web_scrapy_model.driver.execute_script("window.__query_clicked = false;")

                # 监听点击
                web_scrapy_model.driver.execute_script("""
                        arguments[0].addEventListener('click', function() {
                        window.__query_clicked = true;
                        });
                """, query_btn)

                print("⌛ 等待用户点击查询按钮...")

                # 等待用户点击（最多 5 分钟）
                WebDriverWait(web_scrapy_model.driver, 300).until(
                        lambda d: d.execute_script("return window.__query_clicked === true;")
                )

                print("OK 检测到用户点击查询，等待订单列表刷新...")

                # 等待表格刷新
                WebDriverWait(web_scrapy_model.driver, LOADING_TIME).until(
                        EC.staleness_of(old_first_row)
                )

                print("OK 订单列表已加载，开始抓取...")

                time.sleep(SWITCHING_TIME)

        except Exception as e:
                print(f"WARN 等待查询超时，尝试继续: {e}")

        all_orders = []
        page = 1

        # ── 第一阶段：翻完所有页，只收集列表数据 ──────────────
        while True:
                print(f"\n第 {page} 页（收集列表）...")
                orders = parse_orders_from_page(web_scrape_model=web_scrapy_model, store=store)
                all_orders.extend(orders)
                print(f"  累计 {len(all_orders)} 条")

                if max_pages and page >= max_pages:
                        print(f"  已达设定最大页数 {max_pages}，停止翻页")
                        break

                if not go_next_page(web_scrapy_model=web_scrapy_model, current_page=page):
                        print("  已到最后一页")
                        break

                page += 1

                # 每 5 页额外冷却
                if page % 5 == 0:
                        print("  冷却 10 秒...")
                        time.sleep(10)

        # ── 第二阶段：统一抓所有详情页（不再需要回列表页）──────
        print(f"\n开始抓取 {len(all_orders)} 条订单的详情页...")
        for order in all_orders:
                # 🚫 半托管订单跳过
                if order.get("semi_managed") == "yes":
                        print(f"  ⏭ 半托管订单跳过详情: {order.get('order_id')}")
                        order["country"]=""
                        continue
                if order.get("order_link"):
                        print(f"  -> 抓详情 {order['order_id']}")
                        detail_data = extract_order_detail(web_scrapy_model=web_scrapy_model, order_link=order["order_link"])
                        order.update(detail_data)
                country = get_country_from_order(order)
                order["country"] = country
                print(f"  🌍 Country detected: {country}")
        # 不调用 driver.quit()，Chrome 是用户自己的，不能关
        return all_orders