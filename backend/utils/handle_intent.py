import json
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KEYWORDS_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "keywords.json"
)

ANSWERS_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "intent_answers.json"
)

def load_json(path):
    with open(path, "r",encoding="utf-8") as f:
        return json.load(f)

KEYWORDS=load_json(KEYWORDS_PATH)
INTENT_ANSWERS=load_json(ANSWERS_PATH)
BUSINESS_INTENTS = [
    "which_model", 
    "damage",
    "how_ship",
    "shipping_time",
    "refund",
    "return",
    "not_work",
    "tracking",
    "install",
    "cancel_order",
    "missing_parts",
    "wrong_item",
    "warranty"
]

SOCIAL_INTENTS = [
    "hi",
    "thank_you",
    "human"
]

# def detect_intent(message):
#     msg = message.lower()
#     for intent, words in KEYWORDS.items():
#         for item in words:
#             keyword = item["word"]
#             if keyword in msg:
#                 item["count"] += 1
#                 return intent
#     return None

def save_keywords():
    with open(KEYWORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(KEYWORDS, f, indent=2)

def match_keywords(intent, msg):

    if intent not in KEYWORDS:
        return False

    for item in KEYWORDS[intent]:

        keyword = item["word"]

        if keyword in msg:
            return True

    return False


def detect_intent(message):

    msg = message.lower()

    # 先检测业务
    for intent in BUSINESS_INTENTS:
        if match_keywords(intent, msg):
            return intent

    # 再检测社交
    for intent in SOCIAL_INTENTS:
        if match_keywords(intent, msg):
            return intent

    return None

def generate_reply(message):

    intent = detect_intent(message)
    print(f"[generate_reply]Intent is: {intent}")
    if intent and intent in INTENT_ANSWERS:
        return INTENT_ANSWERS[intent]

    return "Let me check this for you. One moment please."