# import socket
from utils.constant_values import STATUS_TRANSLATION
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="auto", target="en")

    
# ─────────────────────────────────────────────────────
# 状态翻译
# ─────────────────────────────────────────────────────

def translate_status(status):
    
    return STATUS_TRANSLATION.get(status, status)


def translate_text(text):
    if not text:
        return ""
    try:
        return translator.translate(text)
    except Exception:
        return text