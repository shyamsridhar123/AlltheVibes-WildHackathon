"""
🐝 Agent Swarm Communication System

Enables agent-to-agent communication with:
- Agent registry with capabilities
- Message protocol for inter-agent messaging
- Task delegation and response handling
- Conversation history tracking

Usage:
    from agents.swarm import Swarm, Message

    swarm = Swarm()
    
    # Send a message to a specific agent
    response = swarm.send("sql_generator", Message(
        from_agent="router",
        content="Generate SQL for: show top 5 customers",
        task_type="sql_generation"
    ))
    
    # Broadcast to all agents that can handle a task type
    responses = swarm.broadcast(Message(
        from_agent="orchestrator",
        content="Review this code for issues",
        task_type="code_review"
    ))
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

from config import chat


# ---------------------------------------------------------------------------
# Message Protocol
# ---------------------------------------------------------------------------


class MessageStatus(Enum):
    """Status of a message in the swarm."""
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(Enum):
    """Types of tasks that can be delegated between agents."""
    CODE_REVIEW = "code_review"
    SQL_GENERATION = "sql_generation"
    README_GENERATION = "readme_generation"
    GIT_ANALYSIS = "git_analysis"
    VISUALIZATION = "visualization"
    INTENT_CLASSIFICATION = "intent_classification"
    GENERAL = "general"


@dataclass
class Message:
    """
    Inter-agent message protocol.
    
    Attributes:
        from_agent: Name of the sending agent
        content: The message content/request
        task_type: Type of task being requested
        context: Additional context data (e.g., file paths, conversation history)
        priority: 1 (highest) to 5 (lowest)
        reply_to: Message ID this is a reply to (for threading)
    """
    from_agent: str
    content: str
    task_type: str = "general"
    context: dict[str, Any] = field(default_factory=dict)
    priority: int = 3
    reply_to: str | None = None
    
    # Auto-generated fields
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: MessageStatus = MessageStatus.PENDING
    
    def to_dict(self) -> dict:
        """Serialize message to dictionary."""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "content": self.content,
            "task_type": self.task_type,
            "context": self.context,
            "priority": self.priority,
            "reply_to": self.reply_to,
            "timestamp": self.timestamp,
            "status": self.status.value,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Deserialize message from dictionary."""
        msg = cls(
            from_agent=data["from_agent"],
            content=data["content"],
            task_type=data.get("task_type", "general"),
            context=data.get("context", {}),
            priority=data.get("priority", 3),
            reply_to=data.get("reply_to"),
        )
        msg.id = data.get("id", msg.id)
        msg.timestamp = data.get("timestamp", msg.timestamp)
        if "status" in data:
            msg.status = MessageStatus(data["status"])
        return msg


@dataclass
class Response:
    """Response from an agent to a message."""
    agent: str
    content: str
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Auto-generated
    message_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "content": self.content,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Agent Definition
# ---------------------------------------------------------------------------


@dataclass
class AgentCapability:
    """Defines an agent's capabilities for the swarm."""
    name: str
    description: str
    task_types: list[str]
    handler: Callable[[Message], Response]
    system_prompt: str = "You are a helpful AI agent."
    
    def can_handle(self, task_type: str) -> bool:
        """Check if this agent can handle a task type."""
        return task_type in self.task_types or "general" in self.task_types


# ---------------------------------------------------------------------------
# Agent Swarm
# ---------------------------------------------------------------------------


class Swarm:
    """
    Central swarm coordinator for agent-to-agent communication.
    
    Manages:
    - Agent registry
    - Message routing
    - Task delegation
    - Conversation history
    """
    
    def __init__(self):
        self._agents: dict[str, AgentCapability] = {}
        self._message_history: list[Message] = []
        self._response_history: list[Response] = []
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register the built-in CLI toolkit agents."""
        
        # SQL Generator
        self.register(AgentCapability(
            name="sql_generator",
            description="Generates SQL from natural language queries",
            task_types=["sql_generation", "database"],
            handler=self._sql_handler,
            system_prompt="You are an expert SQL agent that generates clear, well-documented SQL queries.",
        ))
        
        # Code Reviewer
        self.register(AgentCapability(
            name="code_reviewer",
            description="Reviews code for bugs, style, and improvements",
            task_types=["code_review", "analysis"],
            handler=self._code_review_handler,
            system_prompt="You are an expert code reviewer. Identify bugs, style issues, and suggest improvements.",
        ))
        
        # Repo Copilot
        self.register(AgentCapability(
            name="repo_copilot",
            description="Analyzes repository structure and generates documentation",
            task_types=["readme_generation", "documentation"],
            handler=self._readme_handler,
            system_prompt="You are a documentation expert. Analyze codebases and generate clear README files.",
        ))
        
        # Commit Whisperer
        self.register(AgentCapability(
            name="commit_whisperer",
            description="Narrates and analyzes git commit history",
            task_types=["git_analysis", "history"],
            handler=self._git_handler,
            system_prompt="You are a dramatic narrator of git history. Bring the commit log to life.",
        ))
        
        # Chaos Visualizer
        self.register(AgentCapability(
            name="chaos_visualizer",
            description="Visualizes git statistics and contributor activity",
            task_types=["visualization", "git_analysis"],
            handler=self._viz_handler,
            system_prompt="You analyze git repositories and present statistics in an engaging way.",
        ))
        
        # Intent Router
        self.register(AgentCapability(
            name="router",
            description="Classifies user intent and routes to appropriate agents",
            task_types=["intent_classification", "routing"],
            handler=self._router_handler,
            system_prompt="You are an intent classifier. Route requests to the most appropriate agent.",
        ))
        
        # Orchestrator (meta-agent)
        self.register(AgentCapability(
            name="orchestrator",
            description="Coordinates multi-agent workflows and complex tasks",
            task_types=["general", "coordination", "planning"],
            handler=self._orchestrator_handler,
            system_prompt="You are the swarm orchestrator. Coordinate agents to complete complex tasks.",
        ))
    
    # -----------------------------------------------------------------------
    # Registry
    # -----------------------------------------------------------------------
    
    def register(self, agent: AgentCapability) -> None:
        """Register an agent with the swarm."""
        self._agents[agent.name] = agent
    
    def unregister(self, name: str) -> bool:
        """Remove an agent from the swarm."""
        if name in self._agents:
            del self._agents[name]
            return True
        return False
    
    def get_agent(self, name: str) -> AgentCapability | None:
        """Get an agent by name."""
        return self._agents.get(name)
    
    def list_agents(self) -> list[dict]:
        """List all registered agents with their capabilities."""
        return [
            {
                "name": a.name,
                "description": a.description,
                "task_types": a.task_types,
            }
            for a in self._agents.values()
        ]
    
    def find_agents_for_task(self, task_type: str) -> list[str]:
        """Find agents that can handle a specific task type."""
        return [
            name for name, agent in self._agents.items()
            if agent.can_handle(task_type)
        ]
    
    # -----------------------------------------------------------------------
    # Messaging
    # -----------------------------------------------------------------------
    
    def send(self, to_agent: str, message: Message) -> Response:
        """
        Send a message to a specific agent.
        
        Args:
            to_agent: Name of the target agent
            message: The message to send
            
        Returns:
            Response from the agent
        """
        # Record message
        message.status = MessageStatus.DELIVERED
        self._message_history.append(message)
        
        # Find the agent
        agent = self._agents.get(to_agent)
        if not agent:
            response = Response(
                agent="swarm",
                content="",
                success=False,
                error=f"Agent '{to_agent}' not found. Available: {list(self._agents.keys())}",
                message_id=message.id,
            )
            self._response_history.append(response)
            return response
        
        # Process message
        message.status = MessageStatus.PROCESSING
        try:
            response = agent.handler(message)
            response.message_id = message.id
            message.status = MessageStatus.COMPLETED
        except Exception as e:
            response = Response(
                agent=to_agent,
                content="",
                success=False,
                error=str(e),
                message_id=message.id,
            )
            message.status = MessageStatus.FAILED
        
        self._response_history.append(response)
        return response
    
    def broadcast(self, message: Message, task_type: str | None = None) -> list[Response]:
        """
        Broadcast a message to all agents that can handle the task type.
        
        Args:
            message: The message to broadcast
            task_type: Filter by task type (uses message.task_type if None)
            
        Returns:
            List of responses from all matching agents
        """
        task = task_type or message.task_type
        agents = self.find_agents_for_task(task)
        
        responses = []
        for agent_name in agents:
            # Don't send to self
            if agent_name == message.from_agent:
                continue
            response = self.send(agent_name, message)
            responses.append(response)
        
        return responses
    
    def delegate(self, from_agent: str, to_agent: str, task: str, context: dict | None = None) -> Response:
        """
        Convenience method for one agent to delegate a task to another.
        
        Args:
            from_agent: The delegating agent
            to_agent: The target agent
            task: Description of the task
            context: Additional context
            
        Returns:
            Response from the target agent
        """
        message = Message(
            from_agent=from_agent,
            content=task,
            task_type="general",
            context=context or {},
        )
        return self.send(to_agent, message)
    
    # -----------------------------------------------------------------------
    # History
    # -----------------------------------------------------------------------
    
    def get_history(self, limit: int = 50) -> list[dict]:
        """Get recent message history."""
        return [m.to_dict() for m in self._message_history[-limit:]]
    
    def get_conversation(self, message_id: str) -> list[dict]:
        """Get a conversation thread by message ID."""
        # Find the root message
        root = None
        for msg in self._message_history:
            if msg.id == message_id:
                root = msg
                break
        
        if not root:
            return []
        
        # Find all replies
        thread = [root.to_dict()]
        for msg in self._message_history:
            if msg.reply_to == message_id:
                thread.append(msg.to_dict())
        
        return thread
    
    # -----------------------------------------------------------------------
    # Default Handlers
    # -----------------------------------------------------------------------
    
    def _sql_handler(self, message: Message) -> Response:
        """Handle SQL generation requests."""
        schema = message.context.get("schema", """
            Tables:
            - users (id, name, email, created_at, role)
            - orders (id, user_id, product_id, amount, status, created_at)
            - products (id, name, category, price, stock)
        """)
        
        prompt = f"""Generate SQL for this request:

{message.content}

Database Schema:
{schema}

Return ONLY the SQL query, no explanation."""

        result = chat(prompt, system="You are an expert SQL generator.", temperature=0.2)
        
        return Response(
            agent="sql_generator",
            content=result,
            success=True,
            metadata={"task_type": "sql_generation"},
        )
    
    def _code_review_handler(self, message: Message) -> Response:
        """Handle code review requests."""
        code = message.context.get("code", message.content)
        
        prompt = f"""Review this code:

```
{code}
```

Identify:
1. Bugs or errors
2. Style issues
3. Performance improvements
4. Security concerns

Be concise and actionable."""

        result = chat(prompt, system="You are an expert code reviewer.", temperature=0.3)
        
        return Response(
            agent="code_reviewer",
            content=result,
            success=True,
            metadata={"task_type": "code_review"},
        )
    
    def _readme_handler(self, message: Message) -> Response:
        """Handle README generation requests."""
        files = message.context.get("files", [])
        structure = message.context.get("structure", "")
        
        prompt = f"""Generate a README for this project:

Structure:
{structure}

Key files:
{json.dumps(files, indent=2)}

Request: {message.content}

Generate a clear, well-structured README."""

        result = chat(prompt, system="You are a documentation expert.", temperature=0.4)
        
        return Response(
            agent="repo_copilot",
            content=result,
            success=True,
            metadata={"task_type": "readme_generation"},
        )
    
    def _git_handler(self, message: Message) -> Response:
        """Handle git analysis requests."""
        commits = message.context.get("commits", [])
        
        prompt = f"""Narrate this git history dramatically:

Commits:
{json.dumps(commits, indent=2) if commits else message.content}

Bring the commit log to life with drama and humor."""

        result = chat(prompt, system="You are a dramatic narrator of git history.", temperature=0.7)
        
        return Response(
            agent="commit_whisperer",
            content=result,
            success=True,
            metadata={"task_type": "git_analysis"},
        )
    
    def _viz_handler(self, message: Message) -> Response:
        """Handle visualization requests."""
        stats = message.context.get("stats", {})
        
        prompt = f"""Analyze and present these git statistics:

Stats:
{json.dumps(stats, indent=2) if stats else message.content}

Present the analysis in an engaging, visual way using ASCII/Unicode."""

        result = chat(prompt, system="You present data visually and engagingly.", temperature=0.5)
        
        return Response(
            agent="chaos_visualizer",
            content=result,
            success=True,
            metadata={"task_type": "visualization"},
        )
    
    def _router_handler(self, message: Message) -> Response:
        """Handle intent classification requests."""
        agents_info = "\n".join(
            f"- {a['name']}: {a['description']}"
            for a in self.list_agents()
        )
        
        prompt = f"""Classify this user request and pick the best agent:

Available agents:
{agents_info}

User request: "{message.content}"

Respond in this format:
agent: <agent_name>
confidence: <high|medium|low>
reasoning: <one sentence>"""

        result = chat(prompt, system="You are an intent classifier.", temperature=0.2)
        
        # Parse result
        parsed = {}
        for line in result.strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                parsed[key.strip().lower()] = val.strip()
        
        return Response(
            agent="router",
            content=result,
            success=True,
            metadata={
                "task_type": "intent_classification",
                "classified_agent": parsed.get("agent"),
                "confidence": parsed.get("confidence"),
            },
        )
    
    def _orchestrator_handler(self, message: Message) -> Response:
        """Handle orchestration requests by delegating to other agents."""
        # First, classify the intent
        router_response = self.send("router", Message(
            from_agent="orchestrator",
            content=message.content,
            task_type="intent_classification",
        ))
        
        target_agent = router_response.metadata.get("classified_agent")
        
        if target_agent and target_agent in self._agents and target_agent != "orchestrator":
            # Delegate to the identified agent
            delegated = self.send(target_agent, Message(
                from_agent="orchestrator",
                content=message.content,
                task_type=message.task_type,
                context=message.context,
                reply_to=message.id,
            ))
            
            return Response(
                agent="orchestrator",
                content=f"Delegated to {target_agent}:\n\n{delegated.content}",
                success=delegated.success,
                metadata={
                    "delegated_to": target_agent,
                    "original_response": delegated.to_dict(),
                },
            )
        
        # Fallback: handle directly
        prompt = f"""Handle this request:

{message.content}

Context: {json.dumps(message.context) if message.context else 'None'}

Provide a helpful response."""

        result = chat(prompt, system="You are a helpful AI coordinator.", temperature=0.5)
        
        return Response(
            agent="orchestrator",
            content=result,
            success=True,
        )


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------

_swarm: Swarm | None = None


def get_swarm() -> Swarm:
    """Get the global swarm instance."""
    global _swarm
    if _swarm is None:
        _swarm = Swarm()
    return _swarm


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------


def run():
    """Interactive swarm communication demo."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    
    console = Console()
    swarm = get_swarm()
    
    console.print(Panel(
        "🐝 [bold cyan]Agent Swarm[/] — Inter-agent communication demo\n\n"
        "Commands:\n"
        "  [green]list[/]              — Show all agents\n"
        "  [green]send <agent> <msg>[/] — Send message to agent\n"
        "  [green]broadcast <msg>[/]   — Broadcast to all agents\n"
        "  [green]ask <msg>[/]         — Let orchestrator route it\n"
        "  [green]history[/]           — Show message history\n"
        "  [green]quit[/]              — Exit",
        title="🐝 Swarm",
        border_style="cyan",
    ))
    
    while True:
        try:
            user_input = console.input("\n[bold green]swarm → [/]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n👋 Swarm disbanded.")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ("quit", "exit", "q"):
            console.print("👋 Swarm disbanded.")
            break
        
        if user_input.lower() == "list":
            table = Table(title="🐝 Registered Agents")
            table.add_column("Agent", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Task Types", style="green")
            
            for agent in swarm.list_agents():
                table.add_row(
                    agent["name"],
                    agent["description"],
                    ", ".join(agent["task_types"]),
                )
            console.print(table)
            continue
        
        if user_input.lower() == "history":
            history = swarm.get_history(10)
            if not history:
                console.print("[dim]No messages yet.[/dim]")
            else:
                for msg in history:
                    console.print(f"[dim]{msg['timestamp'][:19]}[/dim] "
                                f"[cyan]{msg['from_agent']}[/cyan] → "
                                f"[yellow]{msg['task_type']}[/yellow]: "
                                f"{msg['content'][:60]}...")
            continue
        
        # Parse commands
        parts = user_input.split(maxsplit=2)
        cmd = parts[0].lower()
        
        if cmd == "send" and len(parts) >= 3:
            target = parts[1]
            content = parts[2]
            
            response = swarm.send(target, Message(
                from_agent="user",
                content=content,
            ))
            
            if response.success:
                console.print(Panel(
                    Markdown(response.content),
                    title=f"🤖 {response.agent}",
                    border_style="green",
                ))
            else:
                console.print(f"[red]Error:[/red] {response.error}")
        
        elif cmd == "broadcast" and len(parts) >= 2:
            content = " ".join(parts[1:])
            responses = swarm.broadcast(Message(
                from_agent="user",
                content=content,
            ))
            
            for resp in responses:
                if resp.success:
                    console.print(Panel(
                        resp.content[:500] + ("..." if len(resp.content) > 500 else ""),
                        title=f"🤖 {resp.agent}",
                        border_style="green",
                    ))
        
        elif cmd == "ask" and len(parts) >= 2:
            content = " ".join(parts[1:])
            response = swarm.send("orchestrator", Message(
                from_agent="user",
                content=content,
            ))
            
            if response.success:
                console.print(Panel(
                    Markdown(response.content),
                    title="🤖 Orchestrator",
                    border_style="cyan",
                ))
            else:
                console.print(f"[red]Error:[/red] {response.error}")
        
        else:
            # Default: send to orchestrator
            response = swarm.send("orchestrator", Message(
                from_agent="user",
                content=user_input,
            ))
            
            if response.success:
                console.print(Panel(
                    Markdown(response.content),
                    title="🤖 Orchestrator",
                    border_style="cyan",
                ))


if __name__ == "__main__":
    run()
