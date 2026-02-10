"""
🤖 Repo Copilot — reads the repo structure and generates an AI-powered README summary.
Explains *what this repo currently is*, even if it's chaos.
"""

import os
import subprocess
from config import chat


def get_repo_tree(root: str = ".", max_depth: int = 3) -> str:
    """Walk the repo and return a tree-like string (ignoring .git, __pycache__, .venv)."""
    ignore = {".git", "__pycache__", ".venv", "node_modules", ".mypy_cache"}
    lines = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter ignored dirs in-place
        dirnames[:] = [d for d in dirnames if d not in ignore]

        depth = dirpath.replace(root, "").count(os.sep)
        if depth >= max_depth:
            dirnames.clear()
            continue

        indent = "  " * depth
        folder = os.path.basename(dirpath) or root
        lines.append(f"{indent}📁 {folder}/")

        sub_indent = "  " * (depth + 1)
        for f in sorted(filenames):
            lines.append(f"{sub_indent}📄 {f}")

    return "\n".join(lines)


def read_key_files(root: str = ".") -> str:
    """Read small text files that might explain the project."""
    snippets = []
    interesting = ["README.md", "main.py", "config.py", "requirements.txt", "pyproject.toml", "package.json"]

    for fname in interesting:
        fpath = os.path.join(root, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(2000)  # first 2k chars
                snippets.append(f"--- {fname} ---\n{content}")
            except Exception:
                pass
    return "\n\n".join(snippets) if snippets else "(no key files found)"


def get_recent_commits(n: int = 10) -> str:
    """Return last N commit messages."""
    try:
        result = subprocess.run(
            ["git", "log", f"--oneline", f"-{n}"],
            capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace"
        )
        return result.stdout.strip() or "(no commits yet)"
    except Exception:
        return "(git not available)"


def generate_readme(repo_path: str = ".") -> str:
    """Generate a README.md summary using AI."""
    tree = get_repo_tree(repo_path)
    files = read_key_files(repo_path)
    commits = get_recent_commits()

    prompt = f"""You are analyzing a GitHub repo for a hackathon. Based on the info below,
generate a fun, concise, informative README.md.

Include:
- A creative project title with emoji
- What this repo appears to be about
- Key files and what they do
- Recent activity summary
- A "How to run" section (best guess)
- A "Contributors" section placeholder

Be witty but informative. This is for a wild AI hackathon — embrace the chaos.

REPO STRUCTURE:
{tree}

KEY FILE CONTENTS:
{files}

RECENT COMMITS:
{commits}
"""

    system = "You are a senior developer who writes excellent README files with personality. Use markdown formatting."
    return chat(prompt, system=system, temperature=0.8)


def run(repo_path: str = "."):
    """Run the Repo Copilot and save README.md."""
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    console.print("\n🤖 [bold cyan]Repo Copilot[/] — Analyzing your repo...\n")

    readme_content = generate_readme(repo_path)

    # Display it
    console.print(Markdown(readme_content))

    # Save it
    out_path = os.path.join(repo_path, "README.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    console.print(f"\n✅ [green]README.md saved to {out_path}[/green]\n")
    return readme_content


if __name__ == "__main__":
    run()
