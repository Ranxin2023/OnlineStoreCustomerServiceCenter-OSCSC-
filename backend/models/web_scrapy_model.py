from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.scrape_order_helper import translate_status
import os
import time

load_dotenv()
LOADING_TIME = 15
CHANNEL_ID = "1579616"
BASE_URL         = os.getenv("BASE_URL")
PAGE_DELAY       = 3    # 翻页等待秒数
# <span class="header--value--E2HYUZn header--valueHighLight--wCk3sLF">8209013605484399</span>
tag_list = [
    ("order_id_el","span.header--valueHighLight--wCk3sLF", False), 
    ("time_el","span.header--value--E2HYUZn", True), 
    ("buyer_el","a.buyerInfo--inline--U3y4fIR", False),
    ("product_el","span.productInfo--itemTitle--QshSnPH", False),
    ("sku_el","span.productInfo--skuCodeValue--FJA_1Ru", True),
    ("price_el","span.productInfo--unitFee--mVPKC9G", False),
    ("qty_el","td[data-next-table-col='3'] div", False),
    ("amount_el","div.amount--amount--YdsJokJ", False),
    ("status_el","div.chc-state-label__stateText", False),
    ("tag_el","span.chc-color-tag", True),
    ("btns","button.next-btn span.next-btn-helper", True)
]
class WebScrapyModel:
    def __init__(self, driver):
        self.driver=driver
    
    # ─────────────────────────────────────────────────────
    # 翻页
    # ─────────────────────────────────────────────────────


    def get_total_pages(self):
        """从分页显示元素读取总页数，例如 '1/30' 返回 30"""
        try:
            display = self.driver.find_element(By.CSS_SELECTOR, "span.next-pagination-display")
            text = display.text.strip()  # 例如 "1/30"
            total = int(text.split("/")[-1])
            print(f"  [分页] 当前: {text}，共 {total} 页")
            return total
        except Exception as e:
            print(f"  [分页] 读取总页数失败: {e}")
            return None

    def go_next_page(self, current_page):
        """点击下一页，返回 True 表示成功翻页，False 表示已是最后一页"""
        try:
            total = self.get_total_pages()
            if total is not None and current_page >= total:
                print(f"  [翻页] 已是最后一页 ({current_page}/{total})")
                return False

            next_btn = self.driver.find_element(
                By.CSS_SELECTOR, "button.next-pagination-item.next-next"
            )
            disabled = next_btn.get_attribute("disabled")
            aria_label = next_btn.get_attribute("aria-label") or ""
            print(f"  [翻页] 找到下一页按钮: aria-label='{aria_label}', disabled='{disabled}'")
            if disabled is not None:
                print("  [翻页] 按钮已禁用，已是最后一页")
                return False
            self.driver.execute_script("arguments[0].click();", next_btn)
            print("  [翻页] 点击下一页成功")
            time.sleep(PAGE_DELAY)
            return True
        except Exception as e:
            print(f"  [翻页] 未找到下一页按钮，停止: {e}")
            return False
    # ─────────────────────────────────────────────────────
    # 列表页解析（第一阶段）+ 详情页抓取（第二阶段）
    # ─────────────────────────────────────────────────────

    def parse_orders_from_page(self):
        """
        first stage — 只解析列表数据，不进详情页
        """
        all_orders = []

        # wait for the table to be loaded
        try:
            WebDriverWait(self.driver, LOADING_TIME).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.next-table-row"))
            )
        except Exception:
            print("  [警告] 订单表格未加载")
            return all_orders

        tables = self.driver.find_elements(By.CSS_SELECTOR, "table.next-table-row")
        print(f"  找到 {len(tables)} 个订单")
        
        for table in tables:
            order_el={}
            order = {}
            # find all the tags
            try:
                for tag, tag_id, is_multi in tag_list:
                    try:
                        if is_multi:
                            order_el[tag] = table.find_elements(By.CSS_SELECTOR, tag_id)
                        else:
                            order_el[tag] = table.find_element(By.CSS_SELECTOR, tag_id)
                    except Exception:
                        order_el[tag] = [] if is_multi else None
            except Exception as e:
                print(f"  [跳过] 解析订单出错: {e}")
                continue
                    
            try:
                # 订单号 + 构造详情链接
                try:
                    order_id_el=order_el["order_id_el"]
                    order_id = order_id_el.text.strip()
                    order['order_id'] = order_id
                    cid=self.channel_id if self.channel_id else CHANNEL_ID
                    order['order_link'] = (
                        f"{BASE_URL}/m_apps/order-manage/"
                        f"orderDetail?orderId={order_id}&channelId={cid}"
                    )
                    print(f"[Parse Orders From Page]Order Link is {order['order_link']}")
                except Exception as e:
                    print(f"  [订单号解析失败] {e}")
                    order['order_id']   = ""
                    order['order_link'] = ""

                # 下单时间
                try:
                    time_els=order_el["time_el"]
                    
                    order['date'] = time_els[0].text.strip() if time_els else ""
                except Exception:
                    order['date'] = ""

                # 买家
                try:
                    buyer_el=order_el["buyer_el"]
                    order['buyer'] = buyer_el.text.strip()
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
                    price_el = table.find_element(
                        By.CSS_SELECTOR, "span.productInfo--unitFee--mVPKC9G"
                    )
                    order['price'] = price_el.text.strip()
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
                    order['amount'] = amount_el.text.strip()
                except Exception:
                    order['amount'] = ""

                # 订单状态
                try:
                    status_el=order_el["status_el"]
                    order['status']    = status_el.text.strip()
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

                # 详情字段先占位
                order['recipient']   = ""
                order['address']     = ""
                order['postal_code'] = ""
                order['email']       = ""
                order['phone']       = ""
                order['tax_number']  = ""

                all_orders.append(order)

            except Exception as e:
                print(f"  [跳过] 解析订单出错: {e}")
                continue

        return all_orders
    

    # ─────────────────────────────────────────────────────
    # 主抓取流程
    # ─────────────────────────────────────────────────────

    def crawl_orders(self, order_list_url, max_pages=None, channel_id=None):
        self.channel_id=channel_id
        # 连接已有 Chrome，绝对不能调 driver.quit()，否则会关掉用户的浏览器
        

        print(f"Opening order list: {order_list_url} and Channel id: {channel_id}")
        self.driver.get(order_list_url)
        time.sleep(2)

        self.driver.execute_script("""
        localStorage.clear();
        sessionStorage.clear();
        """)

        self.driver.refresh()
        # 等页面真正加载完（等到有订单表格出现，最多 30 秒）
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.next-table-row"))
            )
            print("OK 订单列表页已加载")
        except Exception:
            print("WARN 等待订单列表超时，尝试继续...")

        # 等待用户在浏览器里点击查询按钮
        print("⏳ 请在浏览器里点击【查询】按钮，程序将自动继续...")
        try:
            # 找到查询按钮，注入 JS 监听点击事件，点击后设置一个标记
            query_btn = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[.//span[text()='查询']]")
                )
            )
            self.driver.execute_script("""
                arguments[0].addEventListener('click', function() {
                    window.__query_clicked = true;
                });
            """, query_btn)
            print("  监听查询按钮中，等待用户点击...")

            # 等用户点击（最多 5 分钟）
            WebDriverWait(self.driver, 300).until(
                lambda d: d.execute_script("return window.__query_clicked === true;")
            )
            print("OK 检测到用户点击查询，等待列表刷新...")
            time.sleep(2)

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.next-table-row"))
            )
            print("OK 订单列表已加载，开始抓取...")
            time.sleep(1)
        except Exception as e:
            print(f"WARN 等待查询超时，尝试继续: {e}")

        all_orders = []
        page = 1

        # ── 第一阶段：翻完所有页，只收集列表数据 ──────────────
        while True:
            print(f"\n第 {page} 页（收集列表）...")
            orders = self.parse_orders_from_page()
            all_orders.extend(orders)
            print(f"  累计 {len(all_orders)} 条")

            if max_pages and page >= max_pages:
                print(f"  已达设定最大页数 {max_pages}，停止翻页")
                break

            if not self.go_next_page(page):
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
                continue
            if order.get("order_link"):
                print(f"  -> 抓详情 {order['order_id']}")
                detail_data = self.extract_order_detail(order["order_link"])
                order.update(detail_data)

        # 不调用 driver.quit()，Chrome 是用户自己的，不能关
        return all_orders
    
    def extract_order_detail(self, order_link):
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
            self.driver.get(order_link)

            # 等待地址区域加载
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[class*='orderInfo--addressItem']")
                    )
                )
            except Exception:
                print("  [详情页] 地址区域加载超时，跳过此订单")
                return result  # 返回空的 result 字典即可

            # ── 收集地址区域所有元素，返回给前端用于定位按钮 ──
            debug_elements = []
            try:
                container = self.driver.find_element(
                    By.XPATH, "//*[contains(@class,'orderInfo--address')]"
                )
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
                eye_els = self.driver.find_elements(By.CSS_SELECTOR, "i[class*='orderEye--eye']")
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
                    self.driver.execute_script("arguments[0].click();", target)
                    # clicked_by = "i[class*='orderEye--eye'][data-spm=i3]"
                    print("     OK 点击收货地址眼睛")
                    time.sleep(1)
                else:
                    print("    WARN 未找到眼睛按钮")
            except Exception as e:
                print(f"    WARN 点击眼睛失败: {e}")

            # ── 等收件人脱敏 ──
            # unmasked = False
            def recipient_unmasked(d):
                items = d.find_elements(By.CSS_SELECTOR, "div[class*='orderInfo--addressItem']")
                for item in items:
                    try:
                        label = item.find_element(By.CSS_SELECTOR, "span[class*='addressLabel']").text.strip()
                        if "收件人名称" in label:
                            value = item.find_element(By.CSS_SELECTOR, "span[class*='addressValue']").text.strip()
                            return "*" not in value and value != ""
                    except Exception:
                        pass
                return False

            try:
                WebDriverWait(self.driver, 5).until(recipient_unmasked)
                print("    OK 收件人已脱敏")
            except Exception:
                # 等待超时就兜底等 2 秒再读，避免空结果
                print("    WARN 等待收件人脱敏超时，延迟2秒后继续")
                time.sleep(2)


            # ── 读取地址字段 ──
            result = {
                'recipient': '', 'address': '', 'postal_code': '',
                'email': '', 'phone': '', 'tax_number': ''
            }
            address_items = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='orderInfo--addressItem']")
            for item in address_items:
                try:
                    label = item.find_element(By.CSS_SELECTOR, "span[class*='addressLabel']").text.strip()
                    value = item.find_element(By.CSS_SELECTOR, "span[class*='addressValue']").text.strip()
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
                except Exception:
                    continue
            print(f"recipient: {result['recipient']}")
            print(f"address: {result['address']}")
            print(f"postal_code: {result['postal_code']}")
            print(f"email: {result['email']}")
            print(f"phone: {result['phone']}")
            print(f"tax_number: {result['tax_number']}")

        except Exception as e:
            print(f"  [详情页错误] {e}")

        return result