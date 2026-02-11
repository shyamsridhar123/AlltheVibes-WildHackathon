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
| **Local-first architecture** | Refactored `config.py` to use Ollama by default. Azure/OpenAI are optional. Updated DadJokes/KnockKnock to use unified config. | 2026-02-10 |
| **Pin dependencies** | Pinned all versions in `requirements.txt` with exact versions. Added Pydantic. | 2026-02-10 |
| **Audit logging** | Added structured JSON audit logging in `tools.py`. Logs all tool calls, results, errors, and user confirmations. | 2026-02-10 |
| **Input validation (Pydantic)** | Added Pydantic models for all tool inputs. Blocks malicious patterns before execution. | 2026-02-10 |
| **Authentication layer** | Added optional API key auth via `REQUIRE_AUTH` + `AGENT_API_KEY`. Defaults to off for CLI usage. | 2026-02-10 |

---

## In Progress

*Nothing currently in progress.*

---

## Backlog (Prioritized)

### Medium Priority (P3)

- [ ] **Add rate limiting** — No rate limiting on any agents
- [ ] **Add agent-to-agent communication** — Currently siloed

### Low Priority (P4)

- [ ] **Add structured error handling** — Some bare except blocks
- [ ] **Add test suite** — No automated tests exist

---

## Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| Use Beth orchestrator | Coordinated multi-agent workflows | — |
| AST parser over eval() | Defense in depth — only allow math, reject everything else | 2026-02-10 |
| Command allowlist over blocklist | Blocklists are trivially bypassed; allowlists fail-safe | 2026-02-10 |
| Workspace-bounded file ops | Prevent reads/writes outside project directory | 2026-02-10 |
| User confirmation for dangerous tools | Human-in-the-loop for shell commands and file writes | 2026-02-10 |
| Local-first with Ollama | No cloud dependency required. Azure/OpenAI optional for enterprise. | 2026-02-10 |
| Pydantic for input validation | Strong typing + validation at boundaries. Graceful fallback if not installed. | 2026-02-10 |
| Optional auth for CLI | CLI users are implicitly authenticated. API key auth available for service exposure. | 2026-02-10 |

---

## Status Summary

**For Leadership:**

All CRITICAL and HIGH vulnerabilities addressed. System is now local-first with Ollama, with optional cloud backends.

**What's Working:**

- Beth agent (orchestrator) — Ready
- Full agent roster — Ready
- All skills — Loaded
- Security-hardened tool execution — `tools.py`, `agent.py`
- Local-first LLM — Ollama default, Azure/OpenAI optional
- Audit logging — All tool executions logged
- Input validation — Pydantic models for all tools
- Optional authentication — API key auth for service exposure

**Blockers:** None. Ready for review and merge.

---

## How We Track Work

| Tool | Audience | Purpose |
|------|----------|---------|
| beads (`bd`) | Agents | Active work, dependencies, blockers, structured memory |
| Backlog.md | Humans | Completed work archive, decisions, readable changelog |

**The rule:** beads is always current. Backlog.md gets updated when work completes.

---

*"Now you know what's happening. Questions? I'll answer them. Complaints? Keep them to yourself."*
