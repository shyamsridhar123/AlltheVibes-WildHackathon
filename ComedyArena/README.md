# 🏟️ Comedy Arena — Joke Judge Showdown

A multi-agent AI system where two joke agents battle and an AI Judge scores them using the **LLM-as-a-Judge** evaluation pattern.

## How It Works

```
User Prompt ──► 🚪 Knock Knock Agent ──► Joke A ──┐
                                                    ├──► ⚖️ Judge Agent ──► Scores + Verdict
User Prompt ──► 👨 Dad Joke Agent    ──► Joke B ──┘
```

1. You give a topic or question
2. **Knock Knock Agent** 🚪 responds with a knock-knock joke
3. **Dad Joke Agent** 👨 responds with a dad joke
4. **Judge Agent** ⚖️ evaluates both using a structured rubric and returns:
   - Scores (creativity, pun quality, relevance, funny factor)
   - A roast for each contestant
   - A dramatic verdict
5. Running **leaderboard** tracks wins across rounds

## Technical Concepts

| Concept | How It's Used |
|---|---|
| **Multi-Agent Orchestration** | Three independent agents coordinated in a pipeline |
| **LLM-as-a-Judge** | A language model evaluates other LLM outputs using a scoring rubric |
| **Structured Output** | Judge returns valid JSON for programmatic scoreboard rendering |
| **Evaluation Rubric** | Creativity, pun quality, relevance, and funny factor (1-10 each) |
| **Stateful Leaderboard** | Tracks wins/ties across rounds within a session |

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your OpenAI API key**:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and replace `sk-your-key-here` with your real key.

4. **Run the arena**:
   ```bash
   python comedy_arena.py
   ```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use for all three agents |

## Example

```
🎤 You: Why is the sky blue?

🔔 ROUND 1 — FIGHT!
-------------------------------------------------------

🚪 Knock Knock Agent:
Knock knock!
(Who's there?)
Ray.
(Ray who?)
Rayleigh scattering makes short blue wavelengths bounce around the sky — let me in, it's getting scattered out here!

👨 Dad Joke Agent:
👨 Dad says: My kid asked me why the sky is blue...
... I said "Because if it were green, we wouldn't know where to stop mowing." *finger guns* 😎👉👉

⚖️  The Judge is deliberating...

=======================================================
📊  S C O R E B O A R D
=======================================================
Category          🚪 Knock Knock     👨 Dad Joke
-------------------------------------------------------
Creativity                  7               8
Pun Quality                 6               9
Relevance                   8               6
Funny Factor                7               9
-------------------------------------------------------
TOTAL                      28              32
=======================================================

🔥 Roast for 🚪: "Scientific accuracy won't save you from that punchline."
🔥 Roast for 👨: "Peak dad energy. The finger guns sealed it."

🏆 WINNER: 👨 Dad Joke Agent
🎭 "In a clash of wavelengths and lawnmowers, the dad joke cuts the competition down to size."
```

## Architecture

The arena demonstrates key AI evaluation patterns:

- **Agent Independence**: Each joke agent has its own system prompt and generates independently
- **Blind Evaluation**: The Judge doesn't know which agent is "supposed" to win
- **Structured Scoring**: JSON output enables programmatic rendering and tracking
- **Session State**: Leaderboard persists across rounds for running competition

## License

MIT
