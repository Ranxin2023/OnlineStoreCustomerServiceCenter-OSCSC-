from flask import Blueprint, request, jsonify
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI
import os
from dotenv import load_dotenv

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


@rag_bp.route("/api/chat/rag", methods=["POST", "OPTIONS"])
def rag_chat():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    data = request.json
    query = data.get("message")

    if not query:
        return jsonify({"error": "message required"}), 400

    # ✅ 正确检索方式（不用自己 embed）
    docs = vectorstore.similarity_search(query, k=3)
    print("docs are:\n")
    for idx, doc in enumerate(docs):
        print(f"docs{idx+1} {doc}")
        
    # 提取文本
    retrieved_docs = [d.page_content for d in docs]

    context = "\n".join(retrieved_docs)

    prompt = build_prompt(context, query)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    return jsonify({
        "answer": answer,
        "context": retrieved_docs
    })