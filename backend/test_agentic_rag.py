from agent.rag.rag_reply import rag_reply

def main():
    print("🚀 RAG + Agent Test (Latest Version)")
    print("Type 'exit' to quit\n")

    
    # 👉 你数据库里要有这个用户（否则VIP逻辑测不到）
    test_user = "ae800292"

    while True:
        query = input("Buyer: ")

        if query.lower() in ["exit", "quit"]:
            print("Bye 👋")
            break

        print(f"\n[TEST] user={test_user}")
        print(f"[TEST] query={query}")

        # 🔥 核心调用（你的新架构）
        result = rag_reply(query, test_user)

        # 🔍 Debug输出
        print("\n[DEBUG RESULT]")
        print(result)

        # 🤖 AI回复
        print("\nAI:", result["answer"])

        # 🖼 图片
        if result.get("jpg"):
            print("[Images]:", result["jpg"])

        # 🎥 视频
        if result.get("mp4"):
            print("[Videos]:", result["mp4"])

        # 🚨 alert
        if result.get("alert"):
            print("[ALERT]:", result["alert"])

        print("\n" + "="*50 + "\n")
    

if __name__ == "__main__":
    main()
