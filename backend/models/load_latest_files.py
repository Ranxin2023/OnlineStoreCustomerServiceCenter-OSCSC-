import json
import os
from datetime import datetime
from pathlib import Path
from utils._load_json import load_json
class LatestFetch:
    def __init__(self):
        self.hclaw_dir=Path(__file__).resolve().parents[3]
        # print(f"HClaw dir is {self.hclaw_dir}")
        self.file_path = os.path.join(self.hclaw_dir, "downloads", "latest_fetch.json")

    def update_latest_fetch(self,store):
        
        print(f"[update_latest_fetch]Base Dir is{self.hclaw_dir}")

        # —————————— 读取原文件 ————————————
        data = {}

        if os.path.exists(self.file_path):
            data=load_json(self.file_path)

        # —————————— 更新时间 ——————————
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data[store] = now

        # —————————— 写回文件 ——————————
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"[FETCH TIME UPDATED] {store} → {now}")

    def get_latest_fetch(self,store):
        
        if not os.path.exists(self.file_path):
            return None

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # print(f"[get_latest_fetch] latest fetch from store is: {data.get(store)}")
        return data.get(store)
