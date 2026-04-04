from agent.rag.rag_utils import format_bullet_answer, build_prompt
from agent.handle_intent import detect_intent
# from agent.handle_intent import generate_reply
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI
from database.user_management import fetch_vip_status_from_users
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
# def rag_reply(query: str, user_name:str) -> str:
#     # =========================
#     # 🔥 获取用户订单（关键🔥）
#     # =========================
#     # orders = fetch_orders_by_username(user_name=user_name)
#     # print(f"[chat] orders = {orders}")
#     # if not orders or orders == "No Orders":
#     #     return {
#     #         "answer": "Welcome to ZBooster. This is Ziri.",
#     #         "jpg": [],
#     #         "mp4": [],
#     #         "alert": ""
#     #     }

#     try:
#         print(f"[rag_reply] query={query}")

#         # =========================
#         # 1️⃣ intent 层
#         # =========================
#         intent_result = detect_intent(query)

#         intent = intent_result["intent"]
#         score = intent_result["score"]

#         print(f"[INTENT] intent={intent}, score={score}")

#         if intent:
#             result = generate_reply(intent)

#             return {
#                 "answer": result["answer"],
#                 "jpg": result["jpg"],
#                 "mp4": result["mp4"],
#                 "alert": result["alert"]
#             }

#         # =========================
#         # 2️⃣ RAG 检索
#         # =========================
#         docs_with_score = vectorstore.similarity_search_with_score(query, k=3)

#         retrieved_docs = []
#         scores = []

#         for doc, score in docs_with_score:
#             retrieved_docs.append(doc.page_content)
#             scores.append(score)

#         best_score = scores[0] if scores else 999
#         print(f"[RAG] best_score={best_score}")

#         # =========================
#         # 3️⃣ out-of-scope 判断
#         # =========================
#         SIM_THRESHOLD = 1.0

#         if best_score > SIM_THRESHOLD:
#             return {
#                 "answer": "Sorry, I can only assist with product and order related questions.",
#                 "jpg": [],
#                 "mp4": [],
#                 "alert": ""
#             }

#         # =========================
#         # 4️⃣ 正常 RAG
#         # =========================
#         context = "\n".join(retrieved_docs)

#         prompt = build_prompt(context, query)

#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}]
#         )

#         answer = response.choices[0].message.content

#         # 🔥 保留你原来的 bullet formatting
#         answer = format_bullet_answer(answer)

#         return {
#             "answer": answer,
#             "jpg": [],
#             "mp4": [],
#             "alert": ""
#         }

#     except Exception as e:
#         print("[rag_reply ERROR]:", e)
#         return "Let me check this for you."
    
def rag_search_and_generate(query):

    try:
        # =========================
        # 1️⃣ RAG 检索
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
        # 2️⃣ out-of-scope 判断
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
        # 3️⃣ 构造 prompt
        # =========================
        context = "\n".join(retrieved_docs)
        prompt = build_prompt(context, query)

        # =========================
        # 4️⃣ LLM 生成
        # =========================
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content

        # 保留你的格式化
        answer = format_bullet_answer(answer)

        return {
            "answer": answer,
            "jpg": [],
            "mp4": [],
            "alert": ""
        }

    except Exception as e:
        print("[rag_search ERROR]:", e)

        return {
            "answer": "Let me check this for you.",
            "jpg": [],
            "mp4": [],
            "alert": ""
        }
    
def check_order_status():
    print("checking order status")

def refund_logic():
    print("refunding")

def rag_reply(query, user_name):

    # 1️⃣ intent
    intent_result = detect_intent(query)
    intent = intent_result["intent"]
    config = intent_result["config"]

    # 2️⃣ 获取用户信息（🔥你已经有）
    vip_info = fetch_vip_status_from_users(user_name)  
    # {star, country, orders...}

    # =========================
    # 🟢 CASE 1: FAQ
    # =========================
    if intent and config["type"] == "faq":
        return {
            "answer": config["answer"],
            "jpg": config.get("jpg", []),
            "mp4": config.get("mp4", []),
            "alert": config.get("alert", "")
        }

    # =========================
    # 🔴 CASE 2: TOOL（核心🔥）
    # =========================
    if intent and config["type"] == "tool":

        tool_name = config["tool"]

        if tool_name == "check_order_status":
            result = check_order_status(vip_info)

        elif tool_name == "refund_flow":
            result = refund_logic(vip_info)

        else:
            result = "Sorry, I cannot handle this request yet."

        # 👉 VIP逻辑（🔥关键）
        if vip_info["star"] == "VIP":
            result = "Dear VIP customer, " + result

        return {
            "answer": result,
            "jpg": [],
            "mp4": [],
            "alert": ""
        }

    # =========================
    # 🔵 CASE 3: RAG fallback
    # =========================
    return rag_search_and_generate(query)