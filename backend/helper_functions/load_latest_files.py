import json
import os
from datetime import datetime

def update_latest_fetch(store):

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "downloads", "latest_fetch.json")
    print(f"[update_latest_fetch]Base Dir is{base_dir}")

    # 读取原文件
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    # 更新时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data[store] = now

    # 写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[FETCH TIME UPDATED] {store} → {now}")

def get_latest_fetch(store):

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"[get_latest_fetch]Base Dir is{base_dir}")
    file_path = os.path.join(base_dir, "downloads", "latest_fetch.json")

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get(store)