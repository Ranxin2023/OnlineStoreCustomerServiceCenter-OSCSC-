import os
import numpy as np
from openai import OpenAI
from utils._load_json import load_json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANSWERS_PATH = os.path.join(BASE_DIR, "knowledge_base", "intent_answers.json")
VECTOR_PATH = os.path.join(BASE_DIR, "embeddings", "intent_vectors_openai.json")

INTENT_ANSWERS = load_json(ANSWERS_PATH)
VECTOR_DATA = load_json(VECTOR_PATH)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------
# embedding
# ------------------------------
def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding)

# ------------------------------
# load vectors
# ------------------------------
intent_vectors = {
    intent: np.array(item["vectors"])
    for intent, item in VECTOR_DATA.items()
}

# ------------------------------
# cosine similarity
# ------------------------------
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# # ------------------------------
# # detect intent (🔥核心函数)
# # ------------------------------
# def detect_intent(message, threshold=0.5):

#     msg = message.lower().strip()
#     is_short = len(msg.split()) <= 3

#     query_vec = get_embedding(msg)

#     best_intent = None
#     best_score = 0

#     for intent, vectors in intent_vectors.items():

#         for vec in vectors:   # 🔥 遍历每个子intent
#             score = cosine(query_vec, vec)

#             if score > best_score:
#                 best_score = score
#                 best_intent = intent

#     print(f"[intent] best={best_intent}, score={best_score}")

#     dynamic_threshold = threshold + 0.05 if not is_short else threshold

#     if best_score > dynamic_threshold:
#         return {
#             "intent": best_intent,
#             "score": best_score
#         }

#     return {
#         "intent": None,
#         "score": best_score
#     }

# ------------------------------
# detect intent (🔥核心函数)
# ------------------------------
def detect_intent(message, threshold=0.5):

    msg = message.lower().strip()
    is_short = len(msg.split()) <= 3

    query_vec = get_embedding(msg)

    best_intent = None
    best_score = 0

    for intent, vectors in intent_vectors.items():

        for vec in vectors:   # 🔥 遍历每个子intent
            score = cosine(query_vec, vec)

            if score > best_score:
                best_score = score
                best_intent = intent

    print(f"[intent] best={best_intent}, score={best_score}")

    dynamic_threshold = threshold + 0.05 if not is_short else threshold

    # ✅ 命中 intent
    if best_score > dynamic_threshold:
        config = INTENT_ANSWERS.get(best_intent)

        print(f"[intent] config={config}")   # 🔥调试用（强烈建议保留）

        return {
            "intent": best_intent,
            "score": best_score,
            "config": config   # 🔥新增
        }

    # ❌ 未命中
    return {
        "intent": None,
        "score": best_score,
        "config": None   # 🔥一定要加，避免后面报错
    }
# ------------------------------
# generate reply（只负责输出）
# ------------------------------
def generate_reply(intent):
    if intent not in INTENT_ANSWERS:
        return None
    data = INTENT_ANSWERS[intent]

    return {
        "answer": data.get("answer", ""),
        "jpg": data.get("jpg", []) or [],
        "mp4": data.get("mp4", []) or [],
        "alert": data.get("alert", "")
    }