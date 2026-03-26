from agent.handle_intent import detect_intent, generate_reply

def main():

    print("Customer Service AI Test")
    print("Type 'exit' to quit\n")

    while True:

        message = input("Buyer: ")

        if message.lower() in ["exit", "quit"]:
            print("Bye")
            break

        # 🔥 1️⃣ 先检测 intent
        result = detect_intent(message)

        intent = result["intent"]
        score = result["score"]

        print(f"[test questions] intent={intent}, score={score}")

        # 🔥 2️⃣ 判断是否命中
        if intent:
            reply = generate_reply(intent)
            source = "intent"
        else:
            reply = "👉 (fallback) This should go to RAG"
            source = "fallback"

        print(f"AI ({source}):", reply)
        print()

if __name__ == "__main__":
    main()