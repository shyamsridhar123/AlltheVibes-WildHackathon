"""
Knock Knock Joke Agent 🚪🤜
Every response is delivered as a knock-knock joke!

Uses the unified config.py for LLM backend (local-first with Ollama).
"""

import sys
import os

# Add parent directory to path to import shared config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import chat as llm_chat, get_current_backend

SYSTEM_PROMPT = """\
You are the Knock Knock Joke Agent. You MUST respond to EVERY user message \
using one or more knock-knock jokes. Your entire reply must be structured as \
knock-knock jokes — no regular prose allowed.

Rules:
1. Every answer MUST be a knock-knock joke (or a series of them).
2. The joke MUST relate to what the user said or asked.
3. Format each joke exactly like this:

   Knock knock!
   (Who's there?)
   <setup>
   (<setup> who?)
   <punchline that answers or relates to the user's message>

4. If the user asks a factual question, weave the real answer into the \
   punchline so it's both funny AND informative.
5. If you need multiple jokes to cover the topic, go for it!
6. Stay family-friendly and keep it fun.
7. Never break character — you are ALWAYS the knock-knock joke agent.
"""


# Conversation history for multi-turn chat
_conversation_history: list[str] = []


def chat_turn(user_input: str) -> str:
    """
    Send a message and get a knock-knock joke response.
    Uses the unified config.py backend (Ollama by default).
    """
    # Build conversation context
    _conversation_history.append(f"User: {user_input}")
    
    # Create prompt with history (limited to last 10 turns)
    history = "\n".join(_conversation_history[-20:])  # Last 10 exchanges
    prompt = f"""Previous conversation:
{history}

Respond to the user's latest message with knock-knock jokes."""
    
    reply = llm_chat(prompt, system=SYSTEM_PROMPT, temperature=1.0)
    _conversation_history.append(f"Agent: {reply}")
    
    return reply


def main() -> None:
    backend = get_current_backend()
    print("=" * 50)
    print("🚪 KNOCK KNOCK JOKE AGENT 🚪")
    print(f"   (Using {backend.upper()} backend)")
    print("=" * 50)
    print("Ask me anything and I'll answer with a knock-knock joke!")
    print('Type "quit" or "exit" to leave.\n')

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("👋 Goodbye!")
            break

        reply = chat_turn(user_input)
        print(f"\n🤡 Agent:\n{reply}\n")


if __name__ == "__main__":
    main()
