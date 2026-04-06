import os
from flask import Blueprint, jsonify, request

from yanwei_apis.get_all_checkpoints import get_all_checkpoints
from database.yanwen_management import save_yanwen_order
from database.yanwen_management import get_yanwen_tracking_numbers

yanwen_bp = Blueprint("yanwen_bp", __name__)

# 🔥 从环境变量拿 token（推荐）
YANWEN_TOKEN = os.getenv("YANWEN_AUTH_TOKEN")

# ─────────────────────────────────────────
# 单个查询（推荐加，方便调试）
# ─────────────────────────────────────────
@yanwen_bp.route("/api/yanwen/fetch-one", methods=["POST"])
def fetch_one():
    data = request.json
    tracking_number = data.get("tracking_number")

    if not tracking_number:
        return jsonify({"error": "tracking_number required"}), 400

    try:
        exchange_number, checkpoints = get_all_checkpoints(
            tracking_number,
            YANWEN_TOKEN
        )

        save_yanwen_order(
            tracking_number=tracking_number,
            exchange_number=exchange_number,
            checkpoints=checkpoints
        )

        return jsonify({
            "tracking_number": tracking_number,
            "exchange_number": exchange_number,
            "checkpoints": checkpoints
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500





# ─────────────────────────────────────────
# API
# ─────────────────────────────────────────
@yanwen_bp.route("/api/yanwen/fetch-all", methods=["POST", "OPTIONS"])
def fetch_all():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    try:
        results = fetch_all_yanwen_orders()

        success_count = sum(1 for r in results if r["status"] == "success")
        fail_count = len(results) - success_count

        return jsonify({
            "status": "done",
            "total": len(results),
            "success": success_count,
            "failed": fail_count,
            "results": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


