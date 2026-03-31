import os
import re
from utils._load_json import load_json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROMPT_PATH = os.path.join(BASE_DIR, "agent", "rag", "prompt.md")

ANSWERS_PATH = os.path.join(BASE_DIR, "knowledge_base", "intent_answers.json")

INTENT_ANSWERS = load_json(ANSWERS_PATH)

def format_bullet_answer(answer: str):
    # 🔹 去掉多余换行
    answer = answer.strip()

    # 🔹 先按句子切分（. ! ?）
    sentences = re.split(r'[.!?]+', answer)

    # 🔹 过滤空句子
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return answer

    # 🔹 第一条当作开头（表扬用户）
    intro = sentences[0]

    # 🔹 后面做 bullet（最多5条）
    bullets = sentences[1:6]

    # 🔹 拼接
    formatted = intro + "\n\n"

    for s in bullets:
        formatted += f"{s}\n"
    print(f"Formatted answer is\n{formatted}")
    return formatted

def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()
    
def build_prompt(context, query):
    template = load_prompt()
    return template.replace("{retrieved_chunks}", context)\
                   .replace("{question}", query)


# ------------------------------
# generate reply（只负责输出）
# ------------------------------
# def generate_reply(intent):
    
#     if intent in INTENT_ANSWERS:
#         return INTENT_ANSWERS[intent]["answer"]

#     return None