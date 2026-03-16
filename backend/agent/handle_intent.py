
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from load_json_ import load_json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANSWERS_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "intent_answers.json"
)
VECTOR_PATH = os.path.join(
    BASE_DIR,
    "embeddings",
    "intent_vectors.json"
)

INTENT_ANSWERS=load_json(ANSWERS_PATH)
VECTOR_DATA=load_json(VECTOR_PATH)

model = SentenceTransformer("BAAI/bge-small-en")


# ------------------------------
# load vectors
# ------------------------------

intent_vectors = {}

for intent, item in VECTOR_DATA.items():
    intent_vectors[intent] = np.array(item["vector"])

# ------------------------------
# cosine similarity
# -----------------------------

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ------------------------------
# match intent
# ------------------------------
def match_intent(message, threshold=0.65):

    query_vec = model.encode(message, normalize_embeddings=True)

    best_intent = None
    best_score = 0

    for intent, vec in intent_vectors.items():

        score = cosine(query_vec, vec)
        print(f"[match_intent] score with intent {intent} is {score}")
        if score > best_score:
            best_score = score
            best_intent = intent

    print(f"[match_intent] best={best_intent}, score={best_score}")

    if best_score > threshold:
        return best_intent, best_score

    return None, best_score

# ------------------------------
# generate reply
# ------------------------------
def generate_reply(message):

    intent, score = match_intent(message)

    if intent:
        return INTENT_ANSWERS[intent]["answer"]

    return "I need assistant to help you. Please wait a moment."


# Old code
# KEYWORDS_PATH = os.path.join(
#     BASE_DIR,
#     "knowledge_base",
#     "keywords.json"
# )




# KEYWORDS=load_json(KEYWORDS_PATH)

# BUSINESS_INTENTS = [
#     "which_model", 
#     "damage",
#     "how_ship",
#     "shipping_time",
#     "refund",
#     "return",
#     "not_work",
#     "tracking",
#     "install",
#     "cancel_order",
#     "missing_parts",
#     "wrong_item",
#     "warranty"
# ]

# SOCIAL_INTENTS = [
#     "hi",
#     "thank_you",
#     "human"
# ]

# # def detect_intent(message):
# #     msg = message.lower()
# #     for intent, words in KEYWORDS.items():
# #         for item in words:
# #             keyword = item["word"]
# #             if keyword in msg:
# #                 item["count"] += 1
# #                 return intent
# #     return None

# def save_keywords():
#     with open(KEYWORDS_PATH, "w", encoding="utf-8") as f:
#         json.dump(KEYWORDS, f, indent=2)

# def match_keywords(intent, msg):

#     if intent not in KEYWORDS:
#         return False

#     for item in KEYWORDS[intent]:

#         keyword = item["word"]

#         if keyword in msg:
#             return True

#     return False


# def detect_intent(message):

#     msg = message.lower()

#     # 先检测业务
#     for intent in BUSINESS_INTENTS:
#         if match_keywords(intent, msg):
#             return intent

#     # 再检测社交
#     for intent in SOCIAL_INTENTS:
#         if match_keywords(intent, msg):
#             return intent

#     return None

# def generate_reply(message):

#     intent = detect_intent(message)
#     print(f"[generate_reply]Intent is: {intent}")
#     if intent and intent in INTENT_ANSWERS:
#         return INTENT_ANSWERS[intent]

#     return "Let me check this for you. One moment please."