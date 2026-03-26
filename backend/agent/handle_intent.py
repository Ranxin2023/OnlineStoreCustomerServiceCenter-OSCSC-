import os
import numpy as np
from openai import OpenAI
from utils.load_json_ import load_json

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
    intent: np.array(item["vector"])
    for intent, item in VECTOR_DATA.items()
}

# ------------------------------
# cosine similarity
# ------------------------------
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ------------------------------
# detect intent (🔥核心函数)
# ------------------------------
def detect_intent(message, threshold=0.5):

    msg = message.lower().strip()

    # 🔥 短句优先（避免 hi + 问题误判）
    is_short = len(msg.split()) <= 3

    query_vec = get_embedding(msg)

    best_intent = None
    best_score = 0

    for intent, vec in intent_vectors.items():
        score = cosine(query_vec, vec)

        # print(f"[intent] {intent} score={score}")

        if score > best_score:
            best_score = score
            best_intent = intent

    print(f"[intent] best={best_intent}, score={best_score}")

    # 🔥 长句提高门槛（防误判）
    dynamic_threshold = threshold + 0.05 if not is_short else threshold

    if best_score > dynamic_threshold:
        return {
            "intent": best_intent,
            "score": best_score
        }

    return {
        "intent": None,
        "score": best_score
    }

# ------------------------------
# generate reply（只负责输出）
# ------------------------------
def generate_reply(intent):
    
    if intent in INTENT_ANSWERS:
        return INTENT_ANSWERS[intent]["answer"]

    return None