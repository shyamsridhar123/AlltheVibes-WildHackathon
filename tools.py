"""
Tool definitions and implementations for the agent.
Each tool is a function decorated with @tool, which registers it in the TOOL_REGISTRY.
"""

from __future__ import annotations

import ast
import json
import math
import operator
import shlex
import subprocess
import datetime
from pathlib import Path
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Security Configuration
# ---------------------------------------------------------------------------

# Workspace root for file operations (prevents path traversal)
WORKSPACE_ROOT = Path(__file__).parent.resolve()

# Allowed file extensions for read/write operations
ALLOWED_EXTENSIONS = frozenset({
    '.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini',
    '.js', '.ts', '.jsx', '.tsx', '.css', '.html', '.sh', '.bash', '.zsh',
    '.env.example', '.gitignore', '.dockerignore', 'Dockerfile', 'Makefile',
})

# Allowlisted shell commands (instead of blocklist approach)
ALLOWED_COMMANDS = frozenset({
    'ls', 'cat', 'head', 'tail', 'grep', 'find', 'wc', 'echo', 'pwd', 'date',
    'git', 'python', 'python3', 'pip', 'which', 'whoami', 'hostname', 'uname',
    'tree', 'file', 'stat', 'du', 'df', 'env', 'printenv', 'sort', 'uniq',
    'diff', 'less', 'more', 'awk', 'sed', 'cut', 'tr', 'tee', 'xargs',
})

# Tools that require user confirmation before execution
DANGEROUS_TOOLS = frozenset({'shell_command', 'write_file'})

# Maximum file size for write operations (1MB)
MAX_WRITE_SIZE = 1_000_000

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
        # Sanitize error message to avoid leaking sensitive info
        error_msg = str(exc)
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        return json.dumps({"error": error_msg})


def is_dangerous_tool(name: str) -> bool:
    """Check if a tool requires user confirmation before execution."""
    return name in DANGEROUS_TOOLS


# ---------------------------------------------------------------------------
# Path Validation Helpers
# ---------------------------------------------------------------------------


def validate_path(path: str, must_exist: bool = True) -> Path:
    """
    Validate and resolve a path within the workspace.
    Raises ValueError if path is invalid or outside workspace.
    """
    if not path or not isinstance(path, str):
        raise ValueError("Path must be a non-empty string")
    
    # Reject obviously dangerous patterns early
    if '\x00' in path:
        raise ValueError("Null bytes not allowed in path")
    
    try:
        # Resolve the path relative to workspace
        if Path(path).is_absolute():
            resolved = Path(path).resolve()
        else:
            resolved = (WORKSPACE_ROOT / path).resolve()
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid path: {e}")
    
    # Ensure path is within workspace (prevent traversal)
    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError:
        raise ValueError("Path traversal detected: access denied. Path must be within workspace.")
    
    if must_exist and not resolved.exists():
        raise ValueError(f"File not found: {path}")
    
    return resolved


def validate_file_extension(path: Path, for_write: bool = False) -> None:
    """
    Validate that file extension is allowed.
    More restrictive for write operations.
    """
    # Get extension (handle files like Dockerfile, Makefile with no extension)
    suffix = path.suffix.lower() if path.suffix else path.name
    
    if suffix not in ALLOWED_EXTENSIONS and path.name not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"File type '{suffix or path.name}' not allowed. "
            f"Allowed extensions: {sorted(ALLOWED_EXTENSIONS)}"
        )


# ---------------------------------------------------------------------------
# Safe Expression Evaluator (replaces dangerous eval())
# ---------------------------------------------------------------------------


class SafeExpressionEvaluator:
    """
    Safely evaluate mathematical expressions using AST parsing.
    Only allows numeric literals, basic operators, and whitelisted math functions.
    """
    
    SAFE_BINARY_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    
    SAFE_UNARY_OPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }
    
    SAFE_COMPARE_OPS = {
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
    }
    
    SAFE_FUNCTIONS = {
        # Basic math
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,
        # Math module functions
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'floor': math.floor,
        'ceil': math.ceil,
        'trunc': math.trunc,
        'factorial': math.factorial,
        'gcd': math.gcd,
        'radians': math.radians,
        'degrees': math.degrees,
        'hypot': math.hypot,
    }
    
    SAFE_CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
    }
    
    def __init__(self, max_length: int = 500):
        self.max_length = max_length
    
    def evaluate(self, expression: str) -> float | int:
        """Safely evaluate a mathematical expression."""
        if not expression or not isinstance(expression, str):
            raise ValueError("Expression must be a non-empty string")
        
        if len(expression) > self.max_length:
            raise ValueError(f"Expression too long. Max: {self.max_length} characters")
        
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax: {e}")
        
        return self._eval_node(tree.body)
    
    def _eval_node(self, node: ast.expr) -> float | int:
        """Recursively evaluate an AST node."""
        # Numeric literals
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Only numeric constants allowed, got {type(node.value).__name__}")
        
        # Named constants (pi, e, etc.)
        if isinstance(node, ast.Name):
            name = node.id.lower()
            if name in self.SAFE_CONSTANTS:
                return self.SAFE_CONSTANTS[name]
            raise ValueError(f"Unknown constant: {node.id}. Allowed: {list(self.SAFE_CONSTANTS.keys())}")
        
        # Binary operations (+, -, *, /, etc.)
        if isinstance(node, ast.BinOp):
            op_func = self.SAFE_BINARY_OPS.get(type(node.op))
            if not op_func:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            # Safety check for power operations
            if isinstance(node.op, ast.Pow):
                if abs(right) > 1000:
                    raise ValueError("Exponent too large (max 1000)")
            return op_func(left, right)
        
        # Unary operations (+x, -x)
        if isinstance(node, ast.UnaryOp):
            op_func = self.SAFE_UNARY_OPS.get(type(node.op))
            if not op_func:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op_func(self._eval_node(node.operand))
        
        # Function calls (sqrt, sin, etc.)
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls allowed")
            
            func_name = node.func.id.lower()
            if func_name not in self.SAFE_FUNCTIONS:
                raise ValueError(
                    f"Unknown function: {node.func.id}. "
                    f"Allowed: {list(self.SAFE_FUNCTIONS.keys())}"
                )
            
            # Evaluate arguments
            args = [self._eval_node(arg) for arg in node.args]
            
            # Check for keyword arguments (not supported)
            if node.keywords:
                raise ValueError("Keyword arguments not supported in math expressions")
            
            return self.SAFE_FUNCTIONS[func_name](*args)
        
        # Comparisons (for expressions like 2 < 3)
        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                op_func = self.SAFE_COMPARE_OPS.get(type(op))
                if not op_func:
                    raise ValueError(f"Unsupported comparison: {type(op).__name__}")
                right = self._eval_node(comparator)
                if not op_func(left, right):
                    return False
                left = right
            return True
        
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")


# Global safe evaluator instance
_safe_evaluator = SafeExpressionEvaluator()


# ---------------------------------------------------------------------------
# Built-in tools
# ---------------------------------------------------------------------------


@tool(
    name="calculator",
    description="Evaluate a mathematical expression. Supports basic arithmetic, powers, sqrt, trig, etc. Examples: '2 + 3 * 4', 'sqrt(144)', 'sin(pi/2)', 'log(100, 10)'.",
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
    """
    Safely evaluate mathematical expressions using AST parsing.
    No eval() - prevents code injection attacks.
    """
    try:
        result = _safe_evaluator.evaluate(expression)
        return json.dumps({"expression": expression, "result": result})
    except ValueError as e:
        return json.dumps({"error": str(e), "expression": expression})
    except (ZeroDivisionError, OverflowError, ValueError) as e:
        return json.dumps({"error": f"Math error: {e}", "expression": expression})


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
    description=f"Run an allowlisted shell command and return stdout/stderr. Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}. For security, commands are validated and run without shell expansion.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute (must start with an allowed command).",
            },
            "timeout": {
                "type": "integer",
                "description": "Max seconds to wait (default 30, max 60).",
            },
        },
        "required": ["command"],
    },
)
def shell_command(command: str, timeout: int = 30) -> str:
    """
    Execute a restricted subset of shell commands safely.
    Uses allowlist approach instead of blocklist - much more secure.
    """
    # Validate timeout
    timeout = max(1, min(60, timeout))  # Enforce 1-60 second range
    
    # Parse command into parts
    try:
        parts = shlex.split(command)
    except ValueError as e:
        return json.dumps({"error": f"Invalid command syntax: {e}"})
    
    if not parts:
        return json.dumps({"error": "Empty command"})
    
    # Get the base command name (handle /bin/ls, ./script, etc.)
    base_cmd = Path(parts[0]).name
    
    # Check if command is in allowlist
    if base_cmd not in ALLOWED_COMMANDS:
        return json.dumps({
            "error": f"Command '{base_cmd}' not in allowlist.",
            "allowed_commands": sorted(ALLOWED_COMMANDS),
            "hint": "Only safe, read-oriented commands are allowed for security."
        })
    
    # Block shell metacharacters in arguments to prevent injection
    dangerous_chars = set(';&|`$(){}[]<>!\\\n\r')
    for i, arg in enumerate(parts[1:], 1):
        if any(c in arg for c in dangerous_chars):
            return json.dumps({
                "error": f"Shell metacharacter detected in argument {i}. "
                         f"These are blocked for security: {' '.join(sorted(dangerous_chars))}"
            })
    
    try:
        proc = subprocess.run(
            parts,  # Pass as list, not string - shell=False by default
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(WORKSPACE_ROOT),  # Always run in workspace directory
        )
        return json.dumps({
            "stdout": proc.stdout[:4000],
            "stderr": proc.stderr[:2000],
            "returncode": proc.returncode,
            "command_executed": parts,
        })
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"Command timed out after {timeout}s"})
    except FileNotFoundError:
        return json.dumps({"error": f"Command not found: {base_cmd}"})
    except PermissionError:
        return json.dumps({"error": f"Permission denied for command: {base_cmd}"})


@tool(
    name="read_file",
    description="Read the contents of a file within the workspace. Path traversal outside workspace is blocked for security.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read (relative to workspace or absolute within workspace).",
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to return (default 200, max 1000).",
            },
        },
        "required": ["path"],
    },
)
def read_file(path: str, max_lines: int = 200) -> str:
    """
    Read file contents with path traversal protection.
    Only files within the workspace directory can be read.
    """
    # Validate and clamp max_lines
    max_lines = max(1, min(1000, max_lines))
    
    try:
        safe_path = validate_path(path, must_exist=True)
    except ValueError as e:
        return json.dumps({"error": str(e), "path": path})
    
    # Check if it's a file (not a directory)
    if not safe_path.is_file():
        return json.dumps({"error": f"Not a file: {path}", "path": path})
    
    try:
        with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except PermissionError:
        return json.dumps({"error": f"Permission denied: {path}", "path": path})
    except IsADirectoryError:
        return json.dumps({"error": f"Is a directory: {path}", "path": path})
    
    total = len(lines)
    truncated = lines[:max_lines]
    content = "".join(truncated)
    
    return json.dumps({
        "path": str(safe_path.relative_to(WORKSPACE_ROOT)),
        "total_lines": total,
        "returned_lines": len(truncated),
        "truncated": total > max_lines,
        "content": content,
    })


@tool(
    name="write_file",
    description="Write content to a file within the workspace. Creates the file if it doesn't exist, overwrites if it does. Path traversal outside workspace is blocked. NOTE: This is a dangerous tool - user confirmation may be required.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to write (relative to workspace or absolute within workspace).",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file (max 1MB).",
            },
        },
        "required": ["path", "content"],
    },
)
def write_file(path: str, content: str) -> str:
    """
    Write file contents with path traversal protection.
    Only files within the workspace directory can be written.
    Limited to allowed file extensions and max file size.
    """
    # Validate content size
    if len(content) > MAX_WRITE_SIZE:
        return json.dumps({
            "error": f"Content too large. Max size: {MAX_WRITE_SIZE} bytes ({MAX_WRITE_SIZE // 1024}KB)",
            "path": path,
            "content_size": len(content),
        })
    
    try:
        # For write, the file may not exist yet
        safe_path = validate_path(path, must_exist=False)
    except ValueError as e:
        return json.dumps({"error": str(e), "path": path})
    
    # Validate file extension
    try:
        validate_file_extension(safe_path, for_write=True)
    except ValueError as e:
        return json.dumps({"error": str(e), "path": path})
    
    # Create parent directories if needed
    try:
        safe_path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        return json.dumps({"error": f"Permission denied creating directory: {safe_path.parent}", "path": path})
    
    # Check if file exists (for informational purposes)
    file_existed = safe_path.exists()
    
    try:
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
    except PermissionError:
        return json.dumps({"error": f"Permission denied: {path}", "path": path})
    except IsADirectoryError:
        return json.dumps({"error": f"Is a directory: {path}", "path": path})
    
    return json.dumps({
        "status": "ok",
        "path": str(safe_path.relative_to(WORKSPACE_ROOT)),
        "bytes_written": len(content),
        "action": "overwritten" if file_existed else "created",
    })


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
