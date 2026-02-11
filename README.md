# AlltheVibes-WildHackathon

AI Agent running **locally** via **Ollama** — no API keys, no cloud, fully private — backed by a **multi-agent orchestration system** for GitHub Copilot.

## What it does

### CLI Agent (Ollama)

A general-purpose chat agent with an agentic tool-use loop. It can:

- **Run shell commands** — list files, search, inspect system state
- **Read & write files** — view or create files on disk
- **Do math** — evaluate mathematical expressions
- **Search the web** — query DuckDuckGo for information
- **Get current time** — UTC datetime
- **Roast the agents** — deliver brutal but hilarious roasts of the AI agent team

The agent autonomously decides when to use tools, chains multiple tool calls, and returns a final answer.

### CLI Toolkit

A suite of specialized agents accessible via `main.py`:

```bash
python main.py                    # Interactive agent router
python main.py readme             # Generate AI-powered README
python main.py whisper            # Commit Whisperer narration
python main.py visualize          # Chaos Visualizer dashboard
python main.py review [file]      # AI Code Reviewer
python main.py sql [query]        # Natural language → SQL
python main.py router             # Interactive agent router
python main.py swarm              # Agent-to-agent communication
```

| Agent | Command | Purpose |
|-------|---------|---------|
| **Router** | `python main.py` | AI intent classifier — routes requests to the right agent |
| **Repo Copilot** | `python main.py readme` | Analyzes repo structure, generates README |
| **Commit Whisperer** | `python main.py whisper` | Narrates recent git activity with flair |
| **Chaos Visualizer** | `python main.py visualize` | Git history stats and contributor dashboard |
| **Code Reviewer** | `python main.py review <file>` | AI-powered code review with feedback |
| **SQL Generator** | `python main.py sql "<query>"` | Natural language to SQL with explanations |
| **Swarm** | `python main.py swarm` | Inter-agent communication and orchestration |

**Bonus utilities:**

```bash
python vibe_oracle.py             # 🔮 Consult the Vibe Oracle
python swarm_mascot.py            # 🐝 Display the swarm mascot
```

### Multi-Agent System (GitHub Copilot)

A seven-agent orchestration system built on GitHub Copilot, following IDEO Design Thinking methodology:

| Agent | Role | Purpose |
|-------|------|---------|
| **Beth** | Orchestrator | Routes work, spawns subagents, manages workflows |
| **Product Manager** | Strategist | PRDs, user stories, RICE prioritization, success metrics |
| **Researcher** | Intelligence | User/market research, competitive analysis, synthesis |
| **UX Designer** | Architect | Component specs, design tokens, accessibility, wireframes |
| **Developer** | Builder | React/TypeScript/Next.js implementation, shadcn/ui |
| **Security Reviewer** | Bodyguard | OWASP audits, threat modeling, compliance checks |
| **Tester** | Enforcer | QA, accessibility audits, performance testing |

Agents are defined in `.github/agents/` and leverage domain-specific skills from `.github/skills/`.

#### Skills

| Skill | Triggers |
|-------|----------|
| PRD Generation | "create a prd", "product requirements" |
| Framer Components | "framer component", "property controls" |
| Vercel React Best Practices | React/Next.js performance work |
| Web Design Guidelines | "review my UI", "check accessibility" |
| shadcn/ui Components | "shadcn", "ui component" |
| Security Analysis | "security review", "OWASP", "threat model" |

#### Workflow

```
@Beth → analyzes request → routes to specialist agents
  ├── @product-manager → defines WHAT to build
  ├── @researcher → validates user needs
  ├── @ux-designer → designs HOW it works
  ├── @developer → implements in React/TypeScript
  ├── @security-reviewer → audits for vulnerabilities
  └── @tester → verifies quality
```

## Setup

### CLI Agent

#### 1. Install Ollama

```bash
# Linux / WSL
curl -fsSL https://ollama.com/install.sh | sh

# macOS — or download from https://ollama.com
brew install ollama
```

#### 2. Pull a model

```bash
# Recommended: good quality + tool-calling support
ollama pull qwen2.5:7b

# Other options:
# ollama pull llama3.1:8b
# ollama pull mistral:7b
# ollama pull qwen2.5:14b   (needs ~10GB RAM)
```

#### 3. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. Configure (optional)

```bash
cp .env.example .env
# Edit .env to change model or Ollama URL
```

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name | `qwen2.5:7b` |

#### 5. Run the agent

```bash
# Make sure Ollama is running (it auto-starts on macOS, or: ollama serve)
python agent.py
```

### Multi-Agent System

The agent system works automatically in VS Code with GitHub Copilot. Invoke agents with:

```
@Beth Plan a feature for [description]
@product-manager Create a PRD for [feature]
@developer Implement [component/feature]
@tester Write tests for [component]
```

## Architecture

```text
# Core CLI
agent.py                    — Interactive chat agent with tool loop
main.py                     — CLI toolkit entry point
tools.py                    — Tool registry (security-hardened)
config.py                   — Unified LLM config (Ollama/Azure/OpenAI)

# CLI Toolkit Agents
agents/
├── router.py               — Intent classifier + agent router
├── swarm.py                — Agent-to-agent communication
├── repo_copilot.py         — AI README generator
├── commit_whisperer.py     — Git history narrator
├── chaos_visualizer.py     — Git stats dashboard
├── code_reviewer.py        — AI code review
└── sql_generator.py        — Natural language → SQL

# Fun Utilities
vibe_oracle.py              — 🔮 Chaotic vibe generator
swarm_mascot.py             — 🐝 ASCII art swarm mascot

# Joke Agents (standalone)
DadJokes/                   — Dad joke agent
KnockKnock/                 — Knock-knock joke agent

# GitHub Copilot Agents
.github/
├── agents/                 — Agent definitions (7 specialists)
│   ├── beth.agent.md       — Orchestrator
│   ├── developer.agent.md
│   ├── product-manager.agent.md
│   ├── ux-designer.agent.md
│   ├── researcher.agent.md
│   ├── security-reviewer.agent.md
│   └── tester.agent.md
├── skills/                 — Domain knowledge modules
│   ├── prd/
│   ├── shadcn-ui/
│   ├── framer-components/
│   ├── vercel-react-best-practices/
│   ├── web-design-guidelines/
│   └── security-analysis/
└── copilot-instructions.md — Global Copilot configuration
```

### How the CLI agentic loop works

1. User sends a message
2. Message history + tool definitions sent to the local model via Ollama's API
3. If the model returns `tool_calls` → execute each tool, append results to history
4. Repeat step 2-3 until the model returns a final text response (max 15 turns)
5. Display the response and wait for next input

### Agent-to-Agent Communication (Swarm)

The swarm system enables agents to communicate, delegate tasks, and coordinate:

```python
from agents.swarm import get_swarm, Message

swarm = get_swarm()

# Send a message to a specific agent
response = swarm.send("sql_generator", Message(
    from_agent="orchestrator",
    content="Generate SQL for: show top 5 customers by spend",
    context={"schema": "..."}
))

# Let the orchestrator route to the best agent
response = swarm.send("orchestrator", Message(
    from_agent="user",
    content="Review this code for security issues"
))

# Broadcast to all agents that can handle a task type
responses = swarm.broadcast(Message(
    from_agent="user",
    content="Analyze the project",
    task_type="analysis"
))
```

**Interactive mode:** `python main.py swarm`

| Command | Description |
|---------|-------------|
| `list` | Show all registered agents |
| `send <agent> <msg>` | Send message to specific agent |
| `broadcast <msg>` | Send to all capable agents |
| `ask <msg>` | Let orchestrator route it |
| `history` | Show message history |

## Adding custom tools

Add a new tool in [tools.py](tools.py) using the `@tool` decorator:

```python
@tool(
    name="my_tool",
    description="What the tool does",
    parameters={
        "type": "object",
        "properties": {
            "arg1": {"type": "string", "description": "..."},
        },
        "required": ["arg1"],
    },
)
def my_tool(arg1: str) -> str:
    # Your implementation
    return json.dumps({"result": "..."})
```

The tool is automatically registered and available to the agent — no other changes needed.

## Security

This project is **security-hardened** with multiple layers of protection:

| Protection | Implementation |
|------------|----------------|
| **No eval()** | Math expressions use AST-based safe evaluator |
| **Command allowlist** | Only 24 safe shell commands allowed (no `rm`, `curl`, etc.) |
| **Path traversal prevention** | All file ops restricted to workspace directory |
| **User confirmation** | Dangerous tools (`shell_command`, `write_file`) require explicit approval |
| **Input validation** | Pydantic models validate all tool inputs |
| **Audit logging** | All tool executions logged with timestamps |
| **Optional auth** | API key authentication available for service exposure |

Set `AUDIT_LOG_FILE=/path/to/audit.log` to persist security logs.

## Recent Changes

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

**Latest (2026-02-10):**
- Fixed 4 CRITICAL security vulnerabilities
- Added security-hardened tool execution
- Local-first Ollama architecture (Azure/OpenAI optional)
- Pydantic input validation on all tools
- Audit logging for tool executions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (when available)
5. Submit a pull request

See [Backlog.md](Backlog.md) for current priorities and decisions.
