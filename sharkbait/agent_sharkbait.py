#!/usr/bin/env python3
"""
🦈 AGENT SHARKBAIT 🦈
"Shark bait, ooh ha ha!"

A code review agent that roams the repo like a shark through the ocean,
gives every file a dramatic ocean-themed review, rates code on the
Sharkbait Scale™, and dispenses unsolicited nautical wisdom.

No APIs. No dependencies. No mercy. Just sharks.

Usage:
    python sharkbait/agent_sharkbait.py                    # Review random file
    python sharkbait/agent_sharkbait.py <filename>         # Review specific file
    python sharkbait/agent_sharkbait.py --patrol            # Review ALL files
    python sharkbait/agent_sharkbait.py --roast <filename>  # Extra spicy review
    python sharkbait/agent_sharkbait.py --initiation        # Join the Tank Gang
"""

import os
import sys
import random
import time
import hashlib
import glob
from pathlib import Path

# ============================================================
# 🦈 SHARKBAIT LORE
# ============================================================

SHARK_ASCII = r"""
                              ___
                         ____/   \___
                   _____/   '       /
             ___--'         \  <    |
        __--'   \    (   )   \     /
   __--'         `--__\___/--' \  |
  '---___              ^       _`-'
         ```----_______/  \---'
              SHARKBAIT OOH HA HA!
"""

MINI_SHARK = "🦈"

TANK_GANG = [
    ("Gill", "the scarred leader", "This code has been through things. I respect it."),
    ("Bloat", "the pufferfish", "This file is... inflating... I'M ABOUT TO BLOW!"),
    ("Peach", "the starfish", "I've been stuck to this codebase for 3 hours. Here's what I see."),
    ("Jacques", "the cleaner shrimp", "I am ashamed. *scrubs code furiously*"),
    ("Gurgle", "the germaphobe", "Do NOT touch this code without sanitizing your inputs first."),
    ("Deb (& Flo)", "the split personality", "I love this code! / No you don't! / Yes I do!"),
    ("Bubbles", "the bubble obsessed", "BUBBLES! ...sorry, I mean, nice O(n) complexity."),
    ("Nemo", "the brave one", "Just keep pushing, just keep pushing..."),
]

# ============================================================
# 🦈 REVIEW TEMPLATES
# ============================================================

OPENING_LINES = [
    "The shark circles your code... sensing weakness...",
    "A dorsal fin emerges from the depths of your repo...",
    "Agent Sharkbait has detected prey — er, code — in the water...",
    "The ocean is vast. Your code is small. Let's see if it survives.",
    "*Jaws theme intensifies*",
    "Shark bait, ooh ha ha! Let me take a bite of this file...",
    "The Tank Gang has assembled to review your contribution.",
    "From the deep abyss of the git log, a review surfaces...",
]

CODE_COMPLIMENTS = [
    "Clean as coral reef water on a calm day 🐠",
    "This function flows like a gentle current. Smooth.",
    "I tried to find a bug but it swam away too fast.",
    "Even the sharks respect this level of craftsmanship.",
    "This code could navigate the East Australian Current no problem.",
    "Gill would nod approvingly. That's the highest honor.",
    "Jacques wouldn't even need to clean this. Immaculate.",
    "The Tank Gang unanimously approves. That NEVER happens.",
]

CODE_ROASTS = [
    "This code looks like it was written during a feeding frenzy.",
    "I've seen cleaner things in the bottom of a fish tank.",
    "Bloat just looked at this file and inflated to maximum capacity.",
    "Jacques fainted. The mess was too much for him.",
    "This function has more side effects than a pufferfish has spines.",
    "The variable naming here is... creative. Like abstract art. Underwater abstract art.",
    "Gurgle just sanitized his entire terminal after reading this.",
    "Even Dory couldn't forget how bad this indentation is.",
    "This code has the structural integrity of a sandcastle at high tide.",
    "Somewhere, a senior developer just felt a disturbance in the force.",
    "The sharks aren't circling because they're interested. They're confused.",
    "P. Sherman, 42 Wallaby Way — that's where I'd recommend filing this code.",
]

MEDIUM_TAKES = [
    "Acceptable. The sharks will let this pass... for now.",
    "It's not elegant, but it won't sink the ship. Probably.",
    "Peach has seen worse. Peach has seen better. Peach has seen... everything.",
    "Mid-ocean tier. Not the surface, not the abyss. Just... floating.",
    "The code works, but it works the way a fish walks. Technically possible.",
    "60% of the time, this works every time.",
    "It compiles. In the ocean, that's called 'not drowning.' Congrats.",
]

NAUTICAL_WISDOM = [
    "Fish are friends, not food. But your bugs? Those are PREY.",
    "Just keep swimming, just keep swimming — through the merge conflicts.",
    "The ocean doesn't care about your linter settings. Neither does this repo.",
    "A shark never looks back. Always commit forward.",
    "In the reef of code, every function is a hiding spot for bugs.",
    "The current will carry your code to production. Ready or not.",
    "Even the smallest fish can make the biggest splash... in the git log.",
    "What do we do? We swim, swim, push, push, merge, merge.",
    "The sea is dark and full of technical debt.",
    "You can't spell 'sharkbait' without 'AI'. Well, you can. But don't.",
]

SHARKBAIT_SCALE = [
    ("🦈🦈🦈🦈🦈", "APEX PREDATOR", "Top of the food chain. This code HUNTS."),
    ("🦈🦈🦈🦈🐟", "GREAT WHITE", "Fearsome. Respected. Occasionally misunderstood."),
    ("🦈🦈🦈🐟🐟", "REEF SHARK", "Solid. Reliable. Won't win awards but won't eat you either."),
    ("🦈🦈🐟🐟🐟", "NURSE SHARK", "Passive. Mostly harmless. Sleeps on the ocean floor."),
    ("🦈🐟🐟🐟🐟", "GUPPY", "Small. Fragile. Might get eaten by the first code review."),
    ("🐟🐟🐟🐟🐟", "PLANKTON", "At the bottom of the food chain. But hey, even plankton are essential."),
]

FILE_REACTIONS = {
    ".py": "Ah, Python. The clownfish of programming languages. Colorful, popular, swims well.",
    ".js": "JavaScript. The jellyfish of code. Beautiful from afar. Painful up close.",
    ".ts": "TypeScript. JavaScript wearing a suit of armor. The sharks approve of type safety.",
    ".md": "Markdown. The coral of the codebase. Pretty, structural, occasionally sharp.",
    ".yml": "YAML. The anglerfish of config files. Looks simple. LIES.",
    ".yaml": "YAML. The anglerfish of config files. Looks simple. LIES.",
    ".json": "JSON. Clean, structured, no surprises. The dolphin of data formats.",
    ".html": "HTML. The skeleton of the web. Every reef needs a foundation.",
    ".css": "CSS. Where specificity wars make actual shark battles look peaceful.",
    ".sh": "Shell script. Raw power. Like a shark with no safety features.",
    ".env": "Environment file. Secrets of the deep. 🤫",
    ".txt": "A text file. The sea cucumber of file types. It exists.",
    ".gitignore": "The bouncer of the repo. Deciding who gets in and who stays out.",
}


def color(text, c):
    """ANSI color wrapper."""
    codes = {"r": "91", "g": "92", "y": "93", "b": "94", "m": "95", "c": "96", "w": "97", "bold": "1"}
    return f"\033[{codes.get(c, '0')}m{text}\033[0m"


def slow_print(text, delay=0.02):
    """Dramatic text reveal."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def shark_fin_animation():
    """A shark fin crosses the terminal."""
    width = 50
    fin = "   /\\ "
    body = "~^^~^^~"
    for i in range(0, width, 3):
        frame = " " * i + fin + "\n" + "~" * i + body + "~" * (width - i)
        sys.stdout.write(f"\r{color(frame, 'c')}")
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write("\033[F")  # Move cursor up
    print("\n")


def analyze_file(filepath):
    """Analyze a file and generate review metrics."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (FileNotFoundError, IsADirectoryError):
        return None

    lines = content.split("\n")
    stats = {
        "lines": len(lines),
        "chars": len(content),
        "empty_lines": sum(1 for l in lines if l.strip() == ""),
        "longest_line": max((len(l) for l in lines), default=0),
        "has_comments": any(l.strip().startswith("#") or l.strip().startswith("//") for l in lines),
        "has_todos": any("TODO" in l or "FIXME" in l or "HACK" in l for l in lines),
        "has_emoji": any(ord(c) > 127 for c in content),
        "extension": Path(filepath).suffix.lower(),
        "filename": Path(filepath).name,
        "hash": hashlib.sha256(content.encode()).hexdigest()[:8].upper(),
    }

    # Generate a deterministic-ish but fun score
    seed = int(stats["hash"], 16)
    random.seed(seed)
    stats["score"] = random.randint(0, 5)
    random.seed()  # Re-randomize

    return stats


def review_file(filepath, roast_mode=False):
    """Generate a full Sharkbait review for a file."""
    stats = analyze_file(filepath)
    if stats is None:
        print(color(f"  🦈 File not found: {filepath}. It swam away.", "r"))
        return

    # Who's reviewing?
    reviewer_name, reviewer_title, reviewer_quote = random.choice(TANK_GANG)
    scale_emoji, scale_name, scale_desc = SHARKBAIT_SCALE[min(5, max(0, 5 - stats["score"]))]

    # File type reaction
    ext_reaction = FILE_REACTIONS.get(stats["extension"], "Unknown species. The sharks are intrigued.")

    print()
    print(color("=" * 60, "c"))
    slow_print(color(f"  🦈 AGENT SHARKBAIT — FILE REVIEW 🦈", "c"), delay=0.03)
    print(color("=" * 60, "c"))

    # Opening
    slow_print(color(f"\n  {random.choice(OPENING_LINES)}\n", "y"), delay=0.02)

    # File info
    print(color(f"  📄 File: {stats['filename']}", "w"))
    print(color(f"  🔬 Type: {ext_reaction}", "m"))
    print(color(f"  📊 Lines: {stats['lines']} | Chars: {stats['chars']} | Empty: {stats['empty_lines']}", "w"))
    print(color(f"  🧬 File DNA: #{stats['hash']}", "b"))
    if stats["longest_line"] > 120:
        print(color(f"  ⚠️  Longest line: {stats['longest_line']} chars. That line is longer than a blue whale.", "r"))
    if stats["has_todos"]:
        print(color(f"  📌 TODOs/FIXMEs detected. The sharks can smell procrastination.", "y"))
    if stats["has_emoji"]:
        print(color(f"  ✨ Contains emoji. The reef approves of self-expression.", "g"))

    # Rating
    print(color(f"\n  {'─' * 40}", "c"))
    print(color(f"  SHARKBAIT SCALE™: {scale_emoji}", "c"))
    print(color(f"  Rating: {scale_name}", "bold"))
    print(color(f"  {scale_desc}", "w"))
    print(color(f"  {'─' * 40}", "c"))

    # Reviewer commentary
    print(color(f"\n  🐠 Reviewed by: {reviewer_name} ({reviewer_title})", "g"))
    print(color(f"  💬 \"{reviewer_quote}\"", "g"))

    # The actual review
    print(color(f"\n  📝 REVIEW:", "y"))
    if roast_mode:
        print(color(f"  🔥 {random.choice(CODE_ROASTS)}", "r"))
        print(color(f"  🔥 {random.choice(CODE_ROASTS)}", "r"))
    elif stats["score"] >= 4:
        print(color(f"  ✅ {random.choice(CODE_COMPLIMENTS)}", "g"))
    elif stats["score"] >= 2:
        print(color(f"  🔶 {random.choice(MEDIUM_TAKES)}", "y"))
    else:
        print(color(f"  🔥 {random.choice(CODE_ROASTS)}", "r"))

    # Nautical wisdom
    print(color(f"\n  🌊 Nautical Wisdom: {random.choice(NAUTICAL_WISDOM)}", "c"))

    print(color("\n" + "=" * 60, "c"))
    print()


def patrol_repo():
    """Review ALL files in the repo. The shark goes hunting."""
    print(color(SHARK_ASCII, "c"))
    slow_print(color("  🦈 SHARKBAIT PATROL MODE — Scanning the entire reef...\n", "y"), delay=0.03)

    repo_root = Path(__file__).parent.parent
    files = []
    for ext in ["*.py", "*.js", "*.ts", "*.md", "*.yml", "*.yaml", "*.json", "*.html", "*.css", "*.sh", "*.txt"]:
        files.extend(glob.glob(str(repo_root / "**" / ext), recursive=True))

    # Filter out .git
    files = [f for f in files if ".git" + os.sep not in f and "__pycache__" not in f]

    if not files:
        print(color("  🦈 No files found. The ocean is empty. Eerie.", "r"))
        return

    print(color(f"  🦈 {len(files)} files detected in the reef.\n", "c"))

    scores = []
    for filepath in files:
        stats = analyze_file(filepath)
        if stats:
            scale_emoji = SHARKBAIT_SCALE[min(5, max(0, 5 - stats["score"]))][0]
            name = os.path.relpath(filepath, repo_root)
            scores.append((name, stats["score"], scale_emoji))
            reviewer = random.choice(TANK_GANG)
            print(f"  {scale_emoji}  {color(name, 'w')} — {color(reviewer[2], 'c')}")

    # Summary
    avg = sum(s[1] for s in scores) / len(scores) if scores else 0
    print(color(f"\n  {'═' * 50}", "m"))
    print(color(f"  🦈 PATROL COMPLETE", "m"))
    print(color(f"  📊 Files scanned: {len(scores)}", "w"))
    print(color(f"  📈 Average Sharkbait Score: {avg:.1f}/5", "y"))

    if avg >= 4:
        print(color(f"  🏆 Verdict: APEX REEF. The sharks bow to this codebase.", "g"))
    elif avg >= 2.5:
        print(color(f"  🙂 Verdict: SURVIVABLE WATERS. Could be worse. Could be better.", "y"))
    else:
        print(color(f"  💀 Verdict: SHARK-INFESTED CODE. Swim at your own risk.", "r"))

    print(color(f"  {'═' * 50}\n", "m"))


def initiation():
    """The Tank Gang initiation ceremony."""
    print(color(SHARK_ASCII, "c"))
    print()
    slow_print(color("  🦈 THE TANK GANG INITIATION CEREMONY 🦈", "m"), delay=0.04)
    print()
    time.sleep(0.5)

    lines = [
        ("Gill", "State your name."),
        ("", "..."),
        ("Gill", "You shall henceforth be known as... SHARKBAIT."),
        ("All", "Shark bait! Ooh ha ha!"),
        ("All", "Shark bait! Ooh ha ha!"),
        ("All", "Shark bait! Ooh-ooh-ooh-ooh-ooh!"),
        ("Bloat", "Welcome to the repo, kid."),
        ("Peach", "I've been watching this codebase for days. You'll fit right in."),
        ("Jacques", "I SHALL clean your code. It is... filthy."),
        ("Gurgle", "Don't touch ANYTHING without tests. Oh wait, there are no tests."),
        ("Deb", "We're SO happy you're here! / No we're not! / YES WE ARE!"),
        ("Bubbles", "BUBBLES! ...I mean, COMMITS!"),
        ("Gill", "Now go. Push to main. Make the swarm proud."),
    ]

    for speaker, line in lines:
        if speaker:
            print(color(f"  {speaker}: ", "y") + color(f"\"{line}\"", "w"))
        else:
            print(color(f"  {line}", "w"))
        time.sleep(0.6)

    print()
    print(color("  ═══════════════════════════════════════", "c"))
    print(color("  🦈 You are now part of the Tank Gang. 🦈", "c"))
    print(color("  🦈 Go push code. The swarm awaits.     🦈", "c"))
    print(color("  ═══════════════════════════════════════", "c"))
    print()


def main():
    """Agent Sharkbait main entry point."""
    args = sys.argv[1:]

    if not args:
        # Review a random file from the repo
        repo_root = Path(__file__).parent.parent
        files = []
        for ext in ["*.py", "*.md", "*.yml", "*.js", "*.ts"]:
            files.extend(glob.glob(str(repo_root / "**" / ext), recursive=True))
        files = [f for f in files if ".git" + os.sep not in f and "__pycache__" not in f]
        if files:
            target = random.choice(files)
            review_file(target)
        else:
            print(color("  🦈 No files in the reef to review. Push some code!", "r"))

    elif args[0] == "--patrol":
        patrol_repo()

    elif args[0] == "--roast" and len(args) > 1:
        review_file(args[1], roast_mode=True)

    elif args[0] == "--initiation":
        initiation()

    else:
        review_file(args[0])


if __name__ == "__main__":
    main()
