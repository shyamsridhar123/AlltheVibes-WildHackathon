"""
🔀 Agent Router — classifies user intent and routes to the right agent.
A tiny but impressive demo of agentic AI routing.
"""

from config import chat


AGENT_REGISTRY = {
    "repo_copilot": "Analyze repo structure and generate README",
    "commit_whisperer": "Narrate recent commit activity",
    "chaos_visualizer": "Visualize git history and contributor stats",
    "code_reviewer": "Review code files with AI feedback",
    "sql_generator": "Generate SQL from natural language",
    "out_of_scope": "Request doesn't match any agent capability",
}


def classify_intent(user_input: str) -> dict:
    """Use AI to classify user intent and pick the best agent."""
    agent_list = "\n".join(f"- {k}: {v}" for k, v in AGENT_REGISTRY.items())

    prompt = f"""You are an intent classifier for an AI agent system.
Given the user's request, classify it into one of these agents:

{agent_list}

User request: "{user_input}"

Respond in this EXACT format (no markdown, no explanation):
agent: <agent_name>
confidence: <high|medium|low>
reasoning: <one sentence explaining why>
"""

    system = "You are a precise intent classifier. Always respond in the exact format requested."
    result = chat(prompt, system=system, temperature=0.2)

    # Parse response
    parsed = {}
    for line in result.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            parsed[key.strip().lower()] = val.strip()

    return {
        "agent": parsed.get("agent", "out_of_scope"),
        "confidence": parsed.get("confidence", "low"),
        "reasoning": parsed.get("reasoning", "Could not determine intent"),
        "raw": result,
    }


def route(user_input: str) -> dict:
    """Classify and route a user request."""
    classification = classify_intent(user_input)

    agent_name = classification["agent"]
    if agent_name not in AGENT_REGISTRY:
        agent_name = "out_of_scope"
        classification["agent"] = agent_name

    return classification


def run():
    """Interactive routing demo."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    console.print("\n🔀 [bold blue]Agent Router[/] — Tell me what you need!\n")
    console.print("Type a request and I'll route it to the right agent.")
    console.print("Type 'quit' to exit.\n")

    while True:
        user_input = console.input("[bold green]You → [/]")
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("\n👋 Bye!\n")
            break

        result = route(user_input)

        table = Table(title="🔀 Routing Result")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Agent", f"🤖 {result['agent']}")
        table.add_row("Confidence", result["confidence"])
        table.add_row("Reasoning", result["reasoning"])
        console.print(table)

        # Actually run the agent if we can
        if result["agent"] == "repo_copilot":
            from agents.repo_copilot import run as run_copilot
            run_copilot()
        elif result["agent"] == "commit_whisperer":
            from agents.commit_whisperer import run as run_whisperer
            run_whisperer()
        elif result["agent"] == "chaos_visualizer":
            from agents.chaos_visualizer import run as run_viz
            run_viz()
        elif result["agent"] == "code_reviewer":
            console.print("\n🔍 [yellow]Tip: run `python main.py review <file>` to review a specific file[/]\n")
        elif result["agent"] == "sql_generator":
            from agents.sql_generator import run as run_sql
            run_sql(user_input)
        elif result["agent"] == "out_of_scope":
            console.print("\n🚫 [red]That's out of scope for our agents. Try something else![/]\n")
        console.print()


if __name__ == "__main__":
    run()
