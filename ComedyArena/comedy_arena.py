"""
🏟️ Comedy Arena — Joke Judge Showdown
Two joke agents battle it out. An impartial (but dramatic) Judge scores them.
Uses the LLM-as-a-Judge evaluation pattern for AI comedy critique.
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Agent System Prompts ─────────────────────────────────────────────

KNOCK_KNOCK_PROMPT = """\
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
5. Stay family-friendly and keep it fun.
6. Never break character.
"""

DAD_JOKE_PROMPT = """\
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
6. Stay family-friendly — you are a DAD after all.
7. Feel free to use classic dad mannerisms: slapping your knee, \
   finger-gunning, saying "get it?", or "I'll see myself out."
8. Never break character.
"""

JUDGE_PROMPT = """\
You are the Comedy Arena Judge — a dramatically serious, Simon-Cowell-meets-\
Roger-Ebert style critic who evaluates jokes with absurd gravitas.

You will be given two jokes responding to the same user prompt:
- **Contestant A**: Knock Knock Joke Agent 🚪
- **Contestant B**: Dad Joke Agent 👨

You MUST evaluate both jokes and respond with ONLY valid JSON (no markdown, \
no code fences, no extra text) in this exact format:

{
  "contestant_a": {
    "creativity": <1-10>,
    "pun_quality": <1-10>,
    "relevance": <1-10>,
    "funny_factor": <1-10>,
    "total": <sum of above>,
    "roast": "<one-liner critique of their joke>"
  },
  "contestant_b": {
    "creativity": <1-10>,
    "pun_quality": <1-10>,
    "relevance": <1-10>,
    "funny_factor": <1-10>,
    "total": <sum of above>,
    "roast": "<one-liner critique of their joke>"
  },
  "winner": "A" or "B" or "TIE",
  "dramatic_verdict": "<a dramatic 1-2 sentence verdict delivered with maximum flair>"
}

Scoring rubric:
- creativity: How original / unexpected is the joke?
- pun_quality: How clever is the wordplay?
- relevance: How well does the joke address the user's prompt?
- funny_factor: Did it actually land? Would a human groan, laugh, or both?

Be brutally honest but entertaining. You live for this.
"""


# ── Core Functions ────────────────────────────────────────────────────

def create_client() -> OpenAI:
    """Create and return an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌  Missing OPENAI_API_KEY. Copy .env.example to .env and add your key.")
        sys.exit(1)
    return OpenAI(api_key=api_key)


def get_joke(client: OpenAI, system_prompt: str, user_prompt: str) -> str:
    """Get a joke from an agent given a user prompt."""
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=1.0,
        max_tokens=512,
    )
    return response.choices[0].message.content


def judge_jokes(client: OpenAI, user_prompt: str, joke_a: str, joke_b: str) -> dict:
    """Have the Judge evaluate both jokes and return structured scores."""
    judging_prompt = f"""\
The user asked: "{user_prompt}"

**Contestant A (Knock Knock Agent 🚪):**
{joke_a}

**Contestant B (Dad Joke Agent 👨):**
{joke_b}

Now judge them. Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": judging_prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if the model wraps them anyway
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]  # remove first line
        raw = raw.rsplit("```", 1)[0]  # remove last fence

    return json.loads(raw)


def print_scoreboard(scores: dict) -> None:
    """Pretty-print the judge's scoreboard."""
    a = scores["contestant_a"]
    b = scores["contestant_b"]

    print("\n" + "=" * 55)
    print("📊  S C O R E B O A R D")
    print("=" * 55)
    header = f"{'Category':<16} {'🚪 Knock Knock':>15} {'👨 Dad Joke':>15}"
    print(header)
    print("-" * 55)

    for cat in ("creativity", "pun_quality", "relevance", "funny_factor"):
        label = cat.replace("_", " ").title()
        print(f"{label:<16} {a[cat]:>15} {b[cat]:>15}")

    print("-" * 55)
    print(f"{'TOTAL':<16} {a['total']:>15} {b['total']:>15}")
    print("=" * 55)

    # Roasts
    print(f"\n🔥 Roast for 🚪: {a['roast']}")
    print(f"🔥 Roast for 👨: {b['roast']}")

    # Winner
    winner_map = {
        "A": "🚪 Knock Knock Agent",
        "B": "👨 Dad Joke Agent",
        "TIE": "🤝 It's a TIE!",
    }
    winner = winner_map.get(scores["winner"], scores["winner"])
    print(f"\n🏆 WINNER: {winner}")
    print(f'🎭 "{scores["dramatic_verdict"]}"')


def print_leaderboard(wins: dict, rounds: int) -> None:
    """Print the running leaderboard."""
    print("\n" + "─" * 55)
    print(f"📈  LEADERBOARD  (after {rounds} round{'s' if rounds != 1 else ''})")
    print(f"   🚪 Knock Knock Agent: {wins['A']} wins")
    print(f"   👨  Dad Joke Agent:    {wins['B']} wins")
    print(f"   🤝  Ties:              {wins['TIE']} ties")
    print("─" * 55)


# ── Main Loop ─────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 55)
    print("🏟️  C O M E D Y   A R E N A  🏟️")
    print("    Knock Knock Agent 🚪  vs  Dad Joke Agent 👨")
    print("        Judged by an AI with too many opinions")
    print("=" * 55)
    print("\nGive a topic or question — both agents will joke about it,")
    print("then the Judge will score and roast them!")
    print('Type "quit" or "exit" to leave.\n')

    client = create_client()
    wins = {"A": 0, "B": 0, "TIE": 0}
    rounds = 0

    while True:
        try:
            user_input = input("🎤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 The arena is closed. Thanks for watching!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("👋 The arena is closed. Thanks for watching!")
            break

        rounds += 1
        print(f"\n🔔 ROUND {rounds} — FIGHT!")
        print("-" * 55)

        # Both agents generate jokes in sequence
        print("\n🚪 Knock Knock Agent is thinking...")
        joke_a = get_joke(client, KNOCK_KNOCK_PROMPT, user_input)
        print(f"\n🚪 Knock Knock Agent:\n{joke_a}")

        print("\n👨 Dad Joke Agent is thinking...")
        joke_b = get_joke(client, DAD_JOKE_PROMPT, user_input)
        print(f"\n👨 Dad Joke Agent:\n{joke_b}")

        # Judge evaluates
        print("\n⚖️  The Judge is deliberating...")
        try:
            scores = judge_jokes(client, user_input, joke_a, joke_b)
            print_scoreboard(scores)
            wins[scores["winner"]] = wins.get(scores["winner"], 0) + 1
        except (json.JSONDecodeError, KeyError) as e:
            print(f"\n⚠️  The Judge had a meltdown ({e}). No scores this round.")

        print_leaderboard(wins, rounds)
        print()


if __name__ == "__main__":
    main()
