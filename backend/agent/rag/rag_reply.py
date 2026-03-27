from agent.rag.rag_utils import format_bullet_answer, generate_reply, build_prompt
from agent.handle_intent import detect_intent
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI

import os

load_dotenv()

embedding = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# 🔥 核心函数（给 listen_chat 用）
# =========================
def rag_reply(query: str) -> str:

    try:
        print(f"[rag_reply] query={query}")

        # =========================
        # 1️⃣ intent 层
        # =========================
        intent_result = detect_intent(query)

        intent = intent_result["intent"]
        score = intent_result["score"]

        print(f"[INTENT] intent={intent}, score={score}")

        if intent:
            return generate_reply(intent)

        # =========================
        # 2️⃣ RAG 检索
        # =========================
        docs_with_score = vectorstore.similarity_search_with_score(query, k=3)

        retrieved_docs = []
        scores = []

        for doc, score in docs_with_score:
            retrieved_docs.append(doc.page_content)
            scores.append(score)

        best_score = scores[0] if scores else 999
        print(f"[RAG] best_score={best_score}")

        # =========================
        # 3️⃣ out-of-scope 判断
        # =========================
        SIM_THRESHOLD = 1.0

        if best_score > SIM_THRESHOLD:
            return "Sorry, I can only assist with product and order related questions."

        # =========================
        # 4️⃣ 正常 RAG
        # =========================
        context = "\n".join(retrieved_docs)

        prompt = build_prompt(context, query)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content

        # 🔥 保留你原来的 bullet formatting
        answer = format_bullet_answer(answer)

        return answer

    except Exception as e:
        print("[rag_reply ERROR]:", e)
        return "Let me check this for you."