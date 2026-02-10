# AlltheVibes-WildHackathon

AI Agent powered by **Claude Opus 4.5** on **Azure AI Foundry**, built from scratch with the Azure AI Inference SDK.

## What it does

A general-purpose chat agent with an agentic tool-use loop. It can:

- **Run shell commands** — list files, search, inspect system state
- **Read & write files** — view or create files on disk
- **Do math** — evaluate mathematical expressions
- **Search the web** — query DuckDuckGo for information
- **Get current time** — UTC datetime

The agent autonomously decides when to use tools, chains multiple tool calls, and returns a final answer.

## Setup

### 1. Prerequisites

- Python 3.10+
- An Azure AI Foundry resource with Claude Opus 4.5 deployed ([Azure AI Model Catalog](https://ai.azure.com/explore/models))

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your Azure AI endpoint and API key
```

| Variable | Description |
|----------|-------------|
| `AZURE_AI_ENDPOINT` | Your Azure AI Foundry model endpoint URL |
| `AZURE_AI_API_KEY` | API key for authentication |
| `AZURE_AI_MODEL` | Model name (default: `claude-opus-4-5-20250219`) |

### 4. Run the agent

```bash
python agent.py
```

## Architecture

```
agent.py    — Main agent loop + CLI interface
tools.py    — Tool registry, definitions, and implementations
.env        — Your Azure credentials (not committed)
```

### How the agentic loop works

1. User sends a message
2. Message history + tool definitions sent to Claude Opus 4.5 via Azure AI Inference API
3. If Claude returns `tool_calls` → execute each tool, append results to history
4. Repeat step 2-3 until Claude returns a final text response (max 15 turns)
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

## Web API

The Vibe Oracle is also available as a REST API via FastAPI.

### Start the Server
```bash
python api.py
# Or: uvicorn api:app --reload
```

### API Endpoints
- `GET /` — Welcome message and endpoint list
- `GET /vibe?query=your-question` — Get a single vibe reading
- `GET /vibes?count=5` — Get multiple vibe readings (1-20)
- `GET /health` — Health check
- `GET /docs` — Interactive API documentation (Swagger UI)
