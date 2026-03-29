# import socket
from constants.constant_values import STATUS_TRANSLATION, ORDER_STATUS_MAP
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="auto", target="en")

    
# ─────────────────────────────────────────────────────
# 状态翻译
# ─────────────────────────────────────────────────────

def translate_status(status):
    
    return STATUS_TRANSLATION.get(status, status)

# ─────────────────────────────────────────────────────
# 文字翻译
# ─────────────────────────────────────────────────────

def translate_text(text):
    if not text:
        return ""
    try:
        return translator.translate(text)
    except Exception:
        return text
    

def find_status_code(raw_status: str)->int:
   
    if not raw_status:
        return -1

    raw_status = raw_status.strip()

    # 统一大小写（英文）
    normalized = raw_status.lower()

    # 🔥 做一层模糊匹配（防UI变化）
    if normalized in ORDER_STATUS_MAP:
        return ORDER_STATUS_MAP[normalized]
    return -2  # 未识别