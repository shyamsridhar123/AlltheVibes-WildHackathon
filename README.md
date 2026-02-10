# AlltheVibes-WildHackathon

AI Agent running **locally** via **Ollama** — no API keys, no cloud, fully private.

## What it does

A general-purpose chat agent with an agentic tool-use loop. It can:

- **Run shell commands** — list files, search, inspect system state
- **Read & write files** — view or create files on disk
- **Do math** — evaluate mathematical expressions
- **Search the web** — query DuckDuckGo for information
- **Get current time** — UTC datetime

The agent autonomously decides when to use tools, chains multiple tool calls, and returns a final answer.

## Setup

### 1. Install Ollama

```bash
# Linux / WSL
curl -fsSL https://ollama.com/install.sh | sh

# macOS — or download from https://ollama.com
brew install ollama
```

### 2. Pull a model

```bash
# Recommended: good quality + tool-calling support
ollama pull qwen2.5:7b

# Other options:
# ollama pull llama3.1:8b
# ollama pull mistral:7b
# ollama pull qwen2.5:14b   (needs ~10GB RAM)
```

### 3. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure (optional)

```bash
cp .env.example .env
# Edit .env to change model or Ollama URL
```

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name | `qwen2.5:7b` |

### 5. Run the agent

```bash
# Make sure Ollama is running (it auto-starts on macOS, or: ollama serve)
python agent.py
```

## Architecture

```text
agent.py    — Main agent loop + CLI interface
tools.py    — Tool registry, definitions, and implementations
.env        — Local config (not committed)
```

### How the agentic loop works

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
