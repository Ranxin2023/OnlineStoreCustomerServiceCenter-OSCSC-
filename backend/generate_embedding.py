# ✅ 1. imports（新版推荐）
from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from agent.rag.load_jsonl import load_jsonl

# ✅ 2. 加载环境变量
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env")

print(f"✅ API Key loaded: {api_key}")


# ✅ 3. 加载数据
documents = load_jsonl("backend/knowledge_base/hwatel_knowledge_base.jsonl")
print(f"📄 Loaded {len(documents)} documents")

# ✅ 4. 创建 embedding
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# ✅ 5. 创建向量数据库（只做一次）
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embedding,
    persist_directory="./chroma_db"
)

# ✅ 6. 持久化
vectorstore.persist()

print("🚀 Embedding completed and saved to ./chroma_db")