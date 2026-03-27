import os
from flask import jsonify
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def handle_saudi_logic(query):

    # 🔥 调外部 API
    # api_result = call_saudi_api(query)

    # 🔥 让 LLM 组织语言（function calling 思想）
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a Saudi customer service assistant"
            },
            {
                "role": "user",
                "content": f"""
                User question: {query}


            Please answer politely.
            """
            }
        ]
    )

    return jsonify({
        "answer": response.choices[0].message.content,
        "source": "saudi_api"
    })