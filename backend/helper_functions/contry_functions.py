from helper_functions.constant_values import PHONE_COUNTRY_MAP, ADDRESS_COUNTRY_MAP
def get_country_from_address(address: str):
    if not address:
        return None

    addr = address.lower()

    for key, country in ADDRESS_COUNTRY_MAP.items():
        if key in addr:
            return country

    return None
def get_country(order):

    phone = order.get("phone", "")
    address = order.get("address", "")

    if not phone:
        return "Unknown"

    phone = phone.replace(" ", "").replace("-", "")

    # 先查普通国家
    for prefix, country in PHONE_COUNTRY_MAP.items():
        if phone.startswith(prefix):
            return country

    # +1 特殊处理
    if phone.startswith("+1") or phone.startswith("1"):
        country = get_country_from_address(address)
        if country:
            return country
        return "US"   # 默认当美国

    return "Unknown"

def get_country_from_order(order):
    phone = order.get("phone", "")
    address = order.get("address", "")

    if phone:
        phone = phone.replace(" ", "").replace("-", "")

        # 普通区号
        for prefix, country in PHONE_COUNTRY_MAP.items():
            if phone.startswith(prefix) or phone.startswith(prefix.replace("+", "")):
                return country

        # +1 特殊处理
        if phone.startswith("+1") or phone.startswith("1"):
            addr = address.lower()
            for key, country in ADDRESS_COUNTRY_MAP.items():
                if key in addr:
                    return country
            return "US"

    # fallback 用地址判断
    addr = address.lower()
    for key, country in ADDRESS_COUNTRY_MAP.items():
        if key in addr:
            return country

    return "Unknown"