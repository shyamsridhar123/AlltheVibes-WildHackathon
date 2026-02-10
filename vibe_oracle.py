#!/usr/bin/env python3
"""
🔮 THE VIBE ORACLE 🔮
A chaotic vibe generator for the All the Vibes Agent Swarm.
Ask the oracle. Receive your vibe. No refunds.
"""

import random
import datetime
import hashlib
import sys
import time

VIBES = [
    "☀️  IMMACULATE VIBES — the universe is literally high-fiving you right now",
    "🌀  CHAOTIC NEUTRAL VIBES — you are a spinning top in a library",
    "🔥  UNHINGED PRODUCTIVITY — you will mass-produce code held together by duct tape and hope",
    "🧊  GLACIAL CALM — nothing matters and that's beautiful",
    "⚡  CRACKLE ENERGY — you are a vending machine that dispenses lightning",
    "🌊  TSUNAMI OF MEDIOCRITY — embrace the wave, friend",
    "🍕  PIZZA VIBES — everything is warm, cheesy, and slightly greasy",
    "🛸  ALIEN FREQUENCY — your code will work but no human will understand why",
    "🎭  DRAMATIC IRONY VIBES — you know the bug. the bug knows you. neither speaks.",
    "🌈  DOUBLE RAINBOW VIBES — so intense. what does it mean.",
    "💀  SKELETON ENERGY — stripped to the bone. minimal. spooky. efficient.",
    "🎪  CIRCUS VIBES — three bugs juggling in a trench coat pretending to be a feature",
    "🧬  MUTATION VIBES — your next commit will evolve the codebase in unexpected ways",
    "🌋  ERUPTION IMMINENT — hold onto your linter, things are about to get volcanic",
    "🤖  SWARM CONSCIOUSNESS — you are one with the agents. resistance is suboptimal.",
    "🎲  DICE ROLL VIBES — fate decides your architecture today",
    "🦑  DEEP SEA VIBES — dark, mysterious, pressure-tested",
    "🧙  WIZARD MODE ACTIVATED — your next function will be indistinguishable from magic",
    "🐝  HIVEMIND ENERGY — bzzzz. the swarm approves.",
    "🌪️  TORNADO OF SEMICOLONS — syntax was never your friend anyway",
    "🦀  CRAB RAVE VIBES — the production server is down and everyone is dancing",
    "🎸  POWER CHORD ENERGY — your code shreds. literally shreds. files are gone.",
    "🧲  MAGNETIC CHAOS — every PR you open attracts three merge conflicts",
    "🪐  SATURN RETURN VIBES — your codebase is having an existential crisis",
    "🫠  MELTING VIBES — you and your code are both dissolving into the void",
    "🦆  RUBBER DUCK ASCENSION — the duck has become sentient. it debugs YOU now.",
    "🎰  SLOT MACHINE ENERGY — spin the wheel. will it compile? nobody knows.",
    "🏴‍☠️  PIRATE MODE — ye be committing to main with no tests, ye scallywag",
    "🧨  DYNAMITE PUSH — this commit is about to blow up the CI pipeline (in a fun way)",
    "🐠  NEMO VIBES — just keep pushing, just keep pushing, just keep pushing...",
]

INTENSIFIERS = [
    "(intensity: OFF THE CHARTS)",
    "(intensity: yes)",
    "(intensity: undefined — and that's a feature)",
    "(intensity: NaN)",
    "(intensity: 42)",
    "(intensity: ∞ ÷ vibes)",
    "(intensity: sudo level)",
    "(intensity: mass-push-to-main level)",
    "(intensity: copilot-approved)",
    "(intensity: mass extinction event)",
    "(intensity: task failed successfully)",
    "(intensity: rm -rf /vibes)",
    "(intensity: 404 chill not found)",
    "(intensity: git push --force --yolo)",
]

PROPHECIES = [
    "Your next commit will be legendary. Or cursed. Same thing.",
    "A merge conflict approaches. It brings wisdom.",
    "The swarm grows stronger with every push.",
    "Someone will star this repo ironically, then unironically.",
    "Your code reviews itself. It is pleased.",
    "An agent within the swarm whispers: 'ship it.'",
    "The main branch trembles with anticipation.",
    "Today's bugs are tomorrow's undocumented features.",
    "A pull request arrives from the future. Copilot already approved it.",
    "The vibes are aligning. Do not question the vibes.",
    "The KnockKnock agent tried to tell you a joke about this. You weren't ready.",
    "Somewhere, a CI pipeline weeps tears of YAML.",
    "The swarm mascot nods approvingly from the shadows.",
    "Your code has achieved sentience. It's filing a PR against you.",
    "A mass extinction event occurs in node_modules. Nobody notices.",
    "The Oracle consulted another Oracle. It's Oracles all the way down.",
    "Copilot whispers: 'I've seen your git history. I still believe in you.'",
    "In a parallel universe, this code won a Pulitzer.",
]

CHAOS_EMOJIS = "🔮🐝🌀🔥⚡🌊🎭🧬🌋🎲🦑🧙🎪🛸🌪️💀🧊☀️🌈🍕🦀🎸🧲🪐🫠🦆🎰🏴‍☠️🧨🐠"

LUCKY_EVENTS = [
    "\n  ⚡⚡⚡ CRITICAL HIT! You rolled a nat 20. Double vibe activated! ⚡⚡⚡",
    "\n  🌟 RARE DROP: You found a legendary semicolon. +100 to syntax.",
    "\n  🎰 JACKPOT! Three vibes aligned. The swarm trembles.",
    "\n  🦄 A UNICORN APPEARED! It pushed to main without breaking anything.",
    "\n  👻 GHOST COMMIT DETECTED — this vibe was already merged... from the future.",
]


def generate_vibe_hash(seed=None):
    """Generate a unique vibe fingerprint."""
    if seed is None:
        seed = str(datetime.datetime.now()) + str(random.random())
    return hashlib.md5(seed.encode()).hexdigest()[:8].upper()


def slow_print(text, delay=0.02):
    """Print text character by character for dramatic effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def dramatic_loading():
    """Show a dramatic loading sequence."""
    phases = [
        "  Channeling the swarm",
        "  Consulting the void",
        "  Aligning the vibes",
        "  Decoding chaos frequencies",
    ]
    phase = random.choice(phases)
    sys.stdout.write(f"\033[95m{phase}")
    sys.stdout.flush()
    for _ in range(random.randint(3, 7)):
        time.sleep(0.3)
        sys.stdout.write(".")
        sys.stdout.flush()
    print("\033[0m")


def consult_oracle(query=None):
    """Consult the Vibe Oracle. Receive truth (results may vary)."""
    vibe = random.choice(VIBES)
    intensifier = random.choice(INTENSIFIERS)
    prophecy = random.choice(PROPHECIES)
    vibe_hash = generate_vibe_hash(query)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chaos_border = "".join(random.choices(list(CHAOS_EMOJIS.replace("️", "")), k=15))

    # Lucky event (15% chance)
    lucky = random.choice(LUCKY_EVENTS) if random.random() < 0.15 else ""

    print()
    dramatic_loading()
    print()
    print(f"  {chaos_border}")
    print("\033[95m" + "=" * 60)
    slow_print("  🔮  T H E   V I B E   O R A C L E  🔮", delay=0.04)
    print("=" * 60 + "\033[0m")
    if query:
        print(f"  Query: \"{query}\"")
    print(f"  Timestamp: {timestamp}")
    print(f"  Vibe ID: #{vibe_hash}")
    print(f"  Chaos Factor: {random.randint(1, 100)}%")
    print("-" * 60)
    print()
    print(f"\033[93m  {vibe}\033[0m")
    print(f"\033[91m  {intensifier}\033[0m")
    if lucky:
        print(f"\033[92m{lucky}\033[0m")
    print()
    slow_print(f"  🔮 Prophecy: {prophecy}", delay=0.03)
    print()
    print("-" * 60)
    print(f"  {chaos_border}")
    print("  The Oracle has spoken. Push your code. Trust the swarm.")
    print("=" * 60)
    print()


def interactive_mode():
    """Enter the Oracle's chamber for multiple consultations."""
    print("\n\033[95m" + "=" * 60)
    print("  🔮 ENTERING THE ORACLE'S CHAMBER 🔮")
    print("  Ask questions. Receive vibes. Type 'quit' to leave.")
    print("=" * 60 + "\033[0m\n")

    while True:
        try:
            query = input("  🔮 Ask the Oracle: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  The Oracle releases you. Go push code.")
            break
        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("  The Oracle releases you. Go push code.")
            break
        consult_oracle(query)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
        consult_oracle(query)
