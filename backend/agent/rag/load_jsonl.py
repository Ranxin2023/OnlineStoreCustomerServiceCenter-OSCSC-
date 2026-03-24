# from langchain.document_loaders import JSONLoader
from langchain.schema import Document
import json

def load_jsonl(file_path):
    docs = []
    with open(file_path, "r") as f:
        for line in f:
            item = json.loads(line)

            content = f"""
Category: {item.get('category')}
Question: {item.get('question')}
Answer: {item.get('answer')}
Keywords: {", ".join(item.get('keywords', []))}
"""

            docs.append(Document(
                page_content=content,
                metadata={
                    "category": item.get("category"),
                    "question": item.get("question")
                }
            ))
    return docs

# documents = load_jsonl("knowledge_base/hwatel_knowledge_base.jsonl")
# print(len(documents))