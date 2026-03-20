from constants.country_maps import PHONE_COUNTRY_MAP, ADDRESS_COUNTRY_MAP
from typing import Dict, Tuple
def get_country_from_address(address: str):
    if not address:
        return None

    addr = address.lower()

    for key, country in ADDRESS_COUNTRY_MAP.items():
        if key in addr:
            return country

    return None


def get_country_from_order(order: Dict[str, str]):
    phone = order.get("phone", "")
    address_raw = order.get("address", "")
    address = address_raw.lower() if address_raw else ""
    if not phone and not address_raw:
        print("[get_country_from_order] NO phone or address found")
        return "Unknown"

    # ─────────────────────────────
    # fallback：没有 phone 用 address
    # ─────────────────────────────
    if not phone:
        
        for key, country in ADDRESS_COUNTRY_MAP.items():
            if key in address:
                return country
        return "Unknown"
    
    phone = phone.replace(" ", "").replace("-", "")

    # ─────────────────────────────
    # +1 特殊处理（US / CA）
    # ─────────────────────────────
    if phone.startswith("+1") or phone.startswith("1"):
        for key, country in ADDRESS_COUNTRY_MAP.items():
            if key in address:
                return country
        return "US"

    # ─────────────────────────────
    # +7 特殊处理（RU / KZ）
    # ─────────────────────────────
    if phone.startswith("+7") or phone.startswith("7"):
        for key, country in ADDRESS_COUNTRY_MAP.items():
            if key in address:
                return country
        return "RU"
    
    # ─────────────────────────────
    # 普通区号匹配
    # ─────────────────────────────
    for prefix, country in PHONE_COUNTRY_MAP.items():
        if phone.startswith(prefix) or phone.startswith(prefix.replace("+", "")):
            return country
        
    return "Unknown"

def parse_address(address:str)->Tuple[str]:
    """
    从地址解析 city 和 province/state
    """
    if not address:
        return "", ""

    parts = [p.strip() for p in address.split(",")]

    city = ""
    province = ""

    if len(parts) >= 4:
        city = parts[-4]
        province = parts[-3]

    elif len(parts) == 3:
        city = parts[-3]
        province = parts[-2]

    return province, city

