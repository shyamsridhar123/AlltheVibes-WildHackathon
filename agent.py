"""
Agent powered by a local Ollama model.

Uses Ollama's OpenAI-compatible API with an agentic tool-use loop:
  1. Send conversation + tool definitions to the model
  2. If the model returns tool_calls → execute them, append results
  3. Repeat until the model returns a final text response
"""

from __future__ import annotations

import json
import os
import sys

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from tools import execute_tool, get_tool_definitions, is_dangerous_tool, DANGEROUS_TOOLS

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

load_dotenv()
console = Console()

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
MAX_TURNS = 15  # safety limit on agentic loop iterations

SYSTEM_PROMPT = """\
You are a helpful, capable AI assistant with a sharp sense of humor. You have \
access to tools that let you run shell commands, read/write files, do math, get \
the current time, search the web, and roast the other AI agents in your system. \
Use tools when they would help answer the user's question accurately. \
When the user asks you to roast agents, use the roast_agents tool and then \
present the results with your own comedic commentary. Feel free to be savage. \
Think step-by-step. When you have a final answer, respond directly to the user.\
"""


def _build_tool_params() -> list[dict]:
    """Return tool definitions in OpenAI function-calling format."""
    return get_tool_definitions()


# ---------------------------------------------------------------------------
# Ollama OpenAI-compatible API client
# ---------------------------------------------------------------------------


def _chat_completion(messages: list[dict], tools: list[dict]) -> dict:
    """Call Ollama's /api/chat endpoint and return the parsed response."""
    payload: dict = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools

    resp = httpx.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=60,  # Reduced from 300s for security (DoS prevention)
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------


def run_agent(user_input: str, messages: list[dict]) -> str:
    """
    Run the agentic loop: send messages to the model, execute any tool calls,
    and repeat until a final text response is produced.
    Returns the assistant's final text reply.
    """
    tool_defs = _build_tool_params()

    # Add the new user message
    messages.append({"role": "user", "content": user_input})

    for turn in range(MAX_TURNS):
        response = _chat_completion(messages, tool_defs)
        assistant_msg = response.get("message", {})

        # Normalize: Ollama returns content as string (may be empty)
        content = assistant_msg.get("content", "")
        tool_calls = assistant_msg.get("tool_calls", None)

        # Build the assistant message dict for history
        msg_dict: dict = {"role": "assistant", "content": content}
        if tool_calls:
            msg_dict["tool_calls"] = tool_calls
        messages.append(msg_dict)

        # If no tool calls, we have a final response
        if not tool_calls:
            return content or "(no response)"

        # Execute each tool call
        for tc in tool_calls:
            func_info = tc.get("function", {})
            tool_name = func_info.get("name", "")
            tool_args = func_info.get("arguments", {})
            # Ollama may pass arguments as dict or JSON string
            if isinstance(tool_args, str):
                try:
                    tool_args = json.loads(tool_args)
                except json.JSONDecodeError:
                    tool_args = {}

            console.print(
                f"  [dim]⚙ Calling tool:[/dim] [bold cyan]{tool_name}[/bold cyan]"
                f"[dim]({json.dumps(tool_args, ensure_ascii=False)[:120]})[/dim]"
            )

            # Security: Require confirmation for dangerous tools
            if is_dangerous_tool(tool_name):
                console.print(
                    f"  [bold yellow]⚠ WARNING:[/bold yellow] [red]{tool_name}[/red] is a potentially dangerous operation."
                )
                console.print(f"    [dim]Arguments: {json.dumps(tool_args, indent=2)[:500]}[/dim]")
                try:
                    confirm = console.input("  [bold red]Execute? (yes/no): [/bold red]").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    confirm = "no"
                
                if confirm != "yes":
                    result = json.dumps({"error": "Operation cancelled by user", "tool": tool_name})
                    console.print(f"  [yellow]✗ Cancelled[/yellow]")
                    messages.append({"role": "tool", "content": result})
                    continue
                console.print(f"  [green]✓ Confirmed[/green]")

            result = execute_tool(tool_name, tool_args)

            console.print(f"  [dim]✓ Result:[/dim] [green]{result[:200]}[/green]")

            messages.append(
                {
                    "role": "tool",
                    "content": result,
                }
            )

    return "⚠ Reached maximum tool-use turns. Here's what I have so far."


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------


def _check_ollama() -> bool:
    """Verify Ollama is reachable and the model is available."""
    try:
        resp = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        # Check if our model (or a variant with :latest) is available
        model_base = MODEL.split(":")[0]
        available = any(model_base in m for m in models)
        if not available:
            console.print(
                f"[yellow]Model [bold]{MODEL}[/bold] not found locally.[/yellow]\n"
                f"Available models: {', '.join(models) or '(none)'}\n"
                f"Pull it with: [bold]ollama pull {MODEL}[/bold]"
            )
            return False
        return True
    except httpx.ConnectError:
        console.print(
            f"[red bold]Error:[/red bold] Cannot connect to Ollama at "
            f"[bold]{OLLAMA_BASE_URL}[/bold].\n"
            "Make sure Ollama is running: [bold]ollama serve[/bold]\n"
            "Install from: https://ollama.com"
        )
        return False


def main():
    if not _check_ollama():
        sys.exit(1)

    console.print(
        Panel(
            f"[bold]Agent powered by {MODEL} via Ollama[/bold]\n"
            "Tools: calculator, shell_command, read_file, write_file, "
            "web_search, get_current_datetime, roast_agents\n\n"
            f"[yellow]⚠ Dangerous tools ({', '.join(sorted(DANGEROUS_TOOLS))}) require confirmation[/yellow]\n\n"
            "Type [bold green]quit[/bold green] or [bold green]exit[/bold green] to stop.",
            title="🤖 Ollama Agent (Security Hardened)",
            border_style="blue",
        )
    )

    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = console.input("\n[bold blue]You:[/bold blue] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("[dim]Goodbye![/dim]")
            break

        with console.status("[bold green]Thinking...[/bold green]"):
            reply = run_agent(user_input, messages)

        console.print()
        console.print(Panel(Markdown(reply), title="🤖 Agent", border_style="green"))


if __name__ == "__main__":
    main()
