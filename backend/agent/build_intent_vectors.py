import json
import os
from sentence_transformers import SentenceTransformer

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

model = SentenceTransformer("BAAI/bge-small-en")

def main():

    with open(ANSWERS_PATH, "r", encoding="utf-8") as f:
        answers = json.load(f)
    print(f"Answers are: \n{answers}")
    intents = list(answers.keys())
    texts = [answers[i]["intent"] for i in intents]

    print("Encoding answers...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    result = {}

    for i, intent in enumerate(intents):

        result[intent] = {
            "intent": answers[intent]["intent"],
            "answer": answers[intent]["answer"],
            "vector": embeddings[i].tolist()
        }

    os.makedirs(os.path.dirname(VECTOR_PATH), exist_ok=True)

    with open(VECTOR_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Saved intent vectors:", VECTOR_PATH)


if __name__ == "__main__":
    main()