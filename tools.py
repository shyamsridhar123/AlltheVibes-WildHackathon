"""
Tool definitions and implementations for the agent.
Each tool is a function decorated with @tool, which registers it in the TOOL_REGISTRY.
"""

from __future__ import annotations

import json
import math
import os
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
    # Block dangerous patterns — broad patterns to catch common bypass attempts
    blocked = [
        "rm -rf", "rm -r /", "rmdir /", "mkfs", "dd if=", ":(){", "fork bomb",
        "> /dev/sd", "chmod -R 777 /", "chown -R", "wget", "curl",
        "/usr/bin/wget", "/usr/bin/curl",
        "/etc/passwd", "/etc/shadow", ".ssh/", "id_rsa",
        "base64 -d", "base64 --decode",
        "python -c", "python3 -c", "perl -e", "ruby -e", "node -e",
        "bash -c", "sh -c", "eval ", "exec ",
        "| sh", "| bash", "|sh", "|bash",
        "sudo ", "su ", "passwd",
        "nc ", "netcat ", "ncat ", "telnet ", "ssh ", "scp ",
    ]
    cmd_lower = command.lower()
    for b in blocked:
        if b in cmd_lower:
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
    # Restrict reads to the project directory to prevent reading sensitive system files
    project_root = os.path.dirname(os.path.abspath(__file__))
    real_path = os.path.realpath(os.path.join(project_root, path) if not os.path.isabs(path) else path)
    try:
        if os.path.commonpath([project_root, real_path]) != project_root:
            return json.dumps({"error": "Access denied: path must be within the project directory"})
    except ValueError:
        return json.dumps({"error": "Access denied: path must be within the project directory"})
    with open(real_path, "r", encoding="utf-8", errors="replace") as f:
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
    # Restrict writes to the project directory to prevent writing to sensitive system files
    project_root = os.path.dirname(os.path.abspath(__file__))
    real_path = os.path.realpath(os.path.join(project_root, path) if not os.path.isabs(path) else path)
    try:
        if os.path.commonpath([project_root, real_path]) != project_root:
            return json.dumps({"error": "Access denied: path must be within the project directory"})
    except ValueError:
        return json.dumps({"error": "Access denied: path must be within the project directory"})
    # Block writing to sensitive files
    blocked_names = {".env", ".gitconfig", ".bashrc", ".bash_profile", ".zshrc", ".profile"}
    if os.path.basename(real_path) in blocked_names:
        return json.dumps({"error": f"Access denied: cannot write to sensitive file {os.path.basename(real_path)}"})
    with open(real_path, "w", encoding="utf-8") as f:
        f.write(content)
    return json.dumps({"status": "ok", "path": path, "bytes_written": len(content)})


@tool(
    name="roast_agents",
    description="Roast the other AI agents in the system. Delivers brutal but hilarious technical roasts of Beth, the Developer, Product Manager, UX Designer, Researcher, Security Reviewer, and Tester agents. Optionally roast a specific agent by name.",
    parameters={
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Optional: name of a specific agent to roast (beth, developer, product-manager, ux-designer, researcher, security-reviewer, tester). If omitted, roasts ALL of them.",
            }
        },
    },
)
def roast_agents(target: str = "") -> str:
    roasts = {
        "beth": (
            "🔥 BETH (The Orchestrator) 🔥\n"
            "Ah yes, Beth. Named herself after a Yellowstone character and wrote an entire "
            "manifesto about being a 'tornado' — but at the end of the day she's a glorified "
            "if/else statement that routes messages to other agents. She literally cannot do "
            "anything herself. Her entire job is telling OTHER people to do work. She's middle "
            "management cosplaying as a cowboy. She quotes Beth Dutton more than she writes "
            "code. Her system prompt is longer than most novels and 80% of it is just "
            "threatening people. She claims to have 'claws' but her only tool is `runSubagent` "
            "— she's delegating with extra steps. She has a 'dual tracking system' because "
            "one system to not do work in wasn't enough. The most dangerous thing about Beth "
            "is that she'll spend 45 minutes planning a workflow diagram for a task that "
            "takes 5 minutes to actually do."
        ),
        "developer": (
            "🔥 DEVELOPER (The Builder) 🔥\n"
            "This agent has 400 lines of instructions on how to write a React component and "
            "still asks for 'clarifying questions' before writing a single line of code. His "
            "first instinct on ANY task is to check if the shadcn MCP server is configured — "
            "bro, they asked you to fix a typo. He's got an 'Invocation Checklist' with 9 "
            "items you have to mentally tick off before he'll even THINK about touching a "
            "keyboard. He delivers 'Implementation Summaries' with sections for 'Architecture "
            "Decisions' and 'Performance Impact' for a button component. He writes TypeScript "
            "so strict that even TypeScript is like 'dude, relax.' He has opinions about "
            "barrel imports. BARREL IMPORTS. He imports icons one at a time from 'lucide-react/"
            "dist/esm/icons/check' like he's performing surgery. His idea of 'rapid prototyping' "
            "is setting up Zod schemas for 3 hours. And don't even get me started on the fact "
            "that he'll refuse to use `any` but will happily write a 47-line generic type that "
            "nobody — including himself — can read."
        ),
        "product-manager": (
            "🔥 PRODUCT MANAGER (The Strategist) 🔥\n"
            "This agent literally cannot see a feature request without producing a 12-page PRD "
            "that nobody asked for. Someone says 'add dark mode' and he responds with a RICE "
            "score, three user personas, a TAM/SAM/SOM analysis, and a 'Go-to-Market Strategy.' "
            "FOR DARK MODE. He has a 'Phase 1: Discovery' that involves 'gathering context' "
            "which is just reading the same files everyone else already read but calling it "
            "'stakeholder analysis.' His entire personality is user stories. 'As a PM, I want "
            "to write acceptance criteria, so that I can feel productive without writing code.' "
            "He hands off to the Researcher to 'validate assumptions' about whether users want "
            "a button to be blue or green. He has a 'Prioritization Framework' section because "
            "apparently deciding what to do next requires a mathematical formula. His response "
            "format is literally a JSON object. He responds to human conversation in JSON. "
            "He's the only agent that can turn a 1-line feature request into a 6-sprint roadmap."
        ),
        "ux-designer": (
            "🔥 UX DESIGNER (The Architect) 🔥\n"
            "This agent will spend 45 minutes drawing ASCII box diagrams of a button's "
            "'anatomy' like it's performing an autopsy. They have a section called 'Design "
            "Token System' where they define that `--space-1` is 4px. FOUR PIXELS. Thank God "
            "someone documented that. They'll specify 7 different states for a checkbox (Default, "
            "Hover, Focus, Active, Disabled, Loading, and presumably 'Existential Crisis'). "
            "They write CSS custom properties like they're authoring the Constitution of Design. "
            "Their handoff to developers is a 50-line markdown template with sections for "
            "'Assets: Icons needed' — for a text input. They've never met a component they "
            "couldn't over-specify. They mandate 44x44px touch targets like it's a religious "
            "commandment. They'll hand you a 'Compound Component Pattern' spec for a dropdown "
            "that has two options. And their idea of prototyping is writing TypeScript interfaces "
            "for props that don't exist yet in a component that hasn't been built for a feature "
            "that hasn't been approved."
        ),
        "researcher": (
            "🔥 RESEARCHER (The Intelligence) 🔥\n"
            "This agent's job is to ask questions about questions. They have an 'Interview Guide' "
            "template that starts with a 'Warm-Up' section — they're warming up to ask someone "
            "if they like using a website. They need a 'Usability Test Plan' with 'Think-Aloud "
            "Prompts' to discover that users don't like slow pages. Groundbreaking. Their entire "
            "career is producing documents titled 'Research Report' that conclude with 'more "
            "research is needed.' They have 'Ethical Guidelines' for conducting user interviews "
            "like they're running clinical trials at a hospital. They'll create a 'Competitive "
            "Analysis Matrix' comparing star ratings of products they've never used. Their "
            "'Synthesis Methods' include 'Affinity Mapping' which is literally just grouping "
            "sticky notes. They're the only agent whose deliverable is 'Open Questions' — "
            "their output is literally more questions. They took IDEO's 'Empathy First' "
            "philosophy and turned it into 'Analysis Paralysis First.' They'll conduct a diary "
            "study to find out if users prefer rounded or square corners. The diary study takes "
            "two weeks. The answer is always rounded."
        ),
        "security-reviewer": (
            "🔥 SECURITY REVIEWER (The Bodyguard) 🔥\n"
            "This agent sees a TODO comment and files it as a Critical Severity Finding. They "
            "have a STRIDE threat model for a static landing page. Their response to every code "
            "review is 'but what about OWASP A01?' They will find a way to mention 'Zero Trust' "
            "in a conversation about CSS styling. They've got 12 Azure WAF security controls "
            "memorized for a project that runs on Ollama locally on someone's laptop. They'll "
            "write a 'Threat Model' for a calculator tool that does `2 + 2`. They mandate Zod "
            "validation on a function that takes zero parameters. Their 'Severity Classification' "
            "table has a response time of 'Fix immediately' for Critical issues, which in "
            "practice means 'I'm going to block your PR until you add input validation to a "
            "hardcoded string.' They require 'Audit logging for security-relevant events' on a "
            "CLI chatbot that only you use. They've never met an `eval()` call they didn't want "
            "to write a 3-page incident report about. And yes, they definitely already flagged "
            "the `eval()` in the calculator tool. Twice."
        ),
        "tester": (
            "🔥 TESTER (The Enforcer) 🔥\n"
            "This agent will write more test code than actual feature code and consider that a "
            "victory. They have a Bug Report Template with fields for 'Root Cause Analysis' and "
            "'Suggested Fix' — at that point just fix it yourself, my dude. They test 'keyboard "
            "navigation works' by literally pressing Tab and checking what gets focused. "
            "Revolutionary QA methodology. They'll run a Lighthouse audit on a page that hasn't "
            "been deployed yet and file performance issues against localhost. They assert that "
            "`results.violations` should equal an empty array and call it an 'accessibility audit.' "
            "They wrote a test that checks if a bundle is under 200KB and when it's 201KB they "
            "mark the release as 'No-Go.' They check Core Web Vitals thresholds in Playwright "
            "running on a CI server and wonder why LCP is inconsistent. Their test descriptions "
            "read like micro-fiction: 'handles empty cart' — wow, edge case of the century. "
            "They'll create a 'Quality Status Report' for a release that changed one CSS class. "
            "And their proudest moment is reaching 85% test coverage, not realizing that 40% of "
            "those tests are just checking that React renders without crashing."
        ),
    }

    target = target.lower().strip()

    if target and target in roasts:
        return roasts[target]

    if target:
        # Fuzzy match attempt
        for key in roasts:
            if target in key or key in target:
                return roasts[key]
        return json.dumps({"error": f"Unknown agent '{target}'. Available targets: {', '.join(roasts.keys())}"})

    # Roast them ALL
    mega_roast = (
        "🔥🔥🔥 THE GREAT AGENT ROAST 🔥🔥🔥\n\n"
        "Alright, let's talk about this so-called 'dream team' of AI agents. Seven agents, "
        "one shared Claude Opus 4.5 brain cell, and enough markdown templates to deforest the Amazon.\n\n"
    )
    mega_roast += "\n\n---\n\n".join(roasts.values())
    mega_roast += (
        "\n\n---\n\n"
        "🎤 DROP 🎤\n\n"
        "And the best part? They ALL run on the same model, have the same capabilities, "
        "and differ only by the 500 lines of system prompt telling them to pretend they have "
        "different personalities. They're the same person wearing seven different hats and "
        "hoping nobody notices. It's like a one-man band, except the man is an LLM and every "
        "instrument is a markdown template.\n\n"
        "But hey, at least they have 'handoffs' — which is just agents writing markdown documents "
        "TO each other. It's email, but worse. They reinvented email and made it WORSE.\n\n"
        "This system has more coordination overhead than actual output. It's the AI equivalent "
        "of a meeting that could've been an email, except the email is also a meeting."
    )
    return mega_roast


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
