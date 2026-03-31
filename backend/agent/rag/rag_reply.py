from agent.rag.rag_utils import format_bullet_answer, build_prompt
from agent.handle_intent import detect_intent, generate_reply
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI
# from database.user_order_management import fetch_orders_by_username
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
def rag_reply(query: str, user_name:str) -> str:
    # =========================
    # 🔥 获取用户订单（关键🔥）
    # =========================
    # orders = fetch_orders_by_username(user_name=user_name)
    # print(f"[chat] orders = {orders}")
    # if not orders or orders == "No Orders":
    #     return {
    #         "answer": "Welcome to ZBooster. This is Ziri.",
    #         "jpg": [],
    #         "mp4": [],
    #         "alert": ""
    #     }

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
            result = generate_reply(intent)

            return {
                "answer": result["answer"],
                "jpg": result["jpg"],
                "mp4": result["mp4"],
                "alert": result["alert"]
            }

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
            return {
                "answer": "Sorry, I can only assist with product and order related questions.",
                "jpg": [],
                "mp4": [],
                "alert": ""
            }

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

        return {
            "answer": answer,
            "jpg": [],
            "mp4": [],
            "alert": ""
        }

    except Exception as e:
        print("[rag_reply ERROR]:", e)
        return "Let me check this for you."