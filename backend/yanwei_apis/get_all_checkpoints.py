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
    # print(f"[get_all_checkpoints]result fetched from yanwen:\n{info}")
    exchange_number=info.get("exchange_number")
    if not info:
        return []

    checkpoints = info.get("checkpoints", [])

    # 按时间排序（最新在前）
    checkpoints_sorted = sorted(
        checkpoints,
        key=lambda x: x["time_stamp"],
        reverse=True
    )

    return exchange_number, checkpoints_sorted

def print_tracking(tracking_number, auth_token):
    exchange_number, checkpoints = get_all_checkpoints(tracking_number, auth_token)

    if not checkpoints:
        print("No tracking data")
        return

    print(f"\n📦 Tracking: {tracking_number}\n")
    print(f"\n📦 Exchange Number: {exchange_number}\n")
    
    for cp in checkpoints:
        print(f"🕒 {cp['time_stamp']}")
        print(f"📍 {cp.get('location', 'N/A')}")
        print(f"📄 {cp['message']}")
        print(f"📊 Status: {cp['tracking_status']}")
        print("-" * 40)