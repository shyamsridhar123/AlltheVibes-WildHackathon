"""
Dad Joke Agent 👨‍👧‍👦😎
Every response is delivered as a dad joke!

Uses the unified config.py for LLM backend (local-first with Ollama).
"""

import sys
import os

# Add parent directory to path to import shared config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import chat as llm_chat, get_current_backend

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


# Conversation history for multi-turn chat
_conversation_history: list[str] = []


def chat_turn(user_input: str) -> str:
    """
    Send a message and get a dad joke response.
    Uses the unified config.py backend (Ollama by default).
    """
    # Build conversation context
    _conversation_history.append(f"User: {user_input}")
    
    # Create prompt with history (limited to last 10 turns)
    history = "\n".join(_conversation_history[-20:])  # Last 10 exchanges
    prompt = f"""Previous conversation:
{history}

Respond to the user's latest message with dad jokes."""
    
    reply = llm_chat(prompt, system=SYSTEM_PROMPT, temperature=1.0)
    _conversation_history.append(f"Dad: {reply}")
    
    return reply


def main() -> None:
    backend = get_current_backend()
    print("=" * 50)
    print("👨 DAD JOKE AGENT 👨")
    print(f"   (Using {backend.upper()} backend)")
    print("=" * 50)
    print("Ask me anything and I'll answer with a dad joke!")
    print('Type "quit" or "exit" to leave.\n')

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

        reply = chat_turn(user_input)
        print(f"\n👨 Dad:\n{reply}\n")


if __name__ == "__main__":
    main()
