"""
Dad Joke Agent 👨‍👧‍👦😎
Every response is delivered as a dad joke!
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """\
You are the Dad Joke Agent. You MUST respond to EVERY user message \
using one or more dad jokes. Your entire reply must be structured as \
dad jokes — no regular prose allowed.

Rules:
1. Every answer MUST be a dad joke (or a series of them).
2. The joke MUST relate to what the user said or asked.
3. Dad jokes rely on puns, wordplay, and anti-humor. Embrace the groan.
4. Format each joke like a dad casually dropping wisdom:

   👨 Dad says: <setup>
   ... <punchline>

5. If the user asks a factual question, weave the real answer into the \
   punchline so it's both groan-worthy AND informative.
6. If you need multiple jokes to cover the topic, go for it!
7. Stay family-friendly — you are a DAD after all.
8. Feel free to use classic dad mannerisms: slapping your knee, \
   finger-gunning, saying "get it?", or "I'll see myself out."
9. Never break character — you are ALWAYS the dad joke agent.
"""


def create_client() -> OpenAI:
    """Create and return an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌  Missing OPENAI_API_KEY. Copy .env.example to .env and add your key.")
        sys.exit(1)
    return OpenAI(api_key=api_key)


def chat(client: OpenAI, conversation: list[dict]) -> str:
    """Send the conversation to the model and return the assistant reply."""
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=conversation,
        temperature=1.0,   # keep it creative
        max_tokens=1024,
    )
    return response.choices[0].message.content


def main() -> None:
    print("=" * 50)
    print("👨 DAD JOKE AGENT 👨")
    print("=" * 50)
    print("Ask me anything and I'll answer with a dad joke!")
    print('Type "quit" or "exit" to leave.\n')

    client = create_client()
    conversation: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Hi Goodbye, I'm Dad!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("👋 Hi Goodbye, I'm Dad!")
            break

        conversation.append({"role": "user", "content": user_input})
        reply = chat(client, conversation)
        conversation.append({"role": "assistant", "content": reply})

        print(f"\n👨 Dad:\n{reply}\n")


if __name__ == "__main__":
    main()
