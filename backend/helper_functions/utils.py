import socket
from helper_functions.constant_values import mapping, DEBUG_PORT
from deep_translator import GoogleTranslator

# ─────────────────────────────────────────────────────
# Driver — 自动检测并启动 Chrome
# ─────────────────────────────────────────────────────

translator = GoogleTranslator(source="auto", target="en")
def is_chrome_reachable():
    """检查 Chrome 调试端口是否可连接"""
    try:
        s = socket.create_connection(("127.0.0.1", DEBUG_PORT), timeout=2)
        s.close()
        return True
    except OSError:
        return False
# ─────────────────────────────────────────────────────
# 状态翻译
# ─────────────────────────────────────────────────────

def translate_status(status):
    
    return mapping.get(status, status)


def parse_address(address):
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
def translate_text(text):
    if not text:
        return ""
    try:
        return translator.translate(text)
    except Exception:
        return text