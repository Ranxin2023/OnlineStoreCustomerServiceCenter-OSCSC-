from agent.handle_intent import detect_intent, generate_reply
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI
from agent.rag.rag_utils import format_bullet_answer
import os

rag_bp = Blueprint("rag", __name__)

load_dotenv()

# ✅ embedding（和建库一致）
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# ✅ 用 LangChain 连接 Chroma（关键🔥）
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)

# ✅ LLM
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ prompt
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_PATH = os.path.join(BASE_DIR, "agent", "rag", "prompt.md")

def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(context, query):
    template = load_prompt()
    return template.replace("{retrieved_chunks}", context)\
                   .replace("{question}", query)

def jsonify_answers(answer: str, source: str, score, context):
    return jsonify({
        "answer": answer, 
        "source": source, 
        "rag_score":score,
        "context":context
    })

@rag_bp.route("/api/chat/rag", methods=["POST", "OPTIONS"])
def rag_chat():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.json
    query = data.get("message")
    print(f"[rag_chat] query is {query}")
    if not query:
        return jsonify({"error": "message required"}), 400

    # =========================
    # 🔥 1️⃣ intent 判断（第一层）
    # =========================
    intent_result = detect_intent(query)

    intent = intent_result["intent"]
    score = intent_result["score"]

    print(f"[INTENT] intent={intent}, score={score}")

    if intent:
        reply = generate_reply(intent)
        return jsonify_answers(reply, "intent", score, None)
        
    # =========================
    # 🔥 2️⃣ RAG 检索 + score（关键）
    # =========================
    docs_with_score = vectorstore.similarity_search_with_score(query, k=3)

    print("\n[RAG] Retrieved docs:\n")

    retrieved_docs = []
    scores = []

    for idx, (doc, score) in enumerate(docs_with_score):
        print(f"doc{idx+1}: {doc}\n score:{score}")
        retrieved_docs.append(doc.page_content)
        scores.append(score)

    # =========================
    # 🔥 3️⃣ out-of-scope 判断（核心）
    # =========================
    best_score = scores[0] if scores else 999

    print(f"[RAG] best_score={best_score}")

    # ⚠️ 注意：LangChain score 越小越相似
    SIM_THRESHOLD = 1.0

    if best_score > SIM_THRESHOLD:
        return jsonify_answers(answer="Sorry, I can only assist with product and order related questions."
                               , source="out_of_scope", score=best_score, context=None)

    # =========================
    # 🔥 4️⃣ 正常 RAG
    # =========================
    context = "\n".join(retrieved_docs)

    prompt = build_prompt(context, query)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content
    # formatting answer to bullet point
    answer = format_bullet_answer(answer)
    return jsonify_answers(answer=answer, source="rag", score=best_score, context=retrieved_docs)