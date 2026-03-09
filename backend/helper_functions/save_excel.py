from datetime import datetime
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import os
# import time


load_dotenv()
# ─────────────────────────────────────────────────────
# 保存 Excel
# ─────────────────────────────────────────────────────
 


def save_orders_to_xlsx(new_orders, store):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(base_dir, "..", "..", "..", "downloads")
    os.makedirs(download_dir, exist_ok=True)

    filename = f"order_list_{store}.xlsx" if store else "order_list.xlsx"
    filepath = os.path.join(download_dir, filename)

    headers = [
        "Store", "Order ID", "Date", "Buyer",
        "Product", "Specs", "SKU", "Price", "Qty", "Amount",
        "Status (中文)", "Status (EN)", "AE/IOSS", "Semi-Managed", "Action",
        "Recipient", "Address", "Postal Code", "Email", "Phone", "Tax Number", "Order Link"
    ]

    col_widths = [10,20,18,12,40,25,15,12,6,12,16,20,8,14,20,20,50,12,25,15,15,75]

    old_rows = []

    # ── 如果文件存在，读取旧数据 ─────────────────────────────
    if os.path.exists(filepath):

        from openpyxl import load_workbook

        wb_old = load_workbook(filepath)
        ws_old = wb_old.active

        for row in ws_old.iter_rows(min_row=2, values_only=True):
            old_rows.append(list(row))

        wb_old.close()

        print(f"读取旧Excel {len(old_rows)} 条")

    # ── 处理新订单 ─────────────────────────────
    new_rows = []

    for order in new_orders:

        raw_date = order.get("date", "")

        parsed_date = None
        try:
            parsed_date = datetime.strptime(raw_date, "%m/%d/%Y %H:%M")
        except Exception:
            pass

        new_rows.append([
            store if store is not None else order.get('store', ''),
            order.get('order_id', ''),
            parsed_date,
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
            order.get('order_link', ''),
        ])

    # ── 新订单在前，旧订单在后 ─────────────────────────────
    all_rows = new_rows + old_rows

    # ── 写 Excel ─────────────────────────────
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"

    header_fill = PatternFill("solid", start_color="4472C4")
    header_font = Font(bold=True, color="FFFFFF")

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    ws.freeze_panes = "A2"

    for row_idx, row in enumerate(all_rows, 2):

        for col_idx, value in enumerate(row, 1):

            cell = ws.cell(row=row_idx, column=col_idx, value=value)

            if col_idx == 3 and isinstance(value, datetime):
                cell.number_format = "YYYY-MM-DD HH:MM:SS"

        link_val = row[-1]

        if link_val:
            ws.cell(row=row_idx, column=len(row)).hyperlink = link_val
            ws.cell(row=row_idx, column=len(row)).font = Font(color="0563C1", underline="single")

    for col, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width

    wb.save(filepath)

    print(f"OK 已保存 {len(all_rows)} 条订单 -> {filepath}")

    wb.close()

    return filepath, filename