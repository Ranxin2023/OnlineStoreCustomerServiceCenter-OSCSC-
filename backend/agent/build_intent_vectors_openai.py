import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANSWERS_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "intent_answers.json"
)

VECTOR_PATH = os.path.join(
    BASE_DIR,
    "embeddings",
    "intent_vectors_openai.json"
)


def get_embedding(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding


def main():

    with open(ANSWERS_PATH, "r", encoding="utf-8") as f:
        answers = json.load(f)

    result = {}

    for intent, item in answers.items():

        intents = item["intent"]

        # 🔥 统一成 list（兼容你有些写成字符串的情况）
        if isinstance(intents, str):
            intents = [intents]

        vectors = []

        # 🔥 核心：每个句子单独 embedding
        for phrase in intents:
            phrase = phrase.strip()

            if not phrase:
                continue

            vec = get_embedding(phrase)
            vectors.append(vec)

        result[intent] = {
            "intent": intents,
            "answer": item["answer"],
            "vectors": vectors   # 🔥 注意：这里变成 vectors
        }

        print(f"✅ encoded intent: {intent} ({len(vectors)} phrases)")

    os.makedirs(os.path.dirname(VECTOR_PATH), exist_ok=True)

    with open(VECTOR_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("🚀 intent vectors regenerated")


if __name__ == "__main__":
    main()