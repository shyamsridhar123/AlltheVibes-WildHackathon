"""
Agent powered by Claude Opus 4.5 on Azure AI Foundry.

Uses the Azure AI Inference SDK with an agentic tool-use loop:
  1. Send conversation + tool definitions to the model
  2. If the model returns tool_calls → execute them, append results
  3. Repeat until the model returns a final text response
"""

from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import (
    ChatCompletionsToolDefinition,
    ChatRequestMessage,
    FunctionDefinition,
    SystemMessage,
    UserMessage,
    AssistantMessage,
    ToolMessage,
)
from azure.core.credentials import AzureKeyCredential

from tools import execute_tool, get_tool_definitions

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

load_dotenv()
console = Console()

ENDPOINT = os.environ.get("AZURE_AI_ENDPOINT", "")
API_KEY = os.environ.get("AZURE_AI_API_KEY", "")
MODEL = os.environ.get("AZURE_AI_MODEL", "claude-opus-4-5-20250219")
MAX_TURNS = 15  # safety limit on agentic loop iterations

SYSTEM_PROMPT = """\
You are a helpful, capable AI assistant. You have access to tools that let you \
run shell commands, read/write files, do math, get the current time, and search \
the web. Use tools when they would help answer the user's question accurately. \
Think step-by-step. When you have a final answer, respond directly to the user.\
"""


def _build_tool_params() -> list[ChatCompletionsToolDefinition]:
    """Convert our tool registry into Azure SDK tool definitions."""
    tools = []
    for defn in get_tool_definitions():
        func = defn["function"]
        tools.append(
            ChatCompletionsToolDefinition(
                function=FunctionDefinition(
                    name=func["name"],
                    description=func["description"],
                    parameters=func["parameters"],
                )
            )
        )
    return tools


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------


def run_agent(user_input: str, messages: list[dict]) -> str:
    """
    Run the agentic loop: send messages to Claude, execute any tool calls,
    and repeat until a final text response is produced.
    Returns the assistant's final text reply.
    """
    client = ChatCompletionsClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(API_KEY),
    )
    tool_defs = _build_tool_params()

    # Add the new user message
    messages.append({"role": "user", "content": user_input})

    for turn in range(MAX_TURNS):
        # Build the SDK message objects from our dict history
        sdk_messages = _to_sdk_messages(messages)

        response = client.complete(
            model=MODEL,
            messages=sdk_messages,
            tools=tool_defs if tool_defs else None,
            temperature=1,  # Claude recommended default
            max_tokens=4096,
        )

        choice = response.choices[0]
        assistant_msg = choice.message

        # Add assistant response to history
        msg_dict: dict = {"role": "assistant", "content": assistant_msg.content or ""}
        if assistant_msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_msg.tool_calls
            ]
        messages.append(msg_dict)

        # If no tool calls, we have a final response
        if not assistant_msg.tool_calls:
            return assistant_msg.content or ""

        # Execute each tool call
        for tc in assistant_msg.tool_calls:
            tool_name = tc.function.name
            try:
                tool_args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            console.print(
                f"  [dim]⚙ Calling tool:[/dim] [bold cyan]{tool_name}[/bold cyan]"
                f"[dim]({json.dumps(tool_args, ensure_ascii=False)[:120]})[/dim]"
            )

            result = execute_tool(tool_name, tool_args)

            console.print(f"  [dim]✓ Result:[/dim] [green]{result[:200]}[/green]")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

    return "⚠ Reached maximum tool-use turns. Here's what I have so far."


def _to_sdk_messages(messages: list[dict]) -> list[ChatRequestMessage]:
    """Convert our dict-based message history to Azure SDK message objects."""
    sdk_msgs: list[ChatRequestMessage] = []
    for m in messages:
        role = m["role"]
        if role == "system":
            sdk_msgs.append(SystemMessage(content=m["content"]))
        elif role == "user":
            sdk_msgs.append(UserMessage(content=m["content"]))
        elif role == "assistant":
            msg = AssistantMessage(content=m.get("content", ""))
            if "tool_calls" in m:
                from azure.ai.inference.models import (
                    ChatCompletionsToolCall,
                    FunctionCall,
                )

                msg.tool_calls = [
                    ChatCompletionsToolCall(
                        id=tc["id"],
                        function=FunctionCall(
                            name=tc["function"]["name"],
                            arguments=tc["function"]["arguments"],
                        ),
                    )
                    for tc in m["tool_calls"]
                ]
            sdk_msgs.append(msg)
        elif role == "tool":
            sdk_msgs.append(
                ToolMessage(
                    tool_call_id=m["tool_call_id"],
                    content=m["content"],
                )
            )
    return sdk_msgs


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------


def main():
    if not ENDPOINT or not API_KEY:
        console.print(
            "[red bold]Error:[/red bold] Set AZURE_AI_ENDPOINT and AZURE_AI_API_KEY "
            "in your .env file. See .env.example for details."
        )
        sys.exit(1)

    console.print(
        Panel(
            "[bold]Agent powered by Claude Opus 4.5 on Azure AI[/bold]\n"
            "Tools: calculator, shell_command, read_file, write_file, "
            "web_search, get_current_datetime\n\n"
            "Type [bold green]quit[/bold green] or [bold green]exit[/bold green] to stop.",
            title="🤖 Azure AI Agent",
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
