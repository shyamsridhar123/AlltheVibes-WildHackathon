# 👨 Dad Joke Agent

An AI agent that responds to **everything** with dad jokes! Puns, wordplay, and maximum groan factor guaranteed.

## Setup

1. **Clone the repo** and `cd` into it.

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your OpenAI API key**:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and replace `sk-your-key-here` with your real key.

5. **Run the agent**:
   ```bash
   python dad_joke_agent.py
   ```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use for responses |

Set these in your `.env` file.

## Example

```
You: What's the best way to learn programming?

👨 Dad:
👨 Dad says: I told my son he should learn Python...
... He said "But Dad, I'm scared of snakes!" I said, "Don't worry,
it's the only snake that won't byte!" 🐍 *slaps knee*

👨 Dad says: Why do programmers prefer dark mode?
... Because light attracts bugs! Get it? 😎👉👉
```

## Combo Mode 🤝

Pair this agent with the **Knock Knock Joke Agent** for an unstoppable
comedy duo! The Knock Knock Agent sets 'em up, Dad knocks 'em down
with puns.

## License

MIT
