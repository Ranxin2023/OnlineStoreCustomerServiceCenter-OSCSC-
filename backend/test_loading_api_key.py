import os
from dotenv import load_dotenv
# 加载环境变量
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env")
print(f"✅ API Key loaded: {api_key}")