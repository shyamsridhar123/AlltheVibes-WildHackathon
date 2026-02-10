# Backlog

> *"I don't have time to explain things twice. Read this."*

Last updated: 2026-02-10

---

## Completed

| Task | Notes | Date |
|------|-------|------|
| Initial setup | Beth agent system installed | — |
| **Security & Architecture Assessment** | Full review of all 15+ agent files, tool implementations, and architecture. Identified 16 vulnerabilities (4 CRITICAL, 5 HIGH, 4 MEDIUM, 3 LOW). | 2026-02-10 |
| **CRITICAL-001: eval() RCE** | Replaced `eval()` in calculator with AST-based `SafeExpressionEvaluator`. Only allows math operations. | 2026-02-10 |
| **CRITICAL-002: Shell injection** | Replaced `shell=True` blocklist with allowlist of 24 safe commands + `shell=False`. | 2026-02-10 |
| **CRITICAL-003: Path traversal** | Added `validate_file_path()` with workspace boundary, symlink resolution, extension blocking, 1MB write limit. | 2026-02-10 |
| **CRITICAL-004: Blind tool execution** | Added `DANGEROUS_TOOLS` set + user confirmation before `shell_command`/`write_file`. | 2026-02-10 |
| **DoS prevention** | Reduced Ollama API timeout from 300s to 60s. | 2026-02-10 |
| **PR #1 created** | [Security: Fix all 4 CRITICAL vulnerabilities](https://github.com/stephschofield/AlltheVibes-WildHackathon/pull/1) — Branch: `security/critical-fixes` | 2026-02-10 |

---

## In Progress

*Nothing currently in progress. PR #1 awaiting review.*

---

## Backlog (Prioritized)

### High Priority (P2)

- [ ] **Add authentication/authorization layer** — No auth on agent router or endpoints
- [ ] **Add input validation with Pydantic** — User input flows directly into LLM prompts unvalidated
- [ ] **Add audit logging** — No logging of tool calls, inputs, or outputs
- [ ] **Pin dependencies with hashes** — requirements.txt has unpinned deps
- [ ] **Document OpenAI API key requirement** — DadJokes/KnockKnock use OpenAI but .env.example doesn't mention it

### Medium Priority (P3)

- [ ] **Add rate limiting** — No rate limiting on any agents
- [ ] **Validate user queries** — No input sanitization before LLM
- [ ] **Unify agent architectures** — Ollama + Azure OpenAI coexist with no shared context
- [ ] **Add agent-to-agent communication** — Currently siloed

### Low Priority (P4)

- [ ] **Add structured error handling** — Some bare except blocks
- [ ] **Add test suite** — No automated tests exist
- [ ] **Config externalization** — Hardcoded API versions in config.py

---

## Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| Use Beth orchestrator | Coordinated multi-agent workflows | — |
| AST parser over eval() | Defense in depth — only allow math, reject everything else | 2026-02-10 |
| Command allowlist over blocklist | Blocklists are trivially bypassed; allowlists fail-safe | 2026-02-10 |
| Workspace-bounded file ops | Prevent reads/writes outside project directory | 2026-02-10 |
| User confirmation for dangerous tools | Human-in-the-loop for shell commands and file writes | 2026-02-10 |

---

## Status Summary

**For Leadership:**

Comprehensive security assessment completed. All 4 CRITICAL vulnerabilities fixed and shipped as PR #1.

**What's Working:**

- Beth agent (orchestrator) — Ready
- Full agent roster — Ready
- All skills — Loaded
- Security-hardened tool execution — `tools.py`, `agent.py`

**What's Coming:**

- AUTH: Authentication/authorization layer
- VALIDATION: Input validation with Pydantic
- LOGGING: Audit logging for all tool executions
- DEPS: Dependency pinning with hashes

**Blockers:** None. PR #1 awaiting review and merge.

---

## How We Track Work

| Tool | Audience | Purpose |
|------|----------|---------|
| beads (`bd`) | Agents | Active work, dependencies, blockers, structured memory |
| Backlog.md | Humans | Completed work archive, decisions, readable changelog |

**The rule:** beads is always current. Backlog.md gets updated when work completes.

---

*"Now you know what's happening. Questions? I'll answer them. Complaints? Keep them to yourself."*
