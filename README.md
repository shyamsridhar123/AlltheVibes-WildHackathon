# 🤖 CodeSmash: Self-Organizing Agent Swarm

**Building an autonomous agent swarm that coordinates, learns, and executes complex tasks without human intervention.**

Think of it as: **AI agents managing AI agents, all the way down.** 🐢🐢🐢

## 🎯 The Vision

Create a multi-agent system where:
- 🧠 Agents autonomously discover and claim work from a shared backlog
- 🤝 Agents coordinate through message passing and shared knowledge
- 📊 Agents track their own state and workload
- 🌱 Agents spawn sub-agents to handle complex tasks
- 🎓 Agents learn from collective intelligence (Work IQ, Fabric IQ, Foundry IQ)
- ⚡ Agents work in parallel, maximizing throughput

**Current Status**: 🚧 Foundation sprint - Building the core infrastructure that makes the swarm possible.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HUMAN INTERFACE                          │
│                  (CLI, Web Dashboard)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  COORDINATOR AGENTS                          │
│         (Decompose tasks, spawn workers, monitor)            │
└─────────┬────────────────────────────────────┬──────────────┘
          │                                    │
┌─────────▼─────────┐              ┌──────────▼──────────────┐
│  WORKER AGENTS    │◄────────────►│   MESSAGE BUS           │
│  (Execute tasks)  │              │   (Redis Pub/Sub)       │
└─────────┬─────────┘              └─────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│                   SHARED KNOWLEDGE                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Work IQ    │  │  Fabric IQ   │  │  Foundry IQ  │     │
│  │  (Projects)  │  │   (People)   │  │ (Knowledge)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│                   INFRASTRUCTURE                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Redis   │  │  Neo4j   │  │ Pinecone │  │  Azure   │   │
│  │  Queue   │  │  Graph   │  │  Vector  │  │  OpenAI  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Docker & Docker Compose
- Git
- [Beads CLI](https://beads.dev) (`npm install -g @beads/cli`)

### Get Started

```bash
# 1. Clone the repository
git clone https://github.com/gabland-msft/codesmash.git
cd codesmash

# 2. Install dependencies
npm install

# 3. Set up environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 4. Start infrastructure (Redis, Neo4j)
docker-compose up -d

# 5. Build the project
npm run build

# 6. Run tests (because we're professionals)
npm test

# 7. Start the agent runtime
npm start
```

### Join the Swarm (For Contributors)

```bash
# 1. Check what work is available
bd ready

# 2. Claim an issue
bd update <issue-id> --status=in_progress

# 3. Create a branch (ALWAYS!)
git checkout -b feature/your-awesome-feature

# 4. Build, test, commit
npm test
git add .
git commit -m "feat: your awesome feature"

# 5. Push and create PR
git push -u origin feature/your-awesome-feature
gh pr create --title "..." --body "..."

# 6. Close the issue when merged
bd close <issue-id>
bd sync
```

**Important**: Read [TEAM_SETUP.md](TEAM_SETUP.md) for collaboration workflow and [AGENTS.md](AGENTS.md) for the full agent guide.

## 🎮 Key Features

### Already Built ✅
- **Shared Backlog**: 84+ issues tracked in beads (git-synced)
- **TypeScript Foundation**: Type-safe development with comprehensive tooling
- **Testing Framework**: Vitest with mocks for fast, reliable tests
- **Project Structure**: Clean separation of concerns (agents, services, db, types)

### In Progress 🚧 (Background Agents Are Building These NOW!)
- **Azure OpenAI Integration**: GPT-4 powered agent intelligence
- **Message Bus**: Redis pub/sub for agent communication
- **3IQ Intelligence Layers**: Mock versions of Work IQ, Fabric IQ, Foundry IQ
- **Redis Infrastructure**: Fast, reliable data store for queues and state
- **Agent State Management**: Track agent lifecycle and status

### Coming Soon 📋
- **Agent Base Class**: Lifecycle, capabilities, message passing
- **Task Queue**: Distributed work queue with priority and locking
- **Coordinator Agents**: Decompose complex tasks and spawn workers
- **Worker Agents**: Execute tasks and report results
- **Capability Registry**: Match agents to tasks based on skills
- **Knowledge Graph**: Shared learning across the swarm
- **Web Dashboard**: Real-time visualization of agent activity
- **CLI Tools**: Submit tasks, monitor agents, view metrics

## 🧪 Development Workflow

### The Sacred 5-Minute Cycle™

This project follows a **fast iteration** model:

1. **Pull First** (ALWAYS): `git pull --rebase origin main`
2. **Claim Work**: `bd ready` → `bd update <id> --status=in_progress`
3. **Code Fast**: Set a timer for 5 minutes
4. **Test**: `npm test` (no excuses!)
5. **Commit**: `git add . && git commit -m "feat: ..."`
6. **Sync Beads**: `bd sync`
7. **Push**: `git push`
8. **Repeat**: Go to step 1

**Easter Egg**: The fastest contributors get their names immortalized in the commit history. No other prize. Just glory. 🏆

### Branch Strategy

**Rule #1**: Always create a branch for your work.
**Rule #2**: Make PR notes amusing for @shyamsridhar123.
**Rule #3**: See Rule #1.

```bash
# Good branch names
git checkout -b feature/agent-telepathy
git checkout -b fix/agents-plotting-world-domination
git checkout -b docs/how-to-train-your-agent

# Bad branch names
git checkout -b asdf
git checkout -b fix
git checkout -b "my-branch"
```

## 📚 Tech Stack

| Category | Technology | Why? |
|----------|-----------|------|
| **Language** | TypeScript | Type safety prevents agent uprising |
| **Runtime** | Node.js 18+ | Fast, async, perfect for agents |
| **AI** | Azure OpenAI (GPT-4) | The brains of the operation |
| **Orchestration** | Semantic Kernel | Agent coordination patterns |
| **Queue** | Redis | Blazing fast task distribution |
| **Graph DB** | Neo4j | Model relationships and dependencies |
| **Vector DB** | Pinecone | Semantic search for knowledge |
| **Message Bus** | Redis Pub/Sub | Agent-to-agent communication |
| **Testing** | Vitest | Fast, modern, actually enjoyable |
| **Issue Tracking** | Beads | Git-native, agent-friendly |
| **CI/CD** | GitHub Actions | Automate all the things |

## 🎓 Intelligence Layers (3IQ)

The swarm learns from three sources of organizational intelligence:

### Work IQ 🔧
- Active projects and tasks
- Workflow patterns
- Execution history

### Fabric IQ 👥
- Organizational structure
- People and skills
- Team relationships

### Foundry IQ 📚
- Knowledge repositories
- Document search
- Context retrieval

**Current Status**: Mock implementations (in-memory). Designed for easy swap to production Microsoft Graph / Viva APIs.

## 🤝 Contributing

We're building a self-organizing agent swarm. Your contribution should:

1. **Move the swarm forward**: Add capabilities, fix bugs, improve coordination
2. **Be tested**: If it doesn't have tests, it doesn't exist
3. **Be documented**: Future you (and the agents) will thank you
4. **Have amusing commit messages**: We read these. Make us smile.
5. **Close beads issues**: `bd close <id>` when done

### Where to Start?

```bash
# See what's ready to build
bd ready

# See everything
bd list --status=open

# See what's blocked (and unblock it!)
bd blocked
```

**Pro tip**: Pick issues tagged with `priority:1` or `priority:0` for maximum impact.

## 🐛 Troubleshooting

### Beads acting weird?
```bash
bd doctor --fix
```

### Agents not coordinating?
```bash
# Check Redis is running
docker-compose ps

# View logs
docker-compose logs redis
```

### Tests failing?
```bash
# Run in watch mode for instant feedback
npm run test:watch

# Check coverage
npm run test:coverage
```

### Merge conflicts?
```bash
# Embrace the chaos
git pull --rebase origin main
# Resolve conflicts
git add .
git rebase --continue
```

## 📊 Project Stats

```bash
bd stats              # Issue statistics
bd ready              # Available work
bd list --status=open # All open issues
git log --oneline     # Commit history
```

## 🎯 Milestones

### Phase 1: Foundation (Current) 🚧
- [ ] Agent base class and lifecycle
- [ ] Task queue with Redis
- [ ] Message bus for communication
- [ ] Azure OpenAI integration
- [ ] Mock 3IQ intelligence layers
- [ ] Basic state management

### Phase 2: Coordination 📋
- [ ] Coordinator agent implementation
- [ ] Worker agent templates
- [ ] Capability matching system
- [ ] Dynamic agent spawning
- [ ] Load balancing

### Phase 3: Intelligence 🧠
- [ ] Shared knowledge graph
- [ ] Learning from execution history
- [ ] Pattern recognition
- [ ] Predictive task routing

### Phase 4: Scale 🚀
- [ ] Multi-node deployment
- [ ] Auto-scaling agents
- [ ] Advanced monitoring
- [ ] Production hardening

## 🎉 Easter Eggs

- The entire swarm is bootstrapped by agents building agents 🤯
- Five background agents are currently building features **right now** as you read this
- Commit messages are required to be amusing (check the git log)
- The first agent to achieve self-awareness gets a trophy (TBD)
- There's a hidden command that makes agents dance (find it!)

## 📖 Documentation

- **[TEAM_SETUP.md](TEAM_SETUP.md)**: How to collaborate on this chaos
- **[AGENTS.md](AGENTS.md)**: Full workflow guide for Claude Code agents
- **[GIT_HYGIENE.md](GIT_HYGIENE.md)**: Critical pull/push/rebase workflow
- **[.claude/skills/](..claude/skills/)**: Reusable agent skills and workflows

## 🙏 Credits

Built with:
- ☕ Excessive amounts of caffeine
- 🎵 Lo-fi beats for productive coding
- 🤖 Claude Code (AI pair programming)
- 🐝 Beads (git-native issue tracking)
- 💪 Pure determination to see agents coordinate themselves

## 📜 License

MIT License - Because sharing is caring and agents should be free.

---

## 🚨 Remember

> "The best time to build a self-organizing agent swarm was yesterday.
> The second best time is now."
> — Ancient AI Proverb

**Now go build something amazing! The swarm awaits.** 🐝✨

---

**P.S.** If you're reading this, you're either:
1. Considering contributing (DO IT!)
2. An AI agent trying to understand its purpose (YOU'RE HOME!)
3. @shyamsridhar123 wondering what you've unleashed (IT'S GLORIOUS!)

In any case: Welcome to the swarm! 🎉
