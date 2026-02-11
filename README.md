# AlltheVibes-WildHackathon

A hackathon toolkit with three layers of AI agents:

1. **Local CLI agent** (`agent.py`)  runs on [Ollama](https://ollama.com), fully offline, with tool calling
2. **Azure OpenAI agents** (`main.py` + `agents/`)  cloud-powered utilities for repo insights, code review, commit narration, and SQL generation
3. **GitHub Copilot agent definitions** (`.github/agents/`)  eight specialist agents for use inside VS Code with GitHub Copilot

Plus a collection of standalone comedy and vibe bots.

## Quick Start

### 1. Local CLI agent (Ollama  no API keys needed)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                      # python-dotenv, rich, httpx
ollama pull qwen2.5:7b                               # or llama3.1:8b, mistral:7b
python agent.py                                      # start the chat agent
```

The CLI agent has these tools built in (defined in `tools.py`):

| Tool | What it does |
|------|-------------|
| `calculator` | Evaluate math expressions (uses Python `math`) |
| `get_current_datetime` | Current UTC date/time |
| `shell_command` | Run shell commands (with safety blocklist) |
| `read_file` | Read files within the project directory |
| `write_file` | Write files within the project directory |
| `web_search` | Search DuckDuckGo Lite (no API key) |
| `roast_agents` | Deliver brutal roasts of the Copilot agent team |

Configure via `.env` (see `.env.example`):

| Variable | Default |
|----------|---------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `OLLAMA_MODEL` | `qwen2.5:7b` |

### 2. Azure OpenAI agents (requires Azure credentials)

These require `azure-identity`, `openai`, and Azure OpenAI credentials. They are **not** included in `requirements.txt`  install separately:

```bash
pip install azure-identity openai
```

Set environment variables or `.env`:

| Variable | Required | Notes |
|----------|----------|-------|
| `ENDPOINT_URL` | Yes | Your Azure OpenAI endpoint |
| `DEPLOYMENT_NAME` | No | Defaults to `gpt-4o` |
| `AZURE_OPENAI_API_KEY` | No | If unset, uses `DefaultAzureCredential` (run `az login`) |
| `AZURE_OPENAI_API_VERSION` | No | Defaults to `2024-12-01-preview` |

Run commands via `main.py`:

```bash
python main.py                     # interactive router (default)
python main.py router              # same  intent-based agent routing
python main.py readme              # generate AI-powered README from repo context
python main.py whisper             # narrate recent git commit activity
python main.py visualize           # ASCII dashboard of contributor & file stats
python main.py review path/to/file # AI code review of a specific file
python main.py sql "describe foo"  # natural language  SQL
```

Each command maps to a Python module in `agents/`:

| Module | What it does |
|--------|-------------|
| `router.py` | Classifies user intent via LLM, routes to the right agent |
| `repo_copilot.py` | Walks the repo tree and generates a README summary |
| `commit_whisperer.py` | Narrates recent git history in dramatic style |
| `chaos_visualizer.py` | Renders contributor stats and file-change frequency |
| `code_reviewer.py` | AI-powered file-level code review |
| `sql_generator.py` | Turns natural language into SQL queries |

### 3. GitHub Copilot agents (VS Code only)

The `.github/agents/` directory contains eight agent definitions for use inside VS Code with GitHub Copilot. These are **not Python code**  they are markdown files with YAML frontmatter that configure Copilot's behavior:

| Agent | File | Role |
|-------|------|------|
| Beth | `beth.agent.md` | Orchestrator  routes work to specialists |
| Product Manager | `product-manager.agent.md` | PRDs, user stories, prioritization |
| Researcher | `researcher.agent.md` | User/market research, competitive analysis |
| UX Designer | `ux-designer.agent.md` | Component specs, design tokens, accessibility |
| Developer | `developer.agent.md` | React/TypeScript/Next.js implementation |
| Security Reviewer | `security-reviewer.agent.md` | OWASP audits, threat modeling |
| Tester | `tester.agent.md` | QA, accessibility, performance testing |
| MacGyver | `macgyver.agent.md` | Improviser  solves problems with whatever is available |

Invoke them in VS Code: `@Beth`, `@developer`, `@product-manager`, etc.

Skills (domain knowledge) are in `.github/skills/`: PRD generation, Framer components, Vercel/React best practices, web design guidelines, shadcn/ui, and security analysis.

## Comedy & Vibe Bots

Standalone scripts, each with their own dependencies:

| Script | What it does | API needed? |
|--------|-------------|-------------|
| `vibe_oracle.py` | Random chaotic vibe prophecies | No |
| `swarm_mascot.py` | ASCII art bee mascot + Finding Nemo gallery | No |
| `swarm_chaos.py` | Runs vibe oracle + mascot + git chaos | No |
| `sharkbait/agent_sharkbait.py` | Ocean-themed code review with the Sharkbait Scale | No |
| `ComedyArena/comedy_arena.py` | Two joke agents judged by an LLM judge | Azure OpenAI |
| `DadJokes/dad_joke_agent.py` | Every response as a dad joke | OpenAI API |
| `KnockKnock/knock_knock_agent.py` | Every response as a knock-knock joke | OpenAI API |
| `emoji-translator/src/emoji_translator.py` | Text to emoji translation | Optional (OpenAI) |

## Project Structure

```
agent.py                 - Ollama CLI agent loop (tool-calling chat)
tools.py                 - Tool registry: calculator, shell, files, web search, roast
config.py                - Azure OpenAI client setup (DefaultAzureCredential or API key)
main.py                  - CLI router to Azure-powered agents
requirements.txt         - Python deps for the Ollama agent (dotenv, rich, httpx)

agents/                  - Azure OpenAI agent modules
  router.py              - Intent classifier and agent routing
  repo_copilot.py        - AI README generator from repo context
  commit_whisperer.py    - Git history narrator
  chaos_visualizer.py    - Contributor/file stats dashboard
  code_reviewer.py       - AI code review
  sql_generator.py       - Natural language to SQL

.github/
  agents/                - GitHub Copilot agent definitions (8 agents)
  skills/                - Domain knowledge for Copilot agents
  instructions/          - Repo-level instructions for Copilot
  prompts/               - Quick-fire prompt templates
  copilot-instructions.md - Global Copilot configuration

ComedyArena/             - LLM-as-judge joke showdown (Azure OpenAI)
DadJokes/                - Dad joke chatbot (OpenAI API)
KnockKnock/              - Knock-knock joke chatbot (OpenAI API)
emoji-translator/        - Text to emoji translator
sharkbait/               - Ocean-themed code reviewer (no API needed)
vibe_oracle.py           - Chaotic vibe generator
swarm_chaos.py           - Swarm chaos engine
swarm_mascot.py          - ASCII art mascot

prompts/                 - System prompts for Azure agents
docs/                    - Research notes and design plans
src/                     - TypeScript agent framework prototype (unfinished)

Backlog.md               - Completed work archive
AGENTS.md                - Workflow instructions (beads + Backlog)
CHANGELOG.md             - Change history
REPO_STRUCTURE.md        - Workspace configuration guide
```

## How the CLI agent loop works

1. User types a message
2. Message history + tool definitions sent to Ollama `/api/chat` endpoint
3. If the model returns `tool_calls` then execute each tool, append results to history
4. Repeat steps 2-3 until the model returns a final text response (max 15 turns)
5. Display the response with rich formatting, wait for next input

## Adding custom tools

Add a tool in `tools.py` using the `@tool` decorator:

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
    return json.dumps({"result": "..."})
```

The tool is automatically registered and available to the agent.

## Recent Changes

See [CHANGELOG.md](CHANGELOG.md) for a full history of changes.

## Contributing

- Track active work with beads (`bd`) and record completions in [Backlog.md](Backlog.md) (see [AGENTS.md](AGENTS.md) for the workflow).
- Keep this README and the project structure section up to date when adding new files or directories.
- Use relative links for all internal file references.