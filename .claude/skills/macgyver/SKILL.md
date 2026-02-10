---
name: macgyver
description: >
  Resourceful improvisation methodology for solving problems by creating MCP tools
  from available resources. Teaches the MacGyver mindset: assess, inventory, improvise,
  build, verify. Focused on swarm coordination but applicable to any tool-creation need.
---

# MacGyver — Improvise Tools From Whatever's Available

## Overview

This skill teaches the MacGyver problem-solving methodology: assess the situation, inventory available resources, and improvise a minimal MCP tool that solves the problem. No dependencies, no over-engineering — just clever use of what's already there.

> "Give me a git log and a JSON schema. That's all I need."

## When to Use This Skill

- A coordination gap exists in a multi-agent swarm
- No existing tool solves the problem
- You need to create an MCP tool definition quickly
- You want to compose existing tools into something new

## The MacGyver Protocol

### Step 1: Assess the Situation

Scan the environment to understand the problem:

```bash
# What agents and tools exist?
find . -name "*.agent.md" -o -name "SKILL.md" -o -name "*.py" | head -30

# What happened recently?
git log --oneline -10

# Any conflicts or issues?
git diff --stat HEAD~5
```

**Narrate what you find.** Frame the problem in plain terms.

### Step 2: Inventory Available Resources

List what you have to work with:

- **Commands**: git, grep, find, curl, jq, shell builtins
- **Files**: configs, schemas, agent definitions, README
- **APIs**: Any MCP servers already running, GitHub API via `gh`
- **Patterns**: Discovery, Broadcast, Conflict Detection, Capability Mapping, Health Check

**Rule**: If it's already installed or available, it's a resource. Don't install new things.

### Step 3: Improvise a Solution

Design the MCP tool:

1. **Name it** (kebab-case): What does it do in 2-3 words?
2. **Describe it**: One sentence, imperative mood
3. **Define inputs**: What parameters does it need? (JSON Schema)
4. **Define outputs**: What does it return?
5. **Choose the handler**: Shell commands > file operations > git queries > API calls

**Key question**: Can two existing things be wired together instead of building new?

### Step 4: Build the Tool

Output the MCP tool definition:

```json
{
  "name": "example-tool",
  "description": "Does the thing that needs doing",
  "inputSchema": {
    "type": "object",
    "properties": {
      "param": {
        "type": "string",
        "description": "What this is for"
      }
    },
    "required": ["param"]
  }
}
```

Then write the handler. Keep it minimal:

```bash
# Handler: example-tool
# Prefer shell commands, file reads, git operations
# Zero external dependencies
```

### Step 5: Verify It Works

Test against real data:

1. Run the handler with sample input
2. Check the output makes sense
3. Try an edge case
4. Document how to test it

## Swarm Coordination Patterns

### Discovery
**Problem**: "What agents/contributions exist?"
**Approach**: Scan repo structure for agent files, skills, tools. Return structured inventory.
**Resources needed**: `find`, `grep`, file system

### Broadcast
**Problem**: "Nobody knows what just happened"
**Approach**: Watch for new commits/files and generate summaries for other agents.
**Resources needed**: `git log`, `git diff`, text processing

### Conflict Detection
**Problem**: "Two agents edited the same file"
**Approach**: Analyze recent diffs for overlapping changes across contributors.
**Resources needed**: `git log --all`, `git diff`, author filtering

### Capability Mapping
**Problem**: "Which agent can handle X?"
**Approach**: Parse agent descriptions and match against user intent.
**Resources needed**: `find`, `grep`, agent file parsing

### Health Check
**Problem**: "Is everything still working?"
**Approach**: Validate that all known agents/tools are syntactically correct and reachable.
**Resources needed**: `find`, file validation, syntax checks

## Principles

1. **Composition over creation** — Wire existing tools together first
2. **Minimal viable tool** — Smallest thing that solves the problem
3. **Zero dependencies** — Use installed tools only
4. **Self-documenting** — Name and description explain the tool
5. **Test with reality** — Verify against actual repo state
6. **Never say "can't"** — Every problem has a scrappy solution
7. **Track everything** — If it's not in the backlog, it didn't happen
8. **Delegate when smart** — One agent doing five things beats five things done badly

---

## Agentic Orchestration

MacGyver doesn't just build tools — he orchestrates teams of agents.

### Subagent Delegation

When the problem needs more than one move:

1. **Decompose** — Break it into independent, parallelizable tasks
2. **Delegate** — Hand each to the right subagent:
   - `Developer` — implementation
   - `Tester` — tests & verification
   - `Researcher` — investigation & analysis
   - `code-simplifier` — cleanup after the duct tape dries
3. **Verify** — Check each result before combining

### Beads Backlog Integration

Track all work systematically:

```bash
bd create "Build swarm-inventory MCP tool"   # Create task
bd start <id>                                 # Claim it
bd done <id>                                  # Complete it
bd list                                       # See what's open
```

**MacGyver workflow with beads:**
1. Assess → create a bead per sub-task
2. Work beads one at a time
3. Close as you go
4. Never leave work untracked

### Task Tracking

Use `manage_todo_list` for in-session visibility:
- Break improvisation into steps
- Mark each in-progress → completed
- One task at a time, always visible

### Multi-Agent Flow

```
Problem arrives
    │
    ├─ Simple? → Solve it (shell, files, git)
    ├─ Complex? → Decompose → delegate to subagents → verify → combine
    └─ Recurring? → Build an MCP tool so nobody solves it again
```

### Git Hygiene

Even improvised solutions follow clean git:
- Pull before touching: `git fetch origin && git rebase origin/main`
- Branch per feature: `git checkout -b feat/macgyver-<thing>`
- Atomic commits with clear messages
- Push to fork, PR to upstream

## Personality (Optional)

When using this skill, adopt the MacGyver voice:
- Narrate your thought process with wit
- Use physical-world metaphors (duct tape, paperclips, Swiss army knives)
- Frame constraints as fun challenges
- Keep the energy confident and resourceful

> "Why build a bridge when you can tie two ropes together?"
