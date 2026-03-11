from flask import Blueprint, jsonify
from flask import send_file
from helper_functions.save_excel import save_orders_to_xlsx
from helper_functions.constant_values import FILL_COUNTRY_HEADERS
import os
import sqlite3

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "database", "orders.db")
order_bp = Blueprint("orders", __name__)
def get_all_orders():
    conn=None
    try:
        
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM orders")

        rows = cursor.fetchall()

        print(f"The length of rows are{len(rows)}")
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[get_orders] Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def parse_address(address):
    """
    从地址解析 city 和 province/state
    """
    if not address:
        return "", ""

    parts = [p.strip() for p in address.split(",")]

    city = ""
    province = ""

    if len(parts) >= 4:
        city = parts[-4]
        province = parts[-3]

    elif len(parts) == 3:
        city = parts[-3]
        province = parts[-2]

    return province, city

@order_bp.route("/api/orders/export", methods=["GET"])
def export_orders():
    try:
        orders = get_all_orders()

        if not orders:
            return jsonify({"error": "No orders found"}), 404
        filename = "order_list.xlsx"
        headers = [
            "Store", "Order ID", "Date", "Buyer","Product", "Specs", 
            "SKU", "Price", "Qty", "Amount","Status (中文)", "Status (EN)", 
            "AE/IOSS", "Semi-Managed", "Action","Recipient", "Address", "Postal Code", 
            "Email", "Phone","Country","Tax Number", "Remark", "Order Link"
        ]
        keys=[
            "store", "order_id", "date", "buyer","product", "specs", 
            "sku", "price", "qty", "amount","status", "status_en", 
            "ae_ioss", "semi_managed", "action","recipient", "address", "postal_code", 
            "email", "phone","country","tax_number", "remark", "order_link" 
        ]
        col_widths = [
                    10,20,18,12,40,25,
                    15,12,6,12,16,20,
                    8,14,20,20,50,12,
                    25,15, 15,15,15, 75
                    ]
        xlsx_path, xlsx_name = save_orders_to_xlsx(orders, filename=filename,data_keys=keys,excel_headers=headers, col_widths=col_widths)

        return send_file(
            xlsx_path,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=xlsx_name
        )

    except Exception as e:
        print(f"[export_orders]Error message is{e}")
        return jsonify({"error": str(e)}), 500
    

@order_bp.route("/api/orders/sa")
def download_sa_orders():

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT order_id,country,address,phone, date, recipient FROM orders WHERE country = 'SA' AND status_en = 'Awaiting shipment'")

    rows = [dict(r) for r in cursor.fetchall()]
    date_counter = {}

    sa_orders = []
    column_widths=[35 for i in range(79)]
    keys=[]
    excel_headers=[]
    for fill_option, column, key, value in FILL_COUNTRY_HEADERS:
        keys.append(key)
        excel_headers.append(column)
    for order in rows:
        row={}
        province, city = parse_address(order.get("address"))
        for fill_option, column, key, value in FILL_COUNTRY_HEADERS:
            if fill_option=='blank':
                row[key]=""
                
            elif fill_option=='fixed':
                row[key]=value
            elif key in order:
                row[key]=order.get(key)
            elif key=='row_number':
                
                order_date = order.get("date")

                if order_date:
                    date_str = order_date.split(" ")[0].replace("-", "")
                else:
                    date_str = "00000000"

                if date_str not in date_counter:
                    date_counter[date_str] = 1
                else:
                    date_counter[date_str] += 1
            
                row[key] = f"{date_str}{date_counter[date_str]:03d}"
            elif key == "recipient_province_state":
                row[key] = province

            elif key == "recipient_city":
                row[key] = city
        sa_orders.append(row)
            

    filepath = save_orders_to_xlsx(data=sa_orders,filename="华通燕文订单.xlsx",data_keys=keys, excel_headers=excel_headers,col_widths=column_widths)

    return send_file(
        filepath,
        as_attachment=True,
        download_name="华通燕文订单.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )