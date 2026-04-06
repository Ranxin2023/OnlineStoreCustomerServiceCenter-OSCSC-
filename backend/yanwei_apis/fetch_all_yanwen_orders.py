from yanwei_apis.get_yanwen_tracking_numbers_from_A import get_yanwen_tracking_numbers_from_A
from yanwei_apis.get_all_checkpoints import get_all_checkpoints
from database.yanwen_management import save_yanwen_order
import os
from dotenv import load_dotenv
load_dotenv()
YANWEN_TOKEN = os.getenv("YANWEN_AUTH_TOKEN")

# ─────────────────────────────────────────
# 批量抓取（你要的核心🔥）
# ─────────────────────────────────────────
def fetch_all_yanwen_orders():
    print(f"YANEN TOKEN is {YANWEN_TOKEN}")

    tracking_numbers = get_yanwen_tracking_numbers_from_A()

    print(f"[YANWEN] All tracking numbers are:\n {tracking_numbers}")

    results = []

    for tn in tracking_numbers:
        try:
            print(f"Fetching: {tn}")

            info = get_all_checkpoints(
                tracking_number=tn,
                auth_token=YANWEN_TOKEN
            )
            # print(f"info is:\n{info}")
            # 👉 存数据库
            save_yanwen_order(
                tracking_number=tn,
                data=info
            )

            results.append({
                "tracking_number": tn,
                "data":info
            })

        except Exception as e:
            print(f"Error for {tn}: {e}")

            results.append({
                "tracking_number": tn,
                "status": "failed",
                "error": str(e)
            })

    return results
