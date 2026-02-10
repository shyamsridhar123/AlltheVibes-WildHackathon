"""
🗄️ Mini SQL Generator — natural language to SQL.
Shows agent thinking, assumptions, and explainability.
"""

from config import chat


SAMPLE_SCHEMA = """
Tables:
  - users (id, name, email, created_at, role)
  - orders (id, user_id, product_id, amount, status, created_at)
  - products (id, name, category, price, stock)
  - reviews (id, user_id, product_id, rating, comment, created_at)
"""


def generate_sql(user_request: str, schema: str = SAMPLE_SCHEMA) -> str:
    """Generate SQL from natural language with explanations."""

    prompt = f"""You are an expert SQL agent. Given the user's request and database schema,
generate SQL and explain your reasoning.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

### 🧠 Understanding
(What the user is asking for, in plain English)

### 🤔 Assumptions
(List any assumptions you made about ambiguous terms)

### 📝 Generated SQL
```sql
(your SQL here)
```

### 📊 Expected Output
(Describe what the result would look like)

### ⚠️ Caveats
(Any gotchas, missing info, or things the user should know)

### 🔄 Alternative Interpretation
(If the request is ambiguous, show an alternative SQL)

DATABASE SCHEMA:
{schema}

USER REQUEST: "{user_request}"
"""

    system = """You are a thoughtful SQL agent that prioritizes explainability.
You show your reasoning, flag assumptions, and handle ambiguity gracefully.
This is for a hackathon demo — be impressive but honest."""

    return chat(prompt, system=system, temperature=0.3)


def run(user_request: str = None):
    """Run the SQL Generator interactively."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()
    console.print("\n🗄️ [bold green]Mini SQL Generator[/] — Natural language → SQL\n")

    if not user_request:
        console.print("Example queries:")
        console.print("  • Show me the top 5 customers by total spend")
        console.print("  • Find products with no reviews")
        console.print("  • Monthly revenue trend for the last year\n")
        user_request = console.input("[bold green]Your query → [/]")

    result = generate_sql(user_request)
    console.print(Panel(Markdown(result), title="🗄️ SQL Agent Output", border_style="green"))
    return result


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    run(query)
