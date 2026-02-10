"""
🔍 AI Code Reviewer — reviews code with honest (and sometimes sarcastic) feedback.
> "This function exists, but I'm not sure why."
"""

import os
from config import chat


def read_file(filepath: str) -> str:
    """Read a file's contents."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(5000)  # first 5k chars
    except Exception as e:
        return f"(could not read file: {e})"


def review_file(filepath: str) -> str:
    """Generate an AI code review for a file."""
    content = read_file(filepath)
    filename = os.path.basename(filepath)

    prompt = f"""You are reviewing code from a wild AI hackathon. The code may be chaotic,
brilliant, or both. Review it with a mix of genuine technical feedback and humor.

For each significant section, provide:
1. 🎯 What it does (or tries to do)
2. ✅ What's good about it
3. ⚠️ What's concerning
4. 💡 One suggestion
5. 🎭 A sarcastic one-liner comment (like a code review from a tired senior dev at 3am)

End with:
- Overall score: X/10
- Hackathon Viability: will it demo?
- One encouraging thing

FILE: {filename}
```
{content}
```
"""

    system = """You are a senior developer doing code review at a hackathon at 3am.
You're tired but insightful. Your reviews are technically accurate but delivered
with the energy of someone who's had too much coffee. Use emoji."""

    return chat(prompt, system=system, temperature=0.8)


def review_all_python_files(root: str = ".") -> str:
    """Find and review all Python files in the repo."""
    ignore = {".git", "__pycache__", ".venv", "node_modules"}
    files_reviewed = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore]
        for f in filenames:
            if f.endswith(".py"):
                fpath = os.path.join(dirpath, f)
                files_reviewed.append(fpath)

    if not files_reviewed:
        return "No Python files found to review. The repo is... minimalist."

    results = []
    for fpath in files_reviewed[:5]:  # limit to 5 files
        results.append(f"\n{'='*60}\n📄 Reviewing: {fpath}\n{'='*60}\n")
        results.append(review_file(fpath))

    return "\n".join(results)


def run(filepath: str = None):
    """Run the AI Code Reviewer."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()
    console.print("\n🔍 [bold red]AI Code Reviewer[/] — Judging your code...\n")

    if filepath and os.path.isfile(filepath):
        result = review_file(filepath)
    else:
        console.print("[yellow]No specific file given — reviewing all Python files...[/]\n")
        result = review_all_python_files()

    console.print(Panel(Markdown(result), title="🔍 Code Review", border_style="red"))
    return result


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    run(filepath)
