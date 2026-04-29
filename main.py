import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic
from agent.orchestrator import Orchestrator

load_dotenv()

BANNER = """
╔══════════════════════════════════════════════╗
║     Klaviyo Customer Support Agent           ║
║     Type 'quit' or 'exit' to end session     ║
╚══════════════════════════════════════════════╝
"""


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Copy .env.example to .env and add your key.")
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    orchestrator = Orchestrator(client)

    print(BANNER)
    print("Hello! I'm your Klaviyo support agent. How can I help you today?\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"quit", "exit", "bye", "goodbye"}:
            print("Agent: Thanks for reaching out. Have a great day!")
            break

        print()
        try:
            response = orchestrator.handle_message(user_input)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"Agent: I encountered an error: {e}")
            print("Please try again or contact support@klaviyo.com.")
        print()


if __name__ == "__main__":
    main()
