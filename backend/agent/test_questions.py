from handle_intent import generate_reply

def main():

    print("Customer Service AI Test")
    print("Type 'exit' to quit\n")

    while True:

        message = input("Buyer: ")

        if message.lower() in ["exit", "quit"]:
            print("Bye")
            break

        reply = generate_reply(message)

        print("AI:", reply)
        print()

if __name__ == "__main__":
    main()