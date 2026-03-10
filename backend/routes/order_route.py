from flask import Blueprint, jsonify
from flask import send_file
from helper_functions.save_excel import save_orders_to_xlsx
import os
order_bp = Blueprint("orders", __name__)
def get_all_orders():
    conn=None
    try:
        import sqlite3
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "database", "orders.db")
        print("DB PATH:", db_path)
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
        headers = [
            "Store", "Order ID", "Date", "Buyer",
            "Product", "Specs", "SKU", "Price", "Qty", "Amount",
            "Status (中文)", "Status (EN)", "AE/IOSS", "Semi-Managed", "Action",
            "Recipient", "Address", "Postal Code", "Email", "Country","Phone", "Tax Number", "Order Link"
        ]
        col_widths = [10,20,18,12,40,25,15,12,6,12,16,20,8,14,20,20,50,12,25,15, 15,15,75]
        xlsx_path, xlsx_name = save_orders_to_xlsx(orders, store=None, filename=filename, headers=headers, col_widths=col_widths)

        return send_file(
            xlsx_path,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=xlsx_name
        )

    except Exception as e:
        print(f"[export_orders]Error message is{e}")
        return jsonify({"error": str(e)}), 500