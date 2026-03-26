import re
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