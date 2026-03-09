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

        xlsx_path, xlsx_name = save_orders_to_xlsx(orders, store=None)

        return send_file(
            xlsx_path,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=xlsx_name
        )

    except Exception as e:
        print(f"[export_orders]Error message is{e}")
        return jsonify({"error": str(e)}), 500