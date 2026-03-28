from flask import Blueprint, jsonify
from flask import send_file
from utils.save_excel import save_orders_to_xlsx
from excel_functions.save_excel import save_yanwen_to_xlsx
from utils.contry_functions import parse_address
from utils.translator_functions import translate_text
from constants.SA_headers import FILL_SA_HEADERS
from constants.order_headers import ORDER_HEADERS, ORDER_KEYS, COLUMN_WIDTHS
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


@order_bp.route("/api/orders/export", methods=["GET"])
def export_orders():
    try:
        orders = get_all_orders()

        if not orders:
            return jsonify({"error": "No orders found"}), 404
        filename = "order_list.xlsx"
        xlsx_path, xlsx_name = save_orders_to_xlsx(orders, filename=filename,data_keys=ORDER_KEYS,excel_headers=ORDER_HEADERS, col_widths=COLUMN_WIDTHS, mode='a')

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

    cursor.execute("SELECT order_id,country,address,phone, date, recipient, short_address FROM orders WHERE country = 'SA' AND status_en = 'Awaiting shipment'")

    rows = [dict(r) for r in cursor.fetchall()]
    date_counter = {}

    sa_orders = []
    column_widths=[2 for _ in range(79)]
    keys=[]
    excel_headers=[]
    
    # add keys and excel headers
    for fill_option, column, key, value in FILL_SA_HEADERS:
        keys.append(key)
        excel_headers.append(column)
        
    # Write SA orders
    for order in rows:
        row={}
        province, city = parse_address(order.get("address"))
        for fill_option, column, key, value in FILL_SA_HEADERS:
            if fill_option=='blank':
                row[key]=""
                
            elif fill_option=='fixed':
                row[key]=value
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
            elif key == "address":
                address = order.get("address", "")
                row[key] = translate_text(address)    

            elif key == "recipient_province_state":
                
                row[key] = translate_text(province)
                
            elif key == "recipient_city":
                row[key] =  translate_text(city)
           
            elif key == "recipient":
                name = order.get("recipient", "")
                row[key] = translate_text(name)  
            elif key == "short_address":
                address=order.get("short_address", "")  
                row[key] = translate_text(address)  
            elif key in order:
                row[key]=order.get(key)
        sa_orders.append(row)
            

    filepath, _= save_yanwen_to_xlsx(data_keys=keys, data=sa_orders, filename="华通燕文订单.xlsx", column_widths=column_widths)

    return send_file(
        filepath,
        as_attachment=True,
        download_name="华通燕文订单.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )