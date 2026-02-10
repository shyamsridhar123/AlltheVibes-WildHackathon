"""
Tool definitions and implementations for the agent.
Each tool is a function decorated with @tool, which registers it in the TOOL_REGISTRY.
"""

from __future__ import annotations

import json
import math
import subprocess
import datetime
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOL_REGISTRY: dict[str, dict[str, Any]] = {}


def tool(
    name: str,
    description: str,
    parameters: dict[str, Any],
):
    """Decorator that registers a callable as an agent tool."""

    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        TOOL_REGISTRY[name] = {
            "function": func,
            "definition": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            },
        }
        return func

    return decorator


def get_tool_definitions() -> list[dict]:
    """Return the list of tool JSON schemas for the model."""
    return [entry["definition"] for entry in TOOL_REGISTRY.values()]


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute a registered tool by name and return its string result."""
    entry = TOOL_REGISTRY.get(name)
    if entry is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = entry["function"](**arguments)
        return result if isinstance(result, str) else json.dumps(result)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Built-in tools
# ---------------------------------------------------------------------------


@tool(
    name="calculator",
    description="Evaluate a mathematical expression. Supports basic arithmetic, powers, sqrt, trig, etc.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The math expression to evaluate, e.g. '2 + 3 * 4' or 'sqrt(144)'.",
            }
        },
        "required": ["expression"],
    },
)
def calculator(expression: str) -> str:
    # Provide a safe math environment
    allowed_names: dict[str, Any] = {
        k: getattr(math, k) for k in dir(math) if not k.startswith("_")
    }
    allowed_names["abs"] = abs
    allowed_names["round"] = round
    allowed_names["min"] = min
    allowed_names["max"] = max

    # Block dangerous builtins
    result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
    return json.dumps({"expression": expression, "result": result})


@tool(
    name="get_current_datetime",
    description="Get the current date and time.",
    parameters={
        "type": "object",
        "properties": {},
    },
)
def get_current_datetime() -> str:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    return json.dumps(
        {
            "utc": now.isoformat(),
            "unix_timestamp": now.timestamp(),
        }
    )


@tool(
    name="shell_command",
    description="Run a shell command and return stdout/stderr. Use for file listing, searching, or other system tasks. Be careful with destructive commands.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute.",
            },
            "timeout": {
                "type": "integer",
                "description": "Max seconds to wait (default 30).",
            },
        },
        "required": ["command"],
    },
)
def shell_command(command: str, timeout: int = 30) -> str:
    # Block obviously dangerous patterns
    blocked = ["rm -rf /", "mkfs", "dd if=", ":(){", "fork bomb"]
    for b in blocked:
        if b in command:
            return json.dumps({"error": f"Blocked dangerous command pattern: {b}"})
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return json.dumps(
            {
                "stdout": proc.stdout[:4000],
                "stderr": proc.stderr[:2000],
                "returncode": proc.returncode,
            }
        )
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"Command timed out after {timeout}s"})


@tool(
    name="read_file",
    description="Read the contents of a file and return it.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read.",
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to return (default 200).",
            },
        },
        "required": ["path"],
    },
)
def read_file(path: str, max_lines: int = 200) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    total = len(lines)
    truncated = lines[:max_lines]
    content = "".join(truncated)
    return json.dumps(
        {
            "path": path,
            "total_lines": total,
            "returned_lines": len(truncated),
            "content": content,
        }
    )


@tool(
    name="write_file",
    description="Write content to a file. Creates the file if it doesn't exist, overwrites if it does.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to write.",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file.",
            },
        },
        "required": ["path", "content"],
    },
)
def write_file(path: str, content: str) -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return json.dumps({"status": "ok", "path": path, "bytes_written": len(content)})


@tool(
    name="web_search",
    description="Search the web using DuckDuckGo Lite (no API key needed). Returns text snippets.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string.",
            },
        },
        "required": ["query"],
    },
)
def web_search(query: str) -> str:
    import httpx
    from html.parser import HTMLParser

    class DDGParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.results: list[str] = []
            self._in_result = False
            self._current = ""

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            if tag == "a" and "result-link" in attrs_dict.get("class", ""):
                self._in_result = True
                self._current = attrs_dict.get("href", "")

        def handle_data(self, data):
            if self._in_result:
                self._current += f" | {data.strip()}"

        def handle_endtag(self, tag):
            if tag == "a" and self._in_result:
                self.results.append(self._current)
                self._in_result = False
                self._current = ""

    try:
        resp = httpx.get(
            "https://lite.duckduckgo.com/lite/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
            follow_redirects=True,
        )
        parser = DDGParser()
        parser.feed(resp.text)

        if parser.results:
            return json.dumps({"query": query, "results": parser.results[:5]})
        # Fallback: return raw text snippets
        text = resp.text[:3000]
        return json.dumps({"query": query, "raw_preview": text})
    except Exception as exc:
        return json.dumps({"error": f"Search failed: {exc}"})
