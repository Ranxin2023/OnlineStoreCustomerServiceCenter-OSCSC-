from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import os
import time
import socket
import subprocess
from dotenv import load_dotenv
load_dotenv()
DEBUG_PORT       = 9222
CHROME_PATH      = os.getenv("CHROME_PATH")
CHROME_USER_DATA = os.getenv("CHROME_USER_DATA")

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
# ─────────────────────────────────────────────────────
# 状态翻译
# ─────────────────────────────────────────────────────

def translate_status(status):
    mapping = {
        '等待发货':     'Awaiting shipment',
        '等待买家收货': 'Awaiting buyer receipt',
        '交易成功':     'Transaction complete',
        '已关闭':       'Closed',
        '等待付款':     'Awaiting payment',
        '等待买家付款': 'Awaiting payment',
        '等待仓库发货': 'Awaiting warehouse shipment',
    }
    return mapping.get(status, status)



def setup_driver():
    """
    连接已有 Chrome（复用登录态）。
    如果 Chrome 未启动，自动拉起，然后等待端口就绪。
    """
    if not is_chrome_reachable():
        print("🚀 Chrome 未启动，正在自动启动...")
        subprocess.Popen([
            CHROME_PATH,
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--user-data-dir={CHROME_USER_DATA}",
        ])
        # 等待端口就绪，最多 15 秒
        for _ in range(15):
            time.sleep(1)
            if is_chrome_reachable():
                print("✅ Chrome 已就绪")
                break
        else:
            raise RuntimeError(
                "Chrome 启动超时。请手动打开 Chrome 并登录速卖通后重试。"
            )

    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    return driver


# ─────────────────────────────────────────────────────
# 保存 Excel
# ─────────────────────────────────────────────────────

def save_orders_to_xlsx(all_orders):
    base_dir     = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(base_dir, "..", "downloads")
    os.makedirs(download_dir, exist_ok=True)

    filename = "order_list_store1.xlsx"
    filepath = os.path.join(download_dir, filename)

    headers = [
        "Order ID", "Order Link", "Date", "Buyer",
        "Product", "Specs", "SKU", "Price", "Qty", "Amount",
        "Status (中文)", "Status (EN)", "AE/IOSS", "Semi-Managed", "Action",
        "Recipient", "Address", "Postal Code", "Email", "Phone", "Tax Number"
    ]

    # ── 读取已有文件中的订单（用于去重）──────────────────
    existing_orders = {}
    if os.path.exists(filepath):
        try:
            from openpyxl import load_workbook
            wb_old = load_workbook(filepath)
            ws_old = wb_old.active
            for row in ws_old.iter_rows(min_row=2, values_only=True):
                order_id = str(row[0]).lstrip("'").strip() if row[0] else ""
                if order_id:
                    row = list(row)
                    # 统一把日期列转为 datetime 对象
                    if row[2] and not isinstance(row[2], datetime):
                        try:
                            row[2] = datetime.strptime(str(row[2]), "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            pass
                    existing_orders[order_id] = row
            print(f"  读取已有文件，共 {len(existing_orders)} 条历史订单")
        except Exception as e:
            print(f"  读取已有文件失败，将覆盖: {e}")

    # ── 新数据合并，order_id 相同则用新数据覆盖 ──────────
    for order in all_orders:
        order_id = order.get('order_id', '').strip()
        if order_id:
            # 将日期字符串转为 datetime 对象，方便排序和 Excel 格式化
            raw_date = order.get('date', '')
            try:
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            except Exception:
                parsed_date = None

            existing_orders[order_id] = [
                "'" + order.get('order_id', ''),
                order.get('order_link', ''),
                parsed_date,                        # datetime 对象，Excel 会自动格式化
                order.get('buyer', ''),
                order.get('product', ''),
                order.get('specs', ''),
                order.get('sku', ''),
                order.get('price', ''),
                order.get('qty', ''),
                order.get('amount', ''),
                order.get('status', ''),
                order.get('status_en', ''),
                order.get('ae_ioss', ''),
                order.get('semi_managed', ''),
                order.get('action', ''),
                order.get('recipient', ''),
                order.get('address', ''),
                order.get('postal_code', ''),
                order.get('email', ''),
                order.get('phone', ''),
                order.get('tax_number', ''),
            ]

    # ── 按日期降序排列（最新的在最上面）─────────────────
    def sort_key(row):
        date_val = row[2]
        if isinstance(date_val, datetime):
            return date_val
        return datetime.min

    sorted_rows = sorted(existing_orders.values(), key=sort_key, reverse=True)

    # ── 写入文件 ──────────────────────────────────────
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"

    header_fill = PatternFill("solid", start_color="4472C4")
    header_font = Font(bold=True, color="FFFFFF", name="Arial")
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill      = header_fill
        cell.font      = header_font
        cell.alignment = Alignment(horizontal="center")

    ws.freeze_panes = "A2"

    for row_idx, values in enumerate(sorted_rows, 2):
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col, value=value)
            # 日期列设置格式
            if col == 3 and isinstance(value, datetime):
                cell.number_format = "YYYY-MM-DD HH:MM:SS"

        # Order Link 设为超链接
        link_val = values[1] if len(values) > 1 else ""
        if link_val:
            ws.cell(row=row_idx, column=2).hyperlink = link_val
            ws.cell(row=row_idx, column=2).font = Font(color="0563C1", underline="single")

    col_widths = [20, 15, 18, 12, 40, 25, 15, 12, 6, 12, 16, 20, 8, 14, 20, 20, 35, 12, 25, 15, 15]
    for col, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width

    wb.save(filepath)
    print(f"OK 已保存 {len(existing_orders)} 条订单（含历史）-> {filepath}")
    wb.close()
    time.sleep(0.5)
    return filepath, filename