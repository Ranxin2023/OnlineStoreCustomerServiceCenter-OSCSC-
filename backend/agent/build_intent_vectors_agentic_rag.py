import json
import os
from openai import OpenAI
from utils._load_json import load_json
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANSWERS_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "intent_answers_agentic_rag.json" 
)

VECTOR_PATH = os.path.join(
    BASE_DIR,
    "embeddings",
    "intent_vectors_openai_agentic_rag.json"       
)


def get_embedding(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding


def main():
    answers=load_json(ANSWERS_PATH)
    result = {}

    for intent, item in answers.items():

        intents = item.get("intent", [])

        # 🔥 兼容 string / list
        if isinstance(intents, str):
            intents = [intents]

        vectors = []

        for phrase in intents:
            phrase = phrase.strip()

            if not phrase:
                continue

            try:
                vec = get_embedding(phrase)
                vectors.append(vec)
            except Exception as e:
                print(f"❌ embedding failed: {phrase} | {e}")

        if not vectors:
            print(f"⚠️ no vectors for intent: {intent}")

        # 🔥 核心：保留所有字段（type / tool / answer / jpg）
        result[intent] = {
            **item,
            "vectors": vectors
        }

        print(f"✅ encoded intent: {intent} ({len(vectors)} phrases)")

    os.makedirs(os.path.dirname(VECTOR_PATH), exist_ok=True)

    with open(VECTOR_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("🚀 intent vectors regenerated (agentic)")


if __name__ == "__main__":
    main()