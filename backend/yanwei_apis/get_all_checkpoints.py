import requests

def query_yanwen_tracking(tracking_number, auth_token):
    url = "http://api.track.yw56.com.cn/api/tracking"

    headers = {
        "Authorization": auth_token
    }

    params = {
        "nums": tracking_number
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("❌ Request failed:", response.status_code)
        return None

    data = response.json()

    if data.get("code") != 0:
        print("❌ API error:", data.get("message"))
        return None

    result = data.get("result", [])

    if not result:
        print("❌ No tracking info")
        return None

    return result[0]   # 单号只有一个

def get_all_checkpoints(tracking_number, auth_token):
    info = query_yanwen_tracking(tracking_number, auth_token)

    if not info:
        return None

    # 👉 拿原始 checkpoints
    checkpoints = info.get("checkpoints", [])

    # 👉 排序（最新在前）
    checkpoints_sorted = sorted(
        checkpoints,
        key=lambda x: x["time_stamp"],
        reverse=True
    )

    # 👉 🔥关键：覆盖原始 data 里的 checkpoints（但整体结构不变）
    info["checkpoints"] = checkpoints_sorted

    return info   # ✅ 返回完整 data

