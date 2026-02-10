"""
📊 Chaos Visualizer — reads git history and turns it into
a beautiful ASCII/markdown visualization of hackathon chaos.
"""

import subprocess
from collections import Counter
from config import chat


def get_contributor_stats() -> dict:
    """Get commit counts per author."""
    try:
        result = subprocess.run(
            ["git", "shortlog", "-sn", "--all"],
            capture_output=True, text=True, timeout=10
        )
        stats = {}
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line:
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    stats[parts[1].strip()] = int(parts[0].strip())
        return stats or {"(no contributors yet)": 0}
    except Exception:
        return {"(git error)": 0}


def get_file_change_frequency(n: int = 50) -> dict:
    """Get the most frequently changed files."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--pretty=format:", "--name-only"],
            capture_output=True, text=True, timeout=10
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return dict(Counter(files).most_common(15))
    except Exception:
        return {"(no data)": 0}


def get_commit_timeline(n: int = 30) -> str:
    """Get commit timestamps for timeline."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--pretty=format:%ai | %an | %s"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() or "(no commits)"
    except Exception:
        return "(git not available)"


def make_bar(value: int, max_val: int, width: int = 30) -> str:
    """Create an ASCII bar."""
    if max_val == 0:
        return ""
    filled = int((value / max_val) * width)
    return "█" * filled + "░" * (width - filled)


def visualize() -> str:
    """Generate a complete chaos visualization."""
    contributors = get_contributor_stats()
    hot_files = get_file_change_frequency()
    timeline = get_commit_timeline()

    # Build ASCII visualization
    output_parts = []

    # Contributors section
    output_parts.append("## 👥 Contributors Leaderboard\n")
    max_commits = max(contributors.values()) if contributors else 1
    for name, count in sorted(contributors.items(), key=lambda x: -x[1]):
        bar = make_bar(count, max_commits, 25)
        output_parts.append(f"  {name:<25} {bar} {count} commits")

    # Hot files section
    output_parts.append("\n## 🔥 Most Changed Files\n")
    max_changes = max(hot_files.values()) if hot_files else 1
    for fname, count in sorted(hot_files.items(), key=lambda x: -x[1]):
        bar = make_bar(count, max_changes, 25)
        output_parts.append(f"  {fname:<35} {bar} {count}x")

    viz_text = "\n".join(output_parts)

    # Get AI commentary
    prompt = f"""You are analyzing a hackathon repo's git activity. Based on the data below,
provide a brief, entertaining "Chaos Report" (max 200 words).

Include:
- Overall chaos level (1-10 with emoji)
- Who's the MVP and why
- Any suspicious patterns
- A prediction for what happens next

DATA:
{viz_text}

TIMELINE:
{timeline}
"""

    system = "You are a witty data analyst commenting on hackathon chaos. Be brief and entertaining."
    ai_commentary = chat(prompt, system=system, temperature=0.8)

    return viz_text + "\n\n## 🧠 AI Chaos Report\n\n" + ai_commentary


def run():
    """Run the Chaos Visualizer."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()
    console.print("\n📊 [bold yellow]Chaos Visualizer[/] — Mapping the madness...\n")

    result = visualize()
    console.print(Panel(Markdown(result), title="📊 Chaos Dashboard", border_style="yellow"))
    return result


if __name__ == "__main__":
    run()
