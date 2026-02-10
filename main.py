"""
🌀 AllTheVibes — AI Chaos Agent Toolkit for Wild Hackathons

A collection of AI-powered agents that bring order (and entertainment)
to the chaos of hackathon development.

Usage:
    python main.py                    # Interactive agent router
    python main.py readme             # Generate AI-powered README
    python main.py whisper            # Commit Whisperer narration
    python main.py visualize          # Chaos Visualizer dashboard
    python main.py review [file]      # AI Code Reviewer
    python main.py sql [query]        # Natural language → SQL
    python main.py router             # Interactive agent router
"""

import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    banner = """
🌀 [bold cyan]AllTheVibes[/bold cyan] — AI Chaos Agent Toolkit

  [green]readme[/]      → 🤖 Generate AI-powered README
  [magenta]whisper[/]     → 🔮 Commit Whisperer narration
  [yellow]visualize[/]   → 📊 Chaos Visualizer dashboard
  [red]review[/]      → 🔍 AI Code Reviewer [dim](+ optional file path)[/dim]
  [green]sql[/]         → 🗄️ Natural language → SQL
  [blue]router[/]      → 🔀 Interactive agent router

  [dim]Or just run with no args for the interactive router![/dim]
"""
    console.print(Panel(banner, title="🌀 AllTheVibes", border_style="cyan"))


def main():
    args = sys.argv[1:]

    if not args:
        print_banner()
        from agents.router import run as run_router
        run_router()
        return

    command = args[0].lower()

    if command == "readme":
        from agents.repo_copilot import run as run_copilot
        run_copilot()

    elif command == "whisper":
        from agents.commit_whisperer import run as run_whisperer
        run_whisperer()

    elif command == "visualize":
        from agents.chaos_visualizer import run as run_viz
        run_viz()

    elif command == "review":
        from agents.code_reviewer import run as run_reviewer
        filepath = args[1] if len(args) > 1 else None
        run_reviewer(filepath)

    elif command == "sql":
        from agents.sql_generator import run as run_sql
        query = " ".join(args[1:]) if len(args) > 1 else None
        run_sql(query)

    elif command == "router":
        from agents.router import run as run_router
        run_router()

    elif command in ("help", "--help", "-h"):
        print_banner()

    else:
        from rich.console import Console
        console = Console()
        console.print(f"\n❓ Unknown command: [red]{command}[/red]")
        print_banner()


if __name__ == "__main__":
    main()
