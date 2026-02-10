# AlltheVibes-WildHackathon

AI Agent running **locally** via **Ollama** — no API keys, no cloud, fully private — backed by a **multi-agent orchestration system** for GitHub Copilot.

```text
                          ╔══════════════════════════════════════════════════════╗
                          ║     🐝  A L L   T H E   V I B E S  🐝               ║
                          ║          A G E N T    S W A R M                      ║
                          ╚══════════════════════════════════════════════════════╝

       ┌─────────────────────────────────────────────────────────────────────────────────┐
       │                        🌐  G I T H U B   C O P I L O T                        │
       │                         M U L T I - A G E N T   S Y S T E M                   │
       │                                                                                 │
       │                              ┌─────────────┐                                    │
       │                              │  🤠  BETH   │                                    │
       │                              │ Orchestrator │                                    │
       │                              └──────┬──────┘                                    │
       │                   ┌────────┬────────┼────────┬─────────┐                        │
       │                   ▼        ▼        ▼        ▼         ▼                        │
       │             ┌──────────┐┌────────┐┌────────┐┌────────┐┌──────────┐              │
       │             │ 📋  PM   ││ 🔬 Re- ││ 🎨 UX  ││ 💻 Dev ││ 🧪 Test │              │
       │             │Strategist││searcher││Designer││Builder ││Enforcer │              │
       │             └──────────┘└────────┘└────────┘└────────┘└──────────┘              │
       │                                      │                                          │
       │                               ┌──────┴──────┐                                   │
       │                               │ 🛡️  Security │                                   │
       │                               │   Reviewer   │                                   │
       │                               └──────────────┘                                   │
       └─────────────────────────────────────────────────────────────────────────────────┘

       ┌─────────────────────────────────────────────────────────────────────────────────┐
       │                    🖥️   L O C A L   C L I   A G E N T S                        │
       │                          ( O l l a m a  P o w e r e d )                         │
       │                                                                                 │
       │    ┌──────────────┐      ┌───────────────────────────────────────────────┐       │
       │    │  🔀 ROUTER   │─────▶│  Agent Selection Based on User Intent        │       │
       │    │ Intent Class.│      └───────────────────────────────────────────────┘       │
       │    └──────┬───────┘                                                             │
       │           │  routes to:                                                         │
       │     ┌─────┼────────┬────────────┬─────────────┬──────────────┐                  │
       │     ▼     ▼        ▼            ▼             ▼              ▼                  │
       │  ┌──────┐┌──────┐┌───────────┐┌───────────┐┌────────────┐┌──────────┐          │
       │  │🤖    ││🔮    ││📊         ││🔍         ││🗄️          ││🔮        │          │
       │  │ Repo ││Commit││  Chaos    ││   Code    ││    SQL     ││  Vibe   │          │
       │  │Copil-││Whisp-││  Visual-  ││ Reviewer  ││ Generator  ││ Oracle  │          │
       │  │ ot   ││ erer ││  izer     ││           ││            ││         │          │
       │  └──────┘└──────┘└───────────┘└───────────┘└────────────┘└──────────┘          │
       │                                                                                 │
       │  ┌──────────────────────────────────────────────────────────────────────┐        │
       │  │  🛠️  TOOLS: calculator │ shell │ read/write │ web_search │ roast   │        │
       │  └──────────────────────────────────────────────────────────────────────┘        │
       └─────────────────────────────────────────────────────────────────────────────────┘

       ┌─────────────────────────────────────────────────────────────────────────────────┐
       │                 😂  C O M E D Y   A G E N T S  ( O p e n A I )                 │
       │                                                                                 │
       │         ┌──────────────────┐              ┌──────────────────┐                   │
       │         │  👨 DAD JOKES    │              │ 🚪 KNOCK KNOCK  │                   │
       │         │  "Hi Hungry,    │              │  "Who's there?"  │                   │
       │         │   I'm Dad!"    │              │  "Bug."          │                   │
       │         └──────────────────┘              │  "Bug who?"     │                   │
       │                                           │  "Bug in prod!" │                   │
       │                                           └──────────────────┘                   │
       └─────────────────────────────────────────────────────────────────────────────────┘

           \   /        \   /        \   /        \   /        \   /
       _.--'(  )'--._.--(  )'--._.--'(  )'--._.--(  )'--._.--'(  )'--._
      /  .-. \/ .-.  /.-. \/ .-.\/.-. \/ .-.\/.-. \/ .-.\/.-. \/ .-.  \
     | ( O ) () ( O )( O ) () ( O( O ) () ( O( O ) () ( O( O ) () ( O )|
      \  '-' /\ '-'  \'-' /\ '-'/\'-' /\ '-'/\'-' /\ '-'/\'-' /\ '-'  /
       '-.__(  )__.--'(  )'--.(  )__.-'(  )'--.(  )__.--'(  )'--.(  )_'
           /   \      /   \    /   \    /   \    /   \    /   \
         | PUSH! |  | VIBE! |  | CODE! | | SWARM |  | SHIP! |  | HACK! |
          '-----'    '-----'    '-----'   '-----'    '-----'    '-----'

                 🐝 THE SWARM IS ALIVE. PUSH YOUR CODE. TRUST THE VIBES. 🐝
```

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
agent.py                    — CLI agent loop + Ollama interface
tools.py                    — Tool registry and implementations
.env                        — Local config (not committed)
.github/
├── agents/                 — Agent definitions (7 specialists)
│   ├── beth.agent.md
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
