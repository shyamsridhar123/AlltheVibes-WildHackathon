# Agent Instructions

This project uses a **dual tracking system**:

| Tool | Audience | Purpose |
|------|----------|---------|
| [beads](https://github.com/steveyegge/beads) (`bd`) | Agents | Active work, dependencies, blockers, structured memory |
| [Backlog.md](Backlog.md) | Humans | Completed work archive, decisions, readable changelog |

**The rule:** beads is always current. Backlog.md gets updated when work completes.

## Quick Setup

```bash
# Install beads
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash

# Initialize in your project
bd init

# Run doctor to verify setup
bd doctor
```

## Quick Reference

```bash
# Simple task
bd create "Issue title" --description="What needs to be done" -l in_progress

# Epic for complex work
bd create "Feature name" --type epic -p 1

# Subtask with parent
bd create "Subtask" --parent <epic-id>

# Task with dependency
bd create "Blocked task" --deps "<blocker-id>"

# List issues / see what's ready
bd list
bd ready

# View dependencies
bd dep tree <id>

# Close an issue
bd close <id>
```

## Workflow

### Simple Tasks
1. `bd create "Task" -l in_progress`
2. Do the work
3. `bd close <id>`
4. Update Backlog.md if significant
5. Commit and push

### Complex Work (Multi-Agent)
1. `bd create "Feature" --type epic -p 1`
2. Break into subtasks with `--parent` and `--deps`
3. `bd ready` to find unblocked work
4. Route to specialists with issue IDs
5. Close subtasks as they complete
6. `bd epic close-eligible` when all children done
7. Update Backlog.md with summary
8. Commit and push

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **Close beads issues** - `bd close <id>` for completed work
2. **Create follow-up issues** - `bd create` for any remaining work
3. **Update Backlog.md** - Add summary to Completed section for significant work
4. **Run quality gates** (if code changed) - Tests, linters, builds
5. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git add -A
   git commit -m "description of work"
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
