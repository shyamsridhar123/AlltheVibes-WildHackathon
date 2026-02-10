"""
🔮 Commit Whisperer — watches git commits and generates
hilarious, insightful summaries of what just happened.

> "Someone just added a half-working SQL generator at 2:41am."
"""

import subprocess
from datetime import datetime
from config import chat


def get_commit_log(n: int = 15) -> str:
    """Get recent commits with author, date, and message."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--pretty=format:%h | %an | %ar | %s"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() or "(no commits yet)"
    except Exception:
        return "(git not available)"


def get_diff_stats(n: int = 5) -> str:
    """Get diff stats for recent commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--stat", "--pretty=format:--- %h by %an ---"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()[:3000] or "(no diffs)"
    except Exception:
        return "(git not available)"


def whisper(n: int = 10) -> str:
    """Generate a witty summary of recent commit activity."""
    log = get_commit_log(n)
    stats = get_diff_stats(min(n, 5))
    now = datetime.now().strftime("%I:%M %p on %A")

    prompt = f"""You are the "Commit Whisperer" — a sarcastic, all-seeing narrator
of a chaotic hackathon git repo. It's currently {now}.

Based on the commit log and diff stats below, generate a dramatic,
funny play-by-play of what's been happening. Think of yourself as a
sports commentator for code commits.

Rules:
- Be witty and dramatic
- Call out patterns (rapid commits, large changes, suspicious file names)
- Give each contributor a personality based on their commits
- End with a "Chaos Score" from 1-10
- Use emoji generously
- Keep it under 500 words

COMMIT LOG:
{log}

DIFF STATS:
{stats}
"""

    system = "You are a hilarious tech commentator narrating a hackathon like it's a reality show. Be dramatic but insightful."
    return chat(prompt, system=system, temperature=0.9)


def run():
    """Run the Commit Whisperer."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()
    console.print("\n🔮 [bold magenta]Commit Whisperer[/] — Reading the git tea...\n")

    result = whisper()
    console.print(Panel(Markdown(result), title="🔮 The Whisper", border_style="magenta"))
    return result


if __name__ == "__main__":
    run()
